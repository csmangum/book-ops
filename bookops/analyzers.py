from __future__ import annotations

import re
from collections import Counter
from difflib import SequenceMatcher
from pathlib import Path
from typing import Any

from .config import RuntimeConfig, load_rules
from .ingest import ChapterDoc, extract_dialogue_lines, extract_time_markers, load_chapters, load_lore
from .models import Evidence, Finding


DAY_RE = re.compile(r"\bDay\s+(\d+)\b", re.IGNORECASE)
PAST_VERB_RE = re.compile(r"\b(was|were|had|did|said|asked|walked|looked|felt|kept)\b", re.IGNORECASE)
PRESENT_VERB_RE = re.compile(r"\b(is|are|has|do|says|asks|walks|looks|feels|keeps)\b", re.IGNORECASE)


def check_timeline_day_sequence(chapters: list[ChapterDoc]) -> list[Finding]:
    findings: list[Finding] = []
    seen: list[tuple[int, int, int, str]] = []  # chapter_num, line, day, path
    path_map: dict[int, str] = {}
    for chapter in chapters:
        path_map[chapter.chapter_number] = str(chapter.path)
        markers = extract_time_markers(chapter.lines)
        for line_no, marker in markers["day"]:
            m = DAY_RE.search(marker)
            if not m:
                continue
            seen.append((chapter.chapter_number, line_no, int(m.group(1)), str(chapter.path)))

    seen_sorted = sorted(seen, key=lambda t: t[0])
    last_day: int | None = None
    for chapter_num, line_no, day, chapter_path in seen_sorted:
        if last_day is not None and day < last_day:
            findings.append(
                Finding(
                    rule_id="HARD.TIMELINE.DAY_SEQUENCE",
                    title="Day sequence regression",
                    severity="high",
                    message=f"Chapter {chapter_num} references Day {day} after Day {last_day}.",
                    scope=f"chapter:{chapter_num}",
                    evidence=[
                        Evidence(
                            file=chapter_path,
                            line_start=line_no,
                            line_end=line_no,
                            excerpt=f"Day marker: Day {day}",
                        )
                    ],
                )
            )
        last_day = max(last_day or day, day)
    return findings


def check_tense_consistency(chapter: ChapterDoc, max_violations: int = 2) -> list[Finding]:
    findings: list[Finding] = []
    violations = []
    for idx, line in enumerate(chapter.lines, start=1):
        present = len(PRESENT_VERB_RE.findall(line))
        past = len(PAST_VERB_RE.findall(line))
        if present > past + 2 and len(line.strip()) > 20:
            violations.append((idx, line.strip()))
    if len(violations) > max_violations:
        evidence = [
            Evidence(
                file=str(chapter.path),
                line_start=line_no,
                line_end=line_no,
                excerpt=excerpt,
            )
            for line_no, excerpt in violations[:5]
        ]
        findings.append(
            Finding(
                rule_id="HARD.TENSE.CONSISTENCY",
                title="Tense drift",
                severity="high",
                message=f"Detected {len(violations)} potential present-tense drifts in a past-tense chapter.",
                scope=f"chapter:{chapter.chapter_number}",
                evidence=evidence,
            )
        )
    return findings


def check_character_invariants(chapter: ChapterDoc) -> list[Finding]:
    findings: list[Finding] = []
    forbidden_patterns = [
        (r"\bHarry\b.*\b(screen|tablet|app|browser|login|wifi|AI assistant)\b", "Harry appears to use digital technology."),
        (r"\bHarry\b.*\b(googled|texted|emailed)\b", "Harry appears to use disallowed digital behaviors."),
    ]
    for pattern, message in forbidden_patterns:
        regex = re.compile(pattern, re.IGNORECASE)
        for idx, line in enumerate(chapter.lines, start=1):
            if regex.search(line):
                findings.append(
                    Finding(
                        rule_id="HARD.CHARACTER.INVARIANTS",
                        title="Character invariant violation",
                        severity="critical",
                        message=message,
                        scope=f"chapter:{chapter.chapter_number}",
                        evidence=[
                            Evidence(
                                file=str(chapter.path),
                                line_start=idx,
                                line_end=idx,
                                excerpt=line.strip(),
                            )
                        ],
                    )
                )
    return findings


def check_phrase_family_density(chapter: ChapterDoc, warn_threshold: int = 6) -> list[Finding]:
    patterns = {
        "not_yet": re.compile(r"\bnot yet\b", re.IGNORECASE),
        "the_way_construction": re.compile(r"\bthe way\b", re.IGNORECASE),
        "warm_warmth": re.compile(r"\bwarm(?:th)?\b", re.IGNORECASE),
    }
    counts = {name: len(regex.findall(chapter.text)) for name, regex in patterns.items()}
    findings: list[Finding] = []
    for name, count in counts.items():
        if count >= warn_threshold:
            findings.append(
                Finding(
                    rule_id="SOFT.REPETITION.PHRASE_FAMILY",
                    title=f"Phrase family density: {name}",
                    severity="medium",
                    message=f"Phrase family '{name}' appears {count} times (threshold {warn_threshold}).",
                    scope=f"chapter:{chapter.chapter_number}",
                    metadata={"count": count, "family": name},
                )
            )
    return findings


def check_motif_density(chapter: ChapterDoc, motif_thresholds: dict[str, int] | None = None) -> list[Finding]:
    if motif_thresholds is None:
        motif_thresholds = {"copper": 8, "chrome": 8, "orchids": 7}
    findings: list[Finding] = []
    text_lower = chapter.text.lower()
    for motif_key, threshold in motif_thresholds.items():
        # Use singular form for search when the motif key is plural (ends in "s"), so
        # text_lower.count() captures both singular and plural occurrences via substring matching.
        search_term = motif_key[:-1] if motif_key.endswith("s") and len(motif_key) > 1 else motif_key
        count = text_lower.count(search_term)
        if count >= threshold:
            findings.append(
                Finding(
                    rule_id="SOFT.MOTIF.DENSITY_BALANCE",
                    title=f"Motif density high: {motif_key}",
                    severity="medium",
                    message=f"Motif '{motif_key}' appears {count} times (threshold {threshold}).",
                    scope=f"chapter:{chapter.chapter_number}",
                    metadata={"motif": motif_key, "search_term": search_term, "count": count},
                )
            )
    return findings


def check_near_verbatim_project(chapters: list[ChapterDoc], similarity_threshold: float = 0.9, min_tokens: int = 10) -> list[Finding]:
    findings: list[Finding] = []
    normalized_lines: list[tuple[int, int, str, str, str]] = []
    for chapter in chapters:
        for idx, line in enumerate(chapter.lines, start=1):
            stripped = line.strip()
            if len(stripped.split()) < min_tokens:
                continue
            normalized = re.sub(r"\s+", " ", stripped.lower())
            normalized_lines.append((chapter.chapter_number, idx, stripped, normalized, str(chapter.path)))

    # Candidate reduction for performance:
    # compare only lines with the same 3-token prefix signature.
    buckets: dict[str, list[tuple[int, int, str, str, str]]] = {}
    for item in normalized_lines:
        _c, _l, _raw, norm, _path = item
        tokens = norm.split()
        signature = " ".join(tokens[:3]) if len(tokens) >= 3 else norm
        buckets.setdefault(signature, []).append(item)

    for bucket_items in buckets.values():
        if len(bucket_items) < 2:
            continue
        for i in range(len(bucket_items)):
            c1, l1, raw1, n1, p1 = bucket_items[i]
            for j in range(i + 1, min(i + 30, len(bucket_items))):
                c2, l2, raw2, n2, p2 = bucket_items[j]
                if c1 == c2:
                    continue
                sim = SequenceMatcher(None, n1, n2).ratio()
                if sim >= similarity_threshold:
                    findings.append(
                        Finding(
                            rule_id="SOFT.REPETITION.NEAR_VERBATIM",
                            title="Near-verbatim repetition",
                            severity="high",
                            message=f"Lines in chapters {c1} and {c2} are highly similar ({sim:.2f}).",
                            scope="project",
                            evidence=[
                                Evidence(file=p1, line_start=l1, line_end=l1, excerpt=raw1),
                                Evidence(file=p2, line_start=l2, line_end=l2, excerpt=raw2),
                            ],
                            metadata={"similarity": round(sim, 4)},
                        )
                    )
                    if len(findings) >= 50:
                        return findings
    return findings


def check_dialogue_voice_drift(chapter: ChapterDoc) -> list[Finding]:
    dialogue = extract_dialogue_lines(chapter.lines)
    findings: list[Finding] = []
    if len(dialogue) < 8:
        return findings
    tokens = Counter()
    for line in dialogue:
        for token in re.findall(r"[A-Za-z']+", line.lower()):
            tokens[token] += 1
    high_modal = tokens["like"] + tokens["kind"] + tokens["just"]
    if high_modal / max(sum(tokens.values()), 1) > 0.08:
        findings.append(
            Finding(
                rule_id="SOFT.DIALOGUE.VOICE_DRIFT",
                title="Possible dialogue voice drift",
                severity="medium",
                message="Dialogue may be drifting toward generic modal-heavy phrasing.",
                scope=f"chapter:{chapter.chapter_number}",
                metadata={"modal_ratio": round(high_modal / max(sum(tokens.values()), 1), 4)},
            )
        )
    return findings


def check_lore_conflicts(chapters: list[ChapterDoc], lore_docs: list[Any]) -> list[Finding]:
    findings: list[Finding] = []
    lore_text = "\n".join(doc.text.lower() for doc in lore_docs)
    # Guardrail for office location continuity style issue.
    if "office is in the bradbury building" in lore_text:
        for chapter in chapters:
            for idx, line in enumerate(chapter.lines, start=1):
                if "office" in line.lower() and "laundromat" in line.lower():
                    findings.append(
                        Finding(
                            rule_id="HARD.PRECEDENCE.STORY_OVER_LORE",
                            title="Potential lore/manuscript conflict",
                            severity="critical",
                            message="Chapter text appears to conflict with established lore for office location.",
                            scope=f"chapter:{chapter.chapter_number}",
                            evidence=[
                                Evidence(
                                    file=str(chapter.path),
                                    line_start=idx,
                                    line_end=idx,
                                    excerpt=line.strip(),
                                )
                            ],
                        )
                    )
    return findings


def run_chapter_analysis(
    config: RuntimeConfig,
    chapter_id: int,
    checks: set[str] | None = None,
) -> dict[str, Any]:
    checks = checks or {"tense", "invariants", "repetition", "motifs", "voice"}
    rules = load_rules(config.rules_path)
    chapters = load_chapters(config.chapters_dir)
    target = next((c for c in chapters if c.chapter_number == chapter_id), None)
    if not target:
        raise ValueError(f"Chapter {chapter_id} not found")

    findings: list[Finding] = []
    tense_rule = next((r for r in rules["rules"] if r["id"] == "HARD.TENSE.CONSISTENCY"), None)
    max_violations = tense_rule.get("params", {}).get("max_violations", 2) if tense_rule else 2
    soft_phrase_rule = next((r for r in rules["rules"] if r["id"] == "SOFT.REPETITION.PHRASE_FAMILY"), None)
    warn_threshold = soft_phrase_rule.get("params", {}).get("warn_threshold", 6) if soft_phrase_rule else 6

    if "tense" in checks:
        findings.extend(check_tense_consistency(target, max_violations=max_violations))
    if "invariants" in checks:
        findings.extend(check_character_invariants(target))
    if "repetition" in checks:
        findings.extend(check_phrase_family_density(target, warn_threshold=warn_threshold))
    if "motifs" in checks:
        motif_rule = next((r for r in rules["rules"] if r["id"] == "SOFT.MOTIF.DENSITY_BALANCE"), None)
        motif_thresholds: dict[str, int] | None = None
        if motif_rule:
            raw_motifs = motif_rule.get("params", {}).get("motifs", {})
            if raw_motifs:
                motif_thresholds = {k: v.get("warn_per_chapter", 8) for k, v in raw_motifs.items() if isinstance(v, dict)}
        findings.extend(check_motif_density(target, motif_thresholds=motif_thresholds))
    if "voice" in checks:
        findings.extend(check_dialogue_voice_drift(target))

    payload = {
        "scope": f"chapter:{chapter_id}",
        "checks": sorted(checks),
        "generated_findings": [f.to_dict() for f in findings],
    }
    return payload


def run_project_analysis(config: RuntimeConfig, chapter_filter_paths: set[str] | None = None) -> dict[str, Any]:
    chapters = load_chapters(config.chapters_dir)
    if chapter_filter_paths:
        filtered: list[ChapterDoc] = []
        for chapter in chapters:
            rel = str(chapter.path.relative_to(config.project_root))
            if rel in chapter_filter_paths:
                filtered.append(chapter)
        chapters = filtered
    lore_docs = load_lore(config.lore_dir)
    findings: list[Finding] = []
    findings.extend(check_timeline_day_sequence(chapters))
    findings.extend(check_near_verbatim_project(chapters))
    findings.extend(check_lore_conflicts(chapters, lore_docs))
    motif_metrics = []
    for chapter in chapters:
        text_lower = chapter.text.lower()
        motif_metrics.append(
            {
                "chapter": chapter.chapter_number,
                "path": str(chapter.path),
                "copper": text_lower.count("copper"),
                "chrome": text_lower.count("chrome"),
                "orchids": text_lower.count("orchids"),
            }
        )
    day_markers = []
    for chapter in chapters:
        markers = extract_time_markers(chapter.lines)
        day_values = [m[1] for m in markers["day"]]
        day_markers.append(
            {
                "chapter": chapter.chapter_number,
                "path": str(chapter.path),
                "day_markers": day_values,
                "date_markers": [m[1] for m in markers["date"]],
            }
        )
    return {
        "scope": "project",
        "generated_findings": [f.to_dict() for f in findings],
        "metrics": {
            "motifs": motif_metrics,
            "timeline_markers": day_markers,
        },
    }
