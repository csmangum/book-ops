"""
CLI for multi-level semantic book indexing.

Usage:
    python -m indexer setup              Download NLTK data (punkt) if needed
    python -m indexer build              Build/rebuild the index
    python -m indexer search "query"     Search at paragraph level (default)
    python -m indexer search "query" -l sentence -n 20
    python -m indexer search "query" -l scene --act "Act I – The Hire"
    python -m indexer search "query" -l chapter --chapter 7
    python -m indexer drill "query"      Hierarchical: chapters -> paragraphs
    python -m indexer stats              Show index statistics
"""

from __future__ import annotations

import argparse
import sys

from rich.console import Console
from rich.table import Table
from rich.panel import Panel
from rich import box

console = Console()

LEVELS = ["sentence", "paragraph", "scene", "chapter", "act"]


def _ensure_index(idx) -> bool:
    """Return True if index has data. Print message and return False if empty."""
    if sum(idx.stats().values()) == 0:
        console.print("[red]Index is empty. Run 'python -m indexer build' first.[/red]")
        return False
    return True


def cmd_setup(args: argparse.Namespace) -> None:
    """Download NLTK punkt tokenizer data required for sentence splitting."""
    import nltk
    with console.status("[bold green]Downloading NLTK punkt tokenizer..."):
        nltk.download("punkt")
    console.print("[green]NLTK data ready. You can run 'python -m indexer build'.[/green]")


def cmd_build(args: argparse.Namespace) -> None:
    from .embedder import BookIndex

    with console.status("[bold green]Loading model and building index..."):
        idx = BookIndex()
        counts = idx.build(force=args.force)

    table = Table(title="Index Built", box=box.ROUNDED)
    table.add_column("Level", style="cyan")
    table.add_column("Units", style="green", justify="right")
    for level in LEVELS:
        table.add_row(level, str(counts.get(level, 0)))
    console.print(table)


def cmd_search(args: argparse.Namespace) -> None:
    from .embedder import BookIndex

    idx = BookIndex()
    if not _ensure_index(idx):
        return

    where = {}
    if args.act:
        where["act"] = args.act
    if args.chapter is not None:
        where["chapter_num"] = args.chapter

    results = idx.query(
        args.query,
        level=args.level,
        n_results=args.n,
        where=where or None,
    )

    if not results:
        console.print("[yellow]No results found.[/yellow]")
        return

    console.print(f"\n[bold]Search: [cyan]{args.query}[/cyan] @ {args.level} level[/bold]\n")

    for i, r in enumerate(results, 1):
        meta = r["metadata"]
        score = 1 - r["distance"]  # cosine distance -> similarity

        header = (
            f"[{i}] Ch {meta['chapter_num']}: {meta['chapter_title']} "
            f"| {meta['act']} | scene {meta['scene_idx']}"
        )
        if args.level in ("paragraph", "sentence"):
            header += f" | para {meta['paragraph_idx']}"
        if args.level == "sentence":
            header += f" | sent {meta['sentence_idx']}"
        header += f"  [dim](sim: {score:.3f})[/dim]"

        text_display = r["text"]
        if len(text_display) > 500 and args.level not in ("sentence",):
            text_display = text_display[:500] + "..."

        console.print(Panel(
            text_display,
            title=header,
            title_align="left",
            border_style="blue" if score > 0.5 else "dim",
            width=min(console.width, 120),
        ))


def cmd_drill(args: argparse.Namespace) -> None:
    from .embedder import BookIndex

    idx = BookIndex()
    if not _ensure_index(idx):
        return

    results = idx.query_hierarchical(
        args.query,
        top_level=args.top,
        drill_level=args.drill,
        n_top=args.n_top,
        n_drill=args.n_drill,
    )

    if not results:
        console.print("[yellow]No results found.[/yellow]")
        return

    console.print(
        f"\n[bold]Drill: [cyan]{args.query}[/cyan] "
        f"({args.top} -> {args.drill})[/bold]\n"
    )

    for i, r in enumerate(results, 1):
        meta = r["metadata"]
        parent = r.get("_parent", {})
        score = 1 - r["distance"]

        header = (
            f"[{i}] Ch {meta['chapter_num']}: {meta['chapter_title']} "
            f"| scene {meta['scene_idx']} | para {meta['paragraph_idx']}"
        )
        header += f"  [dim](sim: {score:.3f})[/dim]"

        text_display = r["text"][:500] + ("..." if len(r["text"]) > 500 else "")

        console.print(Panel(
            text_display,
            title=header,
            title_align="left",
            border_style="green" if score > 0.5 else "dim",
            width=min(console.width, 120),
        ))


def cmd_stats(args: argparse.Namespace) -> None:
    from .embedder import BookIndex

    idx = BookIndex()
    if not _ensure_index(idx):
        return

    counts = idx.stats()
    table = Table(title="Index Statistics", box=box.ROUNDED)
    table.add_column("Level", style="cyan")
    table.add_column("Units Indexed", style="green", justify="right")
    table.add_column("Use For", style="dim")

    descriptions = {
        "sentence": "Precise fact / continuity lookups",
        "paragraph": "Sensory beats, dialogue, action moments",
        "scene": "Scene-level narrative segments (split on ---)",
        "chapter": "Thematic / structural queries",
        "act": "Arc-level story structure",
    }

    for level in LEVELS:
        table.add_row(level, str(counts.get(level, 0)), descriptions.get(level, ""))
    table.add_row("", "", "")
    table.add_row("[bold]Total[/bold]", f"[bold]{sum(counts.values())}[/bold]", "")
    console.print(table)


def main() -> None:
    parser = argparse.ArgumentParser(
        prog="indexer",
        description="Multi-level semantic index for The Last Pure Thing",
    )
    sub = parser.add_subparsers(dest="command")

    # setup
    p_setup = sub.add_parser("setup", help="Download NLTK data (punkt) if needed")
    p_setup.set_defaults(func=cmd_setup)

    # build
    p_build = sub.add_parser("build", help="Build or rebuild the semantic index")
    p_build.add_argument("--force", action="store_true", help="Force full rebuild")
    p_build.set_defaults(func=cmd_build)

    # search
    p_search = sub.add_parser("search", help="Semantic search at a given level")
    p_search.add_argument("query", help="Search query")
    p_search.add_argument("-l", "--level", choices=LEVELS, default="paragraph",
                          help="Granularity level (default: paragraph)")
    p_search.add_argument("-n", type=int, default=10, help="Number of results")
    p_search.add_argument("--act", type=str, default=None,
                          help="Filter by act name")
    p_search.add_argument("--chapter", type=int, default=None,
                          help="Filter by chapter number")
    p_search.set_defaults(func=cmd_search)

    # drill
    p_drill = sub.add_parser("drill", help="Hierarchical drill-down search")
    p_drill.add_argument("query", help="Search query")
    p_drill.add_argument("--top", choices=LEVELS, default="chapter",
                         help="Top-level search (default: chapter)")
    p_drill.add_argument("--drill", choices=LEVELS, default="paragraph",
                         help="Drill-down level (default: paragraph)")
    p_drill.add_argument("--n-top", type=int, default=3,
                         help="Number of top-level results")
    p_drill.add_argument("--n-drill", type=int, default=5,
                         help="Drill results per top-level match")
    p_drill.set_defaults(func=cmd_drill)

    # stats
    p_stats = sub.add_parser("stats", help="Show index statistics")
    p_stats.set_defaults(func=cmd_stats)

    args = parser.parse_args()
    if not args.command:
        parser.print_help()
        sys.exit(1)
    args.func(args)


if __name__ == "__main__":
    main()
