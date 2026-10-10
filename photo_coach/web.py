from __future__ import annotations

from pathlib import Path

from fastapi import FastAPI, Query
from fastapi.responses import HTMLResponse, JSONResponse

from .search import load_index, search_photos
from .trends import build_trend_tips


def create_app(index_path: Path) -> FastAPI:
    app = FastAPI(title="Photo Coach")

    @app.get("/", response_class=HTMLResponse)
    def home():
        return """
<!doctype html>
<html lang="zh">
<meta charset="utf-8"/>
<title>Photo Coach</title>
<body style="font-family:system-ui;max-width:720px;margin:2rem auto;">
  <h1>Photo Coach</h1>
  <p>本地选片 / 打分 / 趋势建议 / 模糊检索</p>
  <form action="/ui/search" method="get">
    <input name="q" placeholder="例如：雨天 红伞" style="width:70%;padding:8px"/>
    <button type="submit">搜索</button>
  </form>
  <p><a href="/api/tips">查看趋势建议 JSON</a></p>
</body>
</html>
"""

    @app.get("/api/tips")
    def tips():
        if not index_path.exists():
            return JSONResponse({"error": "index missing; run photo-coach scan first"}, status_code=404)
        photos = load_index(index_path)
        return {"tips": build_trend_tips(photos)}

    @app.get("/api/search")
    def api_search(q: str = Query(...), top_k: int = 10):
        if not index_path.exists():
            return JSONResponse({"error": "index missing"}, status_code=404)
        photos = load_index(index_path)
        mode, hits = search_photos(photos, q, top_k=top_k)
        return {
            "mode": mode,
            "results": [{"score": s, "file": p.filename, "path": p.path, "flags": p.flags} for p, s in hits],
        }

    @app.get("/ui/search", response_class=HTMLResponse)
    def ui_search(q: str = ""):
        if not index_path.exists():
            return HTMLResponse("<p>请先运行 photo-coach scan</p>", status_code=404)
        photos = load_index(index_path)
        mode, hits = search_photos(photos, q, top_k=20)
        rows = "".join(
            f"<li><b>{s:.3f}</b> {p.filename} <small>{','.join(p.flags)}</small></li>" for p, s in hits
        ) or "<li>无结果</li>"
        return f"""
<!doctype html><html lang="zh"><meta charset="utf-8"/>
<body style="font-family:system-ui;max-width:720px;margin:2rem auto;">
<a href="/">← 返回</a>
<h2>搜索：{q}</h2>
<p>mode={mode}</p>
<ul>{rows}</ul>
</body></html>
"""

    return app
