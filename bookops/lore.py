from __future__ import annotations

import hashlib
import re
from pathlib import Path
from typing import Any

from .agents import AgentResult
from .config import RuntimeConfig, load_rules
from .ingest import load_chapters, load_lore
from .utils import dump_json, load_json, utc_now_iso
from .vcs import changed_paths_since


_LORE_FILE_RE = re.compile(r"(?:lore[/\\])?([a-zA-Z0-9_-]+)\.md", re.IGNORECASE)


def agent_proposals_to_lore_proposals(
    agent_results: list[AgentResult],
    scope: str,
    lore_docs: list[Any],
    config: RuntimeConfig,
) -> list[dict[str, Any]]:
    """Convert agent proposals (kind=lore_update) to lore proposal format.

    Agent proposals with kind 'lore_update' are converted to the standard
    lore proposal shape for the approve/sync path. Target lore file is
    inferred from content when possible, else the first lore file is used.
    """
    proposals: list[dict[str, Any]] = []
    chapter_id: int | None = None
    if scope.startswith("chapter:"):
        try:
            chapter_id = int(scope.split(":")[1])
        except (IndexError, ValueError):
            pass

    if not lore_docs:
        return []
    lore_paths = [str(d.path.relative_to(config.project_root)) for d in lore_docs]
    lore_names = {d.name.lower(): str(d.path.relative_to(config.project_root)) for d in lore_docs}
    default_target = lore_paths[0]

    for result in agent_results:
        for idx, p in enumerate(result.proposals):
            if p.get("kind") != "lore_update":
                continue
            content = p.get("content", "")
            target = default_target
            match = _LORE_FILE_RE.search(content)
            if match:
                name = match.group(1).lower()
                for lore_name, path in lore_names.items():
                    if lore_name == name or name in lore_name:
                        target = path
                        break

            proposal_id = f"agent-{result.name}-{idx}-{hashlib.sha256(content.encode()).hexdigest()[:8]}"
            proposals.append(
                {
                    "id": proposal_id,
                    "chapter": chapter_id,
                    "target_lore_file": target,
                    "reason": content,
                    "evidence": [],
                    "status": "pending_review",
                    "source_agent": result.name,
                }
            )

    return proposals


def select_chapters_for_lore_delta(
    chapters: list[Any],
    chapter_id: int | None = None,
    changed_chapter_paths: set[str] | None = None,
    project_root: Path | None = None,
) -> list[Any]:
    selected = [c for c in chapters if chapter_id is None or c.chapter_number == chapter_id]
    if changed_chapter_paths is not None and project_root is not None:
        selected = [
            c
            for c in selected
            if str(c.path.relative_to(project_root)) in changed_chapter_paths
        ]
    return selected


def generate_lore_delta(
    config: RuntimeConfig,
    chapter_id: int | None = None,
    since_ref: str | None = None,
    agent_results: list[AgentResult] | None = None,
) -> dict[str, Any]:
    chapters = load_chapters(config.chapters_dir)
    lore_docs = load_lore(config.lore_dir)
    changed_chapters: set[str] | None = None
    if since_ref:
        changed = changed_paths_since(config.project_root, since_ref)
        changed_chapters = {p for p in changed if p.startswith("chapters/")}

    selected = select_chapters_for_lore_delta(
        chapters,
        chapter_id=chapter_id,
        changed_chapter_paths=changed_chapters,
        project_root=config.project_root,
    )
    if chapter_id is not None and not selected:
        raise ValueError(f"Chapter {chapter_id} not found")

    lore_names = {doc.name.lower(): doc for doc in lore_docs}
    proposals: list[dict[str, Any]] = []

    for chapter in selected:
        chapter_text = chapter.text.lower()
        for name, lore_doc in lore_names.items():
            token = name.split()[0]
            if token and token in chapter_text:
                proposals.append(
                    {
                        "id": f"proposal-{chapter.chapter_number}-{name.replace(' ', '-')}",
                        "chapter": chapter.chapter_number,
                        "target_lore_file": str(lore_doc.path.relative_to(config.project_root)),
                        "reason": f"Character/entity '{name}' appears in chapter text; review lore alignment.",
                        "evidence": [
                            {
                                "file": str(chapter.path.relative_to(config.project_root)),
                                "line_hint": 1,
                                "excerpt": chapter.lines[0] if chapter.lines else "",
                            }
                        ],
                        "status": "pending_review",
                    }
                )

    if agent_results:
        scope = f"chapter:{chapter_id}" if chapter_id is not None else "project"
        agent_proposals = agent_proposals_to_lore_proposals(
            agent_results, scope, lore_docs, config
        )
        proposals.extend(agent_proposals)

    payload = {
        "generated_at": utc_now_iso(),
        "scope": f"chapter:{chapter_id}" if chapter_id is not None else "project",
        "since_ref": since_ref,
        "chapter_count_evaluated": len(selected),
        "proposals": proposals,
    }
    dump_json(config.bookops_dir / "lore-proposals.json", payload)
    return payload


def apply_lore_proposal(config: RuntimeConfig, proposal_id: str) -> dict[str, Any]:
    rules = load_rules(config.rules_path)
    precedence = rules.get("policy", {}).get("precedence", {}).get("manuscript_over_lore", True)
    proposals_store = load_json(config.bookops_dir / "lore-proposals.json", default={}) or {}
    proposals = proposals_store.get("proposals", [])
    proposal = next((p for p in proposals if p.get("id") == proposal_id), None)
    if not proposal:
        raise ValueError(f"Proposal {proposal_id} not found")
    if proposal.get("status") != "approved":
        raise ValueError(f"Proposal {proposal_id} must be approved before apply (current status: {proposal.get('status')}).")

    if not precedence:
        raise ValueError("Cannot apply lore proposal because manuscript-over-lore precedence is disabled.")

    target_lore_file = proposal["target_lore_file"]
    if Path(target_lore_file).is_absolute():
        raise ValueError(f"Proposal target_lore_file must be a relative path: {target_lore_file!r}")
    target = (config.project_root / target_lore_file).resolve()
    try:
        target.relative_to(config.project_root.resolve())
    except ValueError:
        raise ValueError(f"Proposal target_lore_file escapes project root: {target_lore_file!r}")
    if not target.exists():
        raise ValueError(f"Lore file not found: {target_lore_file}")

    content = target.read_text(encoding="utf-8")
    stamp = f"\n\n<!-- BookOps sync: {utc_now_iso()} proposal={proposal_id} -->\n"
    target.write_text(content + stamp, encoding="utf-8")

    proposal["status"] = "applied"
    proposals_store["proposals"] = proposals
    dump_json(config.bookops_dir / "lore-proposals.json", proposals_store)
    return proposal


def approve_lore_proposal(config: RuntimeConfig, proposal_id: str, reviewer: str, note: str = "") -> dict[str, Any]:
    proposals_store = load_json(config.bookops_dir / "lore-proposals.json", default={}) or {}
    proposals = proposals_store.get("proposals", [])
    proposal = next((p for p in proposals if p.get("id") == proposal_id), None)
    if not proposal:
        raise ValueError(f"Proposal {proposal_id} not found")
    if proposal.get("status") == "applied":
        raise ValueError(f"Proposal {proposal_id} already applied.")

    proposal["status"] = "approved"
    proposal["approved_by"] = reviewer
    proposal["approved_at"] = utc_now_iso()
    if note:
        proposal["approval_note"] = note

    proposals_store["proposals"] = proposals
    dump_json(config.bookops_dir / "lore-proposals.json", proposals_store)
    return proposal
