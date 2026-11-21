# Cartridge: project context

Goal: let anyone build a small, portable, offline "specialty AI" by feeding it files and links, then copy the
result to a USB drive. Not training: a pack = indexed documents (SQLite FTS5) + a small pretrained GGUF model +
the llama.cpp engine, all plain files in one folder. Answers must cite sources and say "Not in my files." when
the documents don't cover the question.

## State (v0.2)
- `python -m cartridge build|add|info|ask|setup|models|compare` (see README.md). Pure stdlib; PDF needs `pip install pypdf`.
- TESTED (in a sandbox): build from txt/md/PDF, keyword retrieval (10/10 expected passages in top 4, 8/10 first on a 151-page book),
  "Not in my files" gating, start/ask/stop lifecycle of the model server using a FAKE stand-in engine.
- TESTED with real models (CPU-only, 4 cores): `runtime.fetch_model` against Hugging Face (SmolLM3 3B and
  ggml-org/Qwen3.5-4B-GGUF, Q4_K_M), and `compare` with both on a 26-page Maine PFML rules PDF
  (results/compare.md, answer key in results/). Qwen answered more cleanly (11/13 right, 0 wrong); SmolLM3 11/13 right, 2 wrong.
  Qwen3.5 is a thinking model: with thinking on it timed out at 120 s per answer, so `_llm` now sends
  `enable_thinking: false`, `max_tokens: 400` and a 300 s timeout.
- NOT TESTED: `python -m cartridge setup` end to end, and the llama.cpp release download (GitHub API/assets were
  not reachable from the sandbox). The engine used in testing was built from source and copied to engine/linux-x64/.
  Asset names were taken from llama.cpp's release.yml (e.g. llama-bin-win-cpu-x64.zip, llama-<tag>-bin-ubuntu-x64.tar.gz).
- Known retrieval gap: "what is a business day" misses the definition on p.1 (not in top 4); cause not investigated.
- `build` now fails (non-zero exit) when no source could be indexed; `compare` reports load/answer timings.
- test_dmso_questions.py still hardcodes /home/claude/cartridge and /tmp/dmsopack and needs the DMSO PDF (not included).

## Rules
- Keep it stdlib-only (except optional pypdf) so a pack runs anywhere with just Python.
- Never let a model answer without retrieved passages; keep the sources footer.
- Don't vouch for the content of user documents (the test book is about DMSO health claims); the tool just retrieves and cites.
- Ask before adding heavy dependencies.

## Roadmap (in order)
1. Verify setup/ask/compare with real models (SmolLM3 3B = ggml-org/SmolLM3-3B-GGUF; Qwen3.5 4B GGUF repo: find on Hugging Face).
2. Embedding-based retrieval alongside keywords (small embedding GGUF served by llama-server), stored in the pack DB.
3. Scanned-PDF support (OCR), better chunking.
4. Optional LoRA adapter for tone/format. 5. Desktop UI wizard.
