"""
CLI for multi-level semantic book indexing.

Usage:
    python -m indexer setup              Download NLTK data (punkt, punkt_tab) if needed
    python -m indexer build              Build/rebuild the index
    python -m indexer search "query"     Search at paragraph level (default)
    python -m indexer search "query" -l sentence -n 20
    python -m indexer search "query" -l scene --act "Act I – The Hire"
    python -m indexer search "query" -l chapter --chapter 7
    python -m indexer drill "query"      Hierarchical: chapters -> paragraphs
    python -m indexer stats              Show index statistics

Note: BookIndex is lazy-imported inside command handlers to avoid loading the
~500MB embedding model for lightweight commands (setup, stats).
"""

from __future__ import annotations

import argparse
import sys
from pathlib import Path

import nltk
from rich.console import Console

from bookops.pdf_ingest import ingest_pdf_to_chapters
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


def cmd_ingest_pdf(args: argparse.Namespace) -> None:
    """Extract PDF, detect chapters, write Markdown, optionally run indexer build."""
    pdf_path = Path(args.pdf).resolve()
    if args.chapters_dir:
        chapters_dir = Path(args.chapters_dir).resolve()
    else:
        chapters_dir = pdf_path.parent / "chapters"

    with console.status("[bold green]Extracting PDF and detecting chapters..."):
        written = ingest_pdf_to_chapters(
            pdf_path,
            output_dir=chapters_dir,
            skip_pages=args.skip_pages,
            toc_page=args.toc_page,
        )

    console.print(f"[green]Wrote {len(written)} chapters to {chapters_dir}[/green]")
    for p in written[:5]:
        console.print(f"  [dim]{p.name}[/dim]")
    if len(written) > 5:
        console.print(f"  [dim]... and {len(written) - 5} more[/dim]")

    if args.build:
        # Lazy import: BookIndex loads ~500MB embedding model
        from .embedder import BookIndex

        book_id = getattr(args, "book_id", None)
        persist_dir = Path(args.index_dir).resolve() if getattr(args, "index_dir", None) else None
        with console.status("[bold green]Building index..."):
            idx = BookIndex(
                chapters_dir=chapters_dir,
                book_id=book_id,
                persist_dir=persist_dir,
            )
            counts = idx.build(force=True)
        table = Table(title="Index Built", box=box.ROUNDED)
        table.add_column("Level", style="cyan")
        table.add_column("Units", style="green", justify="right")
        for level in LEVELS:
            table.add_row(level, str(counts.get(level, 0)))
        console.print(table)


def cmd_setup(args: argparse.Namespace) -> None:
    """Download NLTK punkt tokenizer data required for sentence splitting."""
    with console.status("[bold green]Downloading NLTK punkt tokenizer..."):
        nltk.download("punkt")
        nltk.download("punkt_tab")
    console.print("[green]NLTK data ready. You can run 'python -m indexer build'.[/green]")


def cmd_build(args: argparse.Namespace) -> None:
    # Lazy import: BookIndex loads ~500MB embedding model
    from .embedder import BookIndex

    persist_dir = Path(args.index_dir).resolve() if getattr(args, "index_dir", None) else None
    chapters_dir = Path(args.chapters_dir).resolve() if getattr(args, "chapters_dir", None) else None
    book_id = getattr(args, "book_id", None)

    with console.status("[bold green]Loading model and building index..."):
        idx = BookIndex(
            persist_dir=persist_dir,
            chapters_dir=chapters_dir,
            book_id=book_id,
        )
        counts = idx.build(force=args.force)

    table = Table(title="Index Built", box=box.ROUNDED)
    table.add_column("Level", style="cyan")
    table.add_column("Units", style="green", justify="right")
    for level in LEVELS:
        table.add_row(level, str(counts.get(level, 0)))
    console.print(table)


def cmd_search(args: argparse.Namespace) -> None:
    # Lazy import: BookIndex loads ~500MB embedding model
    from .embedder import BookIndex

    persist_dir = Path(args.index_dir).resolve() if getattr(args, "index_dir", None) else None
    idx = BookIndex(persist_dir=persist_dir)
    if not _ensure_index(idx):
        return

    where = {}
    if args.act:
        where["act"] = args.act
    if args.chapter is not None:
        where["chapter_num"] = args.chapter

    if getattr(args, "hybrid", False):
        results = idx.query_hybrid(
            args.query,
            level=args.level,
            n_results=args.n,
            where=where or None,
        )
    else:
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
        if getattr(args, "hybrid", False) and "rrf_score" in r:
            score_display = f"rrf: {r['rrf_score']:.4f}"
            high_score = r["rrf_score"] > 0.02
        else:
            score = 1 - r["distance"]  # cosine distance -> similarity
            score_display = f"sim: {score:.3f}"
            high_score = score > 0.5

        header = (
            f"[{i}] Ch {meta['chapter_num']}: {meta['chapter_title']} "
            f"| {meta['act']} | scene {meta['scene_idx']}"
        )
        if args.level in ("paragraph", "sentence"):
            header += f" | para {meta['paragraph_idx']}"
        if args.level == "sentence":
            header += f" | sent {meta['sentence_idx']}"
        header += f"  [dim]({score_display})[/dim]"

        text_display = r["text"]
        if len(text_display) > 500 and args.level not in ("sentence",):
            text_display = text_display[:500] + "..."

        console.print(Panel(
            text_display,
            title=header,
            title_align="left",
            border_style="blue" if high_score else "dim",
            width=min(console.width, 120),
        ))


def cmd_drill(args: argparse.Namespace) -> None:
    # Lazy import: BookIndex loads ~500MB embedding model
    from .embedder import BookIndex

    persist_dir = Path(args.index_dir).resolve() if getattr(args, "index_dir", None) else None
    idx = BookIndex(persist_dir=persist_dir)
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
    # Lazy import: BookIndex loads ~500MB embedding model
    from .embedder import BookIndex

    persist_dir = Path(args.index_dir).resolve() if getattr(args, "index_dir", None) else None
    idx = BookIndex(persist_dir=persist_dir)
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

    # ingest-pdf
    p_ingest = sub.add_parser("ingest-pdf", help="Extract PDF to Markdown chapters and optionally build index")
    p_ingest.add_argument("pdf", help="Path to PDF file")
    p_ingest.add_argument(
        "--chapters-dir",
        default=None,
        help="Output directory for chapter Markdown files (default: <pdf_dir>/chapters)",
    )
    p_ingest.add_argument("--skip-pages", type=int, default=12, help="Skip first N pages (front matter)")
    p_ingest.add_argument("--toc-page", type=int, default=11, help="Page number of table of contents (1-based)")
    p_ingest.add_argument("--index-dir", default=None, help="Index persistence directory (default: .book_index)")
    p_ingest.add_argument("--book-id", default=None, help="Book ID for act mapping (e.g. alice, last_pure_thing)")
    p_ingest.add_argument("--build", action="store_true", help="Run indexer build after ingest")
    p_ingest.set_defaults(func=cmd_ingest_pdf)

    # setup
    p_setup = sub.add_parser("setup", help="Download NLTK data (punkt) if needed")
    p_setup.set_defaults(func=cmd_setup)

    # build
    p_build = sub.add_parser("build", help="Build or rebuild the semantic index")
    p_build.add_argument("--force", action="store_true", help="Force full rebuild")
    p_build.add_argument("--index-dir", default=None, help="Index persistence directory (default: .book_index)")
    p_build.add_argument(
        "--chapters-dir",
        default=None,
        help="Chapters directory (default: project chapters/). When building after ingest-pdf, pass the same --chapters-dir used for ingest.",
    )
    p_build.add_argument("--book-id", default=None, help="Book ID for act mapping (e.g. alice, last_pure_thing)")
    p_build.set_defaults(func=cmd_build)

    # search
    p_search = sub.add_parser("search", help="Semantic search at a given level")
    p_search.add_argument("--index-dir", default=None, help="Index directory (e.g. .book_index_alice for Alice)")
    p_search.add_argument("query", help="Search query")
    p_search.add_argument("-l", "--level", choices=LEVELS, default="paragraph",
                          help="Granularity level (default: paragraph)")
    p_search.add_argument("-n", type=int, default=10, help="Number of results")
    p_search.add_argument("--act", type=str, default=None,
                          help="Filter by act name")
    p_search.add_argument("--chapter", type=int, default=None,
                          help="Filter by chapter number")
    p_search.add_argument("--hybrid", action="store_true",
                          help="Use hybrid BM25 + semantic search")
    p_search.set_defaults(func=cmd_search)

    # drill
    p_drill = sub.add_parser("drill", help="Hierarchical drill-down search")
    p_drill.add_argument("--index-dir", default=None, help="Index directory (e.g. .book_index_alice for Alice)")
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
    p_stats.add_argument("--index-dir", default=None, help="Index directory (e.g. .book_index_alice for Alice)")
    p_stats.set_defaults(func=cmd_stats)

    args = parser.parse_args()
    if not args.command:
        parser.print_help()
        sys.exit(1)
    args.func(args)


if __name__ == "__main__":
    main()
