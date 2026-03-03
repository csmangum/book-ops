"""Build context pack for model-backed agents.

Provides chapter excerpts, canon slices, open issues, and rule snippets
per the agent contract.
"""

from __future__ import annotations

from pathlib import Path
from typing import Any

from .canon import build_canon, load_snapshot
from .config import RuntimeConfig, load_rules
from .ingest import load_chapters
from .issues import filter_issues, load_issue_store


MAX_CHAPTER_EXCERPT_CHARS = 12_000


def build_context_pack(
    config: RuntimeConfig,
    scope: str,
    scope_id: int | None = None,
) -> dict[str, Any]:
    """Build context pack for agent execution.

    Args:
        config: Runtime configuration.
        scope: "chapter" or "project".
        scope_id: Chapter ID when scope is chapter.

    Returns:
        Dict with chapter_excerpts, canon_slices, open_issues, rule_snippets.
    """
    pack: dict[str, Any] = {
        "chapter_excerpts": [],
        "canon_slices": {},
        "open_issues": [],
        "rule_snippets": [],
    }

    chapters = load_chapters(config.chapters_dir)
    canon = load_snapshot(config.canon_latest) if config.canon_latest.exists() else build_canon(config)
    rules = load_rules(config.rules_path)
    store = load_issue_store(config.issues_file)

    if scope == "chapter" and scope_id is not None:
        chapter_doc = next((c for c in chapters if c.chapter_number == scope_id), None)
        if chapter_doc:
            excerpt = chapter_doc.text
            if len(excerpt) > MAX_CHAPTER_EXCERPT_CHARS:
                excerpt = excerpt[:MAX_CHAPTER_EXCERPT_CHARS] + "\n\n[... truncated ...]"
            pack["chapter_excerpts"] = [
                {
                    "chapter_id": scope_id,
                    "path": str(chapter_doc.path.relative_to(config.project_root)),
                    "title": chapter_doc.title,
                    "text": excerpt,
                }
            ]
        timeline = canon.get("timeline", {})
        chapter_days = timeline.get("chapter_days", {})
        pack["canon_slices"] = {
            "chapter_days": {k: v for k, v in chapter_days.items() if int(k) <= scope_id},
            "dates": [d for d in timeline.get("dates", []) if d.get("chapter", 0) <= scope_id],
            "times": [t for t in timeline.get("times", []) if t.get("chapter", 0) <= scope_id],
            "entities": canon.get("entities", [])[:50],
        }
        scope_filter = f"chapter:{scope_id}"
    else:
        for c in chapters[:10]:
            excerpt = c.text
            if len(excerpt) > 4000:
                excerpt = excerpt[:4000] + "\n\n[... truncated ...]"
            pack["chapter_excerpts"].append(
                {
                    "chapter_id": c.chapter_number,
                    "path": str(c.path.relative_to(config.project_root)),
                    "title": c.title,
                    "text": excerpt,
                }
            )
        pack["canon_slices"] = {
            "chapter_days": canon.get("timeline", {}).get("chapter_days", {}),
            "dates": canon.get("timeline", {}).get("dates", [])[:30],
            "times": canon.get("timeline", {}).get("times", [])[:30],
            "entities": canon.get("entities", [])[:50],
        }
        scope_filter = "project"

    open_issues = filter_issues(
        store,
        status=None,
        severity=None,
        scope=scope_filter,
    )
    pack["open_issues"] = [
        {
            "id": i.get("id"),
            "rule_id": i.get("rule_id"),
            "severity": i.get("severity"),
            "message": i.get("message", "")[:200],
        }
        for i in open_issues
        if i.get("status") in ("open", "in_progress")
    ][:20]

    rules_list = rules.get("rules", [])
    scope_rules = [r for r in rules_list if r.get("scope") in (scope, "chapter", "project")]
    pack["rule_snippets"] = [
        {
            "id": r.get("id"),
            "message": r.get("message"),
            "severity": r.get("severity"),
            "scope": r.get("scope"),
        }
        for r in scope_rules[:15]
    ]

    return pack
