# Cartridge: project context

Goal: let anyone build a small, portable, offline "specialty AI" by feeding it files and links, then copy the
result to a USB drive. Not training: a pack = indexed documents (SQLite FTS5) + a small pretrained GGUF model +
the llama.cpp engine, all plain files in one folder. Answers must cite sources and say "Not in my files." when
the documents don't cover the question.

## State (v0.2)
- `python -m cartridge build|add|info|ask|setup|models|compare` (see README.md). Pure stdlib; PDF needs `pip install pypdf`.
- TESTED (in a sandbox): build from txt/md/PDF, keyword retrieval (originally 10/10 expected passages in top 4 on a 151-page test book that is no longer in the repo),
  "Not in my files" gating, start/ask/stop lifecycle of the model server using a FAKE stand-in engine.
- TESTED with real models (CPU-only, 4 cores): `runtime.fetch_model` against Hugging Face (SmolLM3 3B and
  ggml-org/Qwen3.5-4B-GGUF, Q4_K_M), and `compare` with both on a 26-page Maine PFML rules PDF
  (results/compare.md; questions and answer key in tests/). Qwen answered more cleanly (11/13 right, 0 wrong); SmolLM3 11/13 right, 2 wrong.
  Qwen3.5 is a thinking model: with thinking on it timed out at 120 s per answer, so `_llm` now sends
  `enable_thinking: false`, `max_tokens: 400` and a 300 s timeout.
- NOT TESTED: `python -m cartridge setup` end to end, and the llama.cpp release download (GitHub API/assets were
  not reachable from the sandbox). The engine used in testing was built from source and copied to engine/linux-x64/.
  Asset names were taken from llama.cpp's release.yml (e.g. llama-bin-win-cpu-x64.zip, llama-<tag>-bin-ubuntu-x64.tar.gz).
- Retrieval (store.search): keyword ranking (IDF-weighted coverage, BM25 tie-break) plus exact-match signals that go first
  (store._exact_hits): (1) definitions of the asked-about term for "what is/does X [mean]" questions ("X" means ... or glossary
  style), (2) passages containing an identifier from the question (SESSION_COOKIE_AGE, matched as the phrase "session cookie age",
  literal spelling preferred), (3) passages containing a version number (6.1) plus another key term. Without these, "day" was
  dropped by the >30%-of-passages filter and BM25 preferred passages repeating a word over its one-line definition; one-character
  tokens ("6", "1" in "6.1") were discarded; identifiers were split into common words.
- Large-corpus test: Django 6.1.3 docs (tests/fetch_django_docs.py downloads them from PyPI; 680 files, 10,187 passages,
  builds in ~4 s). `python3 tests/test_django_questions.py`: 20/20 in top 4, 13/20 first (originally 10/20 and 4/20);
  out-of-scope questions are still rejected. FMLA: 12/12 in top 4, 10/12 first (originally 11/12 and 9/12). No known misses left.
  The last two fixes: (a) list-aware chunking (ingest._paragraphs): "Django provides three fetch modes:" plus its numbered items
  stays in one passage (it used to be cut after item 2, so no passage named all three modes), (b) an identifier at the start of a
  line, list item or directive (heading "``TIME_ZONE``", "2. ``FETCH_PEERS`` fetches...") counts as a defining occurrence and is
  preferred, (c) a run of 3+ consecutive key words that appears verbatim is promoted, but only if the passage also contains every
  other key term (without that condition, "private plan substitution" pushed the correct FMLA fee passage out of the top 4;
  blending ranks with reciprocal-rank fusion failed for the same reason: BM25 ranks 1-10 are nearly flat).
  Heuristics were tuned on these two documents only; re-check on other corpora. Rebuild packs after chunking changes.
- Model behaviour (results/compare_django_*.md): when the needed passage is missing, models used to guess or invent
  (both made up a third fetch mode). The system prompt now forbids guessing and says to decline when a list/count is not fully
  named, and declines print no Sources list. Recheck on 9 questions: Qwen3.5 4B now declines the fetch-modes question and
  stays correct on the rest; SmolLM3 3B still invents "FETCH_MANY" there (but no longer loops, and answers 8 of the other 8
  sensibly). Small models obey "don't guess" imperfectly: do not rely on the prompt alone, keep improving retrieval.
- `build` now fails (non-zero exit) when no source could be indexed; `compare` reports load/answer timings.
- Test document is the Maine Paid Family and Medical Leave rules (tests/maine_fmla.pdf, 26 pages). Retrieval test:
  `python3 tests/test_fmla_questions.py` (builds a temp pack, 12/12 in top 4, 10/12 first).
  Model comparison questions: tests/fmla_questions.txt, answer key: tests/fmla_answer_key.txt. The earlier DMSO test was removed.

## Rules
- Keep it stdlib-only (except optional pypdf) so a pack runs anywhere with just Python.
- Never let a model answer without retrieved passages; keep the sources footer.
- Don't vouch for the content of user documents; the tool just retrieves and cites.
- Ask before adding heavy dependencies.

## Roadmap (in order)
1. Verify setup/ask/compare with real models (SmolLM3 3B = ggml-org/SmolLM3-3B-GGUF; Qwen3.5 4B GGUF repo: find on Hugging Face).
2. Embedding-based retrieval alongside keywords (small embedding GGUF served by llama-server), stored in the pack DB.
3. Scanned-PDF support (OCR), better chunking.
4. Optional LoRA adapter for tone/format. 5. Desktop UI wizard.
