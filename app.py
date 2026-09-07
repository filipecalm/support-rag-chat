from __future__ import annotations

from fastapi import FastAPI, HTTPException
from fastapi.responses import HTMLResponse
from pydantic import BaseModel, Field

from ask import answer, min_score

app = FastAPI(
    title="Support RAG Chat",
    description="FAQ RAG with citations and refusal â€” not a ChatGPT wrapper.",
    version="0.1.0",
)
