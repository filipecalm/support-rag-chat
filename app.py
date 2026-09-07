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


