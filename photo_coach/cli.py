from __future__ import annotations

import json
from pathlib import Path
from typing import Optional

import typer
from rich.console import Console
from rich.table import Table

from .cull import group_near_duplicates
from .scan import scan_folder
from .search import load_index, save_index, search_photos
from .trends import build_trend_tips

app = typer.Typer(add_completion=False, help="Photo Coach — local cull / score / tips / search")
console = Console()


@app.command()
def scan(
    folder: Path = typer.Argument(..., exists=True, file_okay=False, help="Photo folder"),
    out: Path = typer.Option(Path(".photo-coach/index.json"), help="Index output path"),
    max_distance: int = typer.Option(4, help="pHash distance for near-duplicates"),
):
    """Scan folder, score photos, group near-duplicates, write index."""
    photos = scan_folder(folder)
    groups = group_near_duplicates(photos, max_distance=max_distance)
    save_index(out, photos)
    console.print(f"[green]Scanned {len(photos)} photos → {out}[/green]")
    table = Table(title="Cull groups (suggested keep)")
    table.add_column("Group")
    table.add_column("Keep")
    table.add_column("Members")
    for g in groups:
        if len(g.members) == 1 and g.members[0].keep:
            continue
        if len(g.members) > 1:
            table.add_row(
                str(g.group_id),
                Path(g.suggested_keep).name,
                ", ".join(f"{m.filename}({m.score})" for m in g.members),
            )
    if table.row_count:
        console.print(table)
    else:
        console.print("No near-duplicate groups above threshold.")
    tips = build_trend_tips(photos)
    console.print("\n[bold]趋势建议[/bold]")
    for i, tip in enumerate(tips, 1):
        console.print(f"{i}. {tip}")


@app.command()
def tips(
    index: Path = typer.Option(Path(".photo-coach/index.json"), exists=True),
    lang: str = typer.Option("zh"),
):
    """Print trend tips from an existing index."""
    photos = load_index(index)
    for i, tip in enumerate(build_trend_tips(photos, lang=lang), 1):
        console.print(f"{i}. {tip}")


@app.command("search")
def search_cmd(
    query: str = typer.Argument(..., help="Fuzzy Chinese/English prompt"),
    index: Path = typer.Option(Path(".photo-coach/index.json"), exists=True),
    top_k: int = typer.Option(10),
):
    """Semantic/keyword search over indexed photos (knowledge-base style)."""
    photos = load_index(index)
    mode, hits = search_photos(photos, query, top_k=top_k)
    console.print(f"[cyan]mode={mode}[/cyan] query={query!r}")
    if not hits:
        console.print("No hits. Try another prompt, or set PHOTO_COACH_EMBED=1 for embeddings.")
        raise typer.Exit(code=1)
    table = Table(title="Search results")
    table.add_column("Score")
    table.add_column("File")
    table.add_column("Flags")
    for p, s in hits:
        table.add_row(f"{s:.3f}", p.filename, ",".join(p.flags) or "-")
    console.print(table)


@app.command()
def serve(
    index: Path = typer.Option(Path(".photo-coach/index.json")),
    host: str = "127.0.0.1",
    port: int = 8765,
):
    """Start a tiny local web UI."""
    import uvicorn
    from .web import create_app

    uvicorn.run(create_app(index), host=host, port=port)


@app.command()
def demo():
    """Run scan+search against bundled fixtures."""
    root = Path(__file__).resolve().parent.parent / "fixtures"
    out = Path(".photo-coach/demo-index.json")
    photos = scan_folder(root)
    group_near_duplicates(photos)
    save_index(out, photos)
    console.print(json.dumps([p.to_dict() for p in photos], ensure_ascii=False, indent=2)[:800] + "\n...")
    mode, hits = search_photos(photos, "红色 雨伞", top_k=3)
    console.print(f"search mode={mode}")
    for p, s in hits:
        console.print(f"  {s:.3f} {p.filename}")
    for tip in build_trend_tips(photos):
        console.print(f"- {tip}")


if __name__ == "__main__":
    app()
