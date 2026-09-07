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
