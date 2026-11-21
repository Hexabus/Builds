"""Answer questions from a pack. Always cites. Says so when the files don't cover it.

Two modes:
  - search-only (default, zero setup): shows the best matching passages with sources.
  - LLM mode: if the pack's manifest sets "llm_endpoint" (any OpenAI-compatible server,
    e.g. llama.cpp `llama-server`, llamafile, Ollama), the model writes a short answer
    using ONLY the retrieved passages.
"""
import json
import re
import urllib.request

from .store import search

MIN_COVERAGE = 0.4  # passage must contain >=40% of the question's key terms

SYSTEM = (
    "You answer ONLY from the numbered passages provided. If they do not contain the "
    "answer, reply exactly: Not in my files. "
    "Never guess, infer or use outside knowledge. If the question asks for a specific list or "
    "number of items (for example \"the three modes\") and the passages do not name every one, "
    "reply exactly: Not in my files. Cite passages like [1]. Be brief."
)

DECLINE = "Not in my files."


def _llm(endpoint, model, question, hits):
    ctx = "\n\n".join(f"[{i}] ({h[1]}, {h[2]})\n{h[3]}" for i, h in enumerate(hits, 1))
    body = json.dumps({
        "model": model or "local",
        "temperature": 0.1,
        "max_tokens": 400,  # answers are meant to be short; also bounds worst-case latency
        # "thinking" models (e.g. Qwen3.5) can reason for minutes on CPU; this is retrieval-grounded
        # Q&A, so ask the chat template to skip the reasoning phase (ignored by templates without it)
        "chat_template_kwargs": {"enable_thinking": False},
        "messages": [
            {"role": "system", "content": SYSTEM},
            {"role": "user", "content": f"Passages:\n{ctx}\n\nQuestion: {question}"},
        ],
    }).encode()
    req = urllib.request.Request(endpoint, body, {"Content-Type": "application/json"})
    with urllib.request.urlopen(req, timeout=300) as r:
        text = json.load(r)["choices"][0]["message"]["content"]
    # some small "thinking" models emit <think>…</think>; hide it from the answer
    return re.sub(r"<think>.*?</think>", "", text, flags=re.S).strip()


def answer(db, manifest, question, k=4, endpoint=None):
    hits = [h for h in search(db, question, k) if h[0] >= MIN_COVERAGE]
    if not hits:
        return "Not in my files.", []
    endpoint = endpoint or manifest.get("llm_endpoint")
    if endpoint:
        try:
            text = _llm(endpoint, manifest.get("llm_model"), question, hits)
            if re.search(r"not in my files\.?\s*$", text, re.I):  # a decline needs no sources list
                return DECLINE, []
            src = "\n".join(f"  [{i}] {h[1]}, {h[2]}" for i, h in enumerate(hits, 1))
            return f"{text}\n\nSources:\n{src}", hits
        except Exception as e:  # model server not running -> degrade gracefully
            note = f"(model unavailable: {e}; showing sources only)\n"
            return note + _format(hits), hits
    return _format(hits), hits


def _format(hits):
    out = []
    for i, (score, src, loc, text) in enumerate(hits, 1):
        snippet = text if len(text) < 600 else text[:600].rsplit(" ", 1)[0] + " …"
        out.append(f"[{i}] {src} ({loc})\n{snippet}")
    return "\n\n".join(out)
