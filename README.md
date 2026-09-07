# Support RAG Chat

**FAQ support chatbot with retrieval, citations, and refusal.**

Not a generic ChatGPT wrapper. Answers only from a versioned knowledge base. If the answer is not in the corpus, the bot refuses.

## Demo

| Action | Result |
| --- | --- |
| Ask something in the FAQ | Answer + citation (file + snippet) |
| Ask something outside the corpus | Explicit refusal — no hallucination |
| Run eval suite | Hit / refusal scores printed |

Local UI: `uvicorn app:app --reload` → http://127.0.0.1:8000  
API: `POST /api/ask` with `{ "q": "..." }`

## Stack

| Layer | Choice |
| --- | --- |
| API / UI | FastAPI (`app.py`) — Vercel Python entrypoint |
| CLI | `ask.py` (same retrieval + eval) |
| Retrieval | TF-IDF (default) or Gemini embeddings |
| LLM | Gemini lab key (optional; `--no-llm` / `no_llm: true` still shows retrieval) |
| Corpus | Markdown files under `corpus/` |

## Architecture

```text
Question
  → chunk retrieval (score)
  → gate (refuse if below threshold)
  → LLM sees only retrieved snippets
  → answer + citations
```

This is RAG. It is **not** an agent, not fine-tuning, and not a production knowledge platform.

## Quick start

```bash
python -m venv .venv
# Windows: .venv\Scripts\activate
pip install -r requirements.txt
copy .env.example .env
# optional: set GEMINI_API_KEY (lab key only)

python ask.py "Por que a dieta do DietOS não é RAG?"
python ask.py --no-llm "Quem atualiza o Premium depois do pagamento?"
python ask.py --eval --no-llm

uvicorn app:app --reload
```

## What recruiters should notice

- Citation required on every answer
- Refusal path when score is low
- Reproducible eval (`--eval`), not vibes
- Corpus is versioned and free of personal / clinical data

## Limitations (intentional)

- Single-hop FAQ only — no multi-tool agent
- No SharePoint / Azure AI Search
- Lab model key — not a production SLA
- Lexical retrieval misses synonyms unless the corpus covers them

## License

MIT
