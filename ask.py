import argparse
import json
import math
import os
import re
from pathlib import Path

ROOT = Path(__file__).resolve().parent
CORPUS = ROOT / "corpus"
try:
    from dotenv import load_dotenv

    load_dotenv(ROOT / ".env")
except ImportError:
    pass

STOP = {
    "a", "o", "os", "as", "um", "uma", "de", "do", "da", "dos", "das", "e", "ou",
    "que", "para", "com", "em", "no", "na", "nos", "nas", "por", "é", "são",
    "não", "se", "ao", "à", "isso", "isto", "the", "and",
}
MIN_SCORE_TFIDF = 0.08
MIN_SCORE_EMBED = 0.35
TOP_K = 3
CHUNK_CHARS = 700
CHUNK_OVERLAP = 80


def tokenize(text: str) -> list[str]:
    return [t for t in re.findall(r"[a-záéíóúâêôãõç0-9]+", text.lower()) if t not in STOP and len(t) > 1]


def chunk_text(text: str) -> list[str]:
    parts = []
    i = 0
    while i < len(text):
        piece = text[i : i + CHUNK_CHARS]
        parts.append(piece.strip())
        if i + CHUNK_CHARS >= len(text):
            break
        i += CHUNK_CHARS - CHUNK_OVERLAP
    return [p for p in parts if p]


def load_chunks() -> list[dict]:
    chunks = []
    for path in sorted(CORPUS.glob("*.md")):
        raw = path.read_text(encoding="utf-8")
        for n, piece in enumerate(chunk_text(raw)):
            chunks.append({"id": f"{path.name}#{n}", "source": path.name, "text": piece})
    if not chunks:
        raise SystemExit("corpus/ vazio")
    return chunks


def tfidf_matrix(docs_tokens: list[list[str]]) -> list[dict[str, float]]:
    n = len(docs_tokens)
    df: dict[str, int] = {}
    for toks in docs_tokens:
        for t in set(toks):
            df[t] = df.get(t, 0) + 1
    vecs = []
    for toks in docs_tokens:
        tf = {}
        for t in toks:
            tf[t] = tf.get(t, 0) + 1
        length = len(toks) or 1
        vec = {}
        for t, c in tf.items():
            idf = math.log((n + 1) / (df[t] + 1)) + 1
            vec[t] = (c / length) * idf
        vecs.append(vec)
    return vecs


def cosine(a: dict[str, float], b: dict[str, float]) -> float:
    keys = set(a) | set(b)
    dot = sum(a.get(k, 0.0) * b.get(k, 0.0) for k in keys)
    na = math.sqrt(sum(v * v for v in a.values())) or 1e-9
    nb = math.sqrt(sum(v * v for v in b.values())) or 1e-9
    return dot / (na * nb)


def retrieve_tfidf(query: str, chunks: list[dict], k: int) -> list[tuple[float, dict]]:
    docs = [tokenize(c["text"]) for c in chunks]
    q = tokenize(query)
    mat = tfidf_matrix(docs + [q])
    qv = mat[-1]
    scored = [(cosine(mat[i], qv), chunks[i]) for i in range(len(chunks))]
    scored.sort(key=lambda x: x[0], reverse=True)
    return scored[:k]


def gemini_client():
    key = os.getenv("GEMINI_API_KEY", "").strip() or os.getenv("GEMINI_API_KEY", "").strip()
    if not key:
        return None
    from google import genai

    return genai.Client(api_key=key)


def retrieve_embed(query: str, chunks: list[dict], k: int, client) -> list[tuple[float, dict]]:
    model = os.getenv("EMBED_MODEL", "text-embedding-004")
    embs = []
    for text in [c["text"] for c in chunks] + [query]:
        res = client.models.embed_content(model=model, contents=text)
        embs.append(res.embeddings[0].values)

    def cos(u, v):
        dot = sum(a * b for a, b in zip(u, v))
        nu = math.sqrt(sum(a * a for a in u)) or 1e-9
        nv = math.sqrt(sum(b * b for b in v)) or 1e-9
        return dot / (nu * nv)

    qv = embs[-1]
    scored = [(cos(embs[i], qv), chunks[i]) for i in range(len(chunks))]
    scored.sort(key=lambda x: x[0], reverse=True)
    return scored[:k]


def retrieve(query: str, chunks: list[dict], retriever: str, client, k: int):
    if retriever == "embed":
        if client is None:
            raise SystemExit("GEMINI_API_KEY vazia: embed precisa da chave (ou use --retriever tfidf)")
        return retrieve_embed(query, chunks, k, client)
    return retrieve_tfidf(query, chunks, k)


def min_score(retriever: str) -> float:
    return MIN_SCORE_EMBED if retriever == "embed" else MIN_SCORE_TFIDF


def format_hits(hits: list[tuple[float, dict]]) -> str:
    lines = []
    for score, ch in hits:
        lines.append(f"[{ch['source']} score={score:.3f}]\n{ch['text']}")
    return "\n\n---\n\n".join(lines)


def generate(query: str, hits: list[tuple[float, dict]], client, retriever: str) -> str:
    floor = min_score(retriever)
    best = hits[0][0] if hits else 0.0
    if best < floor:
        return "RECUSA: não está na base de conhecimento (score baixo). Não vou inventar."
    ctx = format_hits(hits)
    prompt = (
        "Responda só com o contexto abaixo. Cite o nome do arquivo. "
        "Se o contexto não responder, diga exatamente: RECUSA: não está na base.\n\n"
        f"CONTEXTO:\n{ctx}\n\nPERGUNTA: {query}"
    )
    if client is None:
        return f"(sem LLM; trechos recuperados)\n\n{ctx}"
    model = os.getenv("GEMINI_MODEL", "gemini-2.0-flash")
    out = client.models.generate_content(model=model, contents=prompt)
    return (out.text or "").strip()


def answer(query: str, retriever: str, no_llm: bool, k: int):
    chunks = load_chunks()
    client = None if no_llm else gemini_client()
    hits = retrieve(query, chunks, retriever, gemini_client() if retriever == "embed" else client, k)
    text = generate(query, hits, None if no_llm else client, retriever)
    return hits, text


def run_eval(retriever: str, no_llm: bool, k: int) -> None:
    cases = json.loads((ROOT / "eval.json").read_text(encoding="utf-8"))
    ok_src = 0
    ok_ref = 0
    n_src = 0
    n_ref = 0
    for case in cases:
        hits, text = answer(case["q"], retriever, no_llm, k)
        sources = {h[1]["source"] for h in hits}
        refused = "RECUSA" in text.upper()
        if case["expect_refuse"]:
            n_ref += 1
            hit = refused or (hits[0][0] < min_score(retriever) if hits else True)
            ok_ref += int(hit)
            tag = "refuse"
        else:
            n_src += 1
            hit = case["must_source"] in sources and not refused
            ok_src += int(hit)
            tag = "source"
        mark = "OK" if hit else "FAIL"
        print(f"{mark} [{tag}] {case['q']}")
        print(f"  top: {', '.join(f'{s}:{sc:.2f}' for sc, c in hits for s in [c['source']])}")
        print(f"  {text[:220].replace(chr(10), ' ')}\n")
    print(f"hit@{k} (fonte): {ok_src}/{n_src}")
    print(f"recusa correta: {ok_ref}/{n_ref}")


def main():
    p = argparse.ArgumentParser()
    p.add_argument("q", nargs="?", help="pergunta")
    p.add_argument("--eval", action="store_true")
    p.add_argument("--no-llm", action="store_true")
    p.add_argument("--retriever", choices=["tfidf", "embed"], default="tfidf")
    p.add_argument("-k", type=int, default=TOP_K)
    args = p.parse_args()
    if args.eval:
        run_eval(args.retriever, args.no_llm, args.k)
        return
    if not args.q:
        p.print_help()
        raise SystemExit(1)
    hits, text = answer(args.q, args.retriever, args.no_llm, args.k)
    print(format_hits(hits))
    print("\n====\n")
    print(text)


if __name__ == "__main__":
    main()
