from __future__ import annotations

from fastapi import FastAPI, HTTPException
from fastapi.responses import HTMLResponse
from pydantic import BaseModel, Field

from ask import answer, min_score

app = FastAPI(
    title="Support RAG Chat",
    description="FAQ RAG with citations and refusal - not a ChatGPT wrapper.",
    version="0.1.0",
)


class AskRequest(BaseModel):
    q: str = Field(min_length=1, max_length=2000)
    retriever: str = Field(default="tfidf", pattern="^(tfidf|embed)$")
    no_llm: bool = False
    k: int = Field(default=3, ge=1, le=10)


class Hit(BaseModel):
    score: float
    source: str
    text: str


class AskResponse(BaseModel):
    answer: str
    refused: bool
    hits: list[Hit]
    retriever: str


@app.get("/api/health")
def health():
    return {"ok": True}


@app.post("/api/ask", response_model=AskResponse)
def ask(body: AskRequest):
    try:
        hits, text = answer(body.q, body.retriever, body.no_llm, body.k)
    except SystemExit as exc:
        raise HTTPException(status_code=500, detail=str(exc) or "corpus error") from exc
    except Exception as exc:
        raise HTTPException(status_code=502, detail=str(exc)) from exc

    floor = min_score(body.retriever)
    best = hits[0][0] if hits else 0.0
    refused = "RECUSA" in text.upper() or best < floor

    return AskResponse(
        answer=text,
        refused=refused,
        hits=[
            Hit(score=score, source=ch["source"], text=ch["text"])
            for score, ch in hits
        ],
        retriever=body.retriever,
    )


@app.get("/", response_class=HTMLResponse)
def home():
    return HTML_PAGE


HTML_PAGE = """<!DOCTYPE html>
<html lang="en">
<head>
  <meta charset="utf-8" />
  <meta name="viewport" content="width=device-width, initial-scale=1" />
  <title>Support RAG Chat</title>
  <style>
    :root {
      --bg: #0b1220;
      --fg: #e8eef7;
      --accent: #3d8bfd;
      --border: #243044;
      --refuse: #f0a0a0;
    }
    * { box-sizing: border-box; }
    body {
      margin: 0;
      min-height: 100vh;
      font-family: "Segoe UI", system-ui, sans-serif;
      background: radial-gradient(1200px 600px at 10% -10%, #152238, var(--bg));
      color: var(--fg);
    }
    main {
      max-width: 42rem;
      margin: 0 auto;
      padding: 2.5rem 1.25rem 4rem;
    }
    h1 { font-size: 1.6rem; margin: 0 0 0.35rem; letter-spacing: -0.02em; }
    .lead { color: #9ab0c8; margin: 0 0 1.5rem; line-height: 1.45; }
    form { display: grid; gap: 0.75rem; }
    textarea {
      width: 100%;
      min-height: 5.5rem;
      resize: vertical;
      padding: 0.85rem 1rem;
      border: 1px solid var(--border);
      border-radius: 0.5rem;
      background: #101a2c;
      color: var(--fg);
      font: inherit;
    }
    .row { display: flex; flex-wrap: wrap; gap: 0.75rem; align-items: center; }
    label { font-size: 0.85rem; color: #9ab0c8; display: flex; gap: 0.4rem; align-items: center; }
    button {
      border: 0;
      border-radius: 0.5rem;
      padding: 0.65rem 1.1rem;
      background: var(--accent);
      color: #061018;
      font-weight: 600;
      cursor: pointer;
    }
    button:disabled { opacity: 0.55; cursor: wait; }
    #out {
      margin-top: 1.5rem;
      padding-top: 1.25rem;
      border-top: 1px solid var(--border);
      display: none;
