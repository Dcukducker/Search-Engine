import asyncio
from fastapi import FastAPI, Query
from fastapi.staticfiles import StaticFiles
from fastapi.responses import HTMLResponse
import uvicorn
from engine import MultiFactorEngine

app = FastAPI(title="Multi-Factor Search Engine")
engine = MultiFactorEngine()

@app.on_event("startup")
async def startup_event():
    # Load and index data in background thread so the web server starts immediately
    loop = asyncio.get_running_loop()
    loop.run_in_executor(None, engine.load_and_index)

app.mount("/static", StaticFiles(directory="static"), name="static")

@app.get("/", response_class=HTMLResponse)
async def read_index():
    with open("static/index.html", "r", encoding="utf-8") as f:
        return f.read()

@app.get("/api/search")
def search(
    q: str = Query(..., min_length=1),
    w_bm25: float = Query(1.0),
    w_sem: float = Query(1.0),
    w_auth: float = Query(1.0),
    top_k: int = Query(20)
):
    if not engine.is_ready:
        return {"status": "loading", "message": "Engine is building indices. This may take a minute on the first run as NLP models download...", "results": []}
        
    results = engine.search(q, w_bm25, w_sem, w_auth, top_k)
    return {"status": "ready", "results": results}

if __name__ == "__main__":
    print("Starting Web Server. Access the UI at: http://127.0.0.1:8000")
    uvicorn.run("main:app", host="127.0.0.1", port=8000, reload=False)
