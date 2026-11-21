# Cartridge

Build portable, offline, cited knowledge packs. Drop in files and links, get a folder you can copy to a USB drive.

    python3 -m cartridge build ./my_docs https://example.com/page -o MyPack --name "My Pack"
    python3 -m cartridge ask MyPack "your question"     # or run MyPack/ask.sh (ask.bat on Windows)
    python3 -m cartridge add MyPack ./more_files
    python3 -m cartridge info MyPack

Supports .txt .md .html .docx .csv .json, URLs, and .pdf (needs `pip install pypdf`).
Pure Python stdlib otherwise; the pack folder carries its own code.

## Add a real AI model (one-time, needs internet)

    python3 -m cartridge setup MyPack --model smollm3 --platforms all

Downloads the llama.cpp engine (Windows, Linux, Mac builds) and a small model into the pack,
so the whole folder runs offline from a USB drive. Then `ask` writes short answers from the
retrieved passages and lists its sources. Use `--platforms current` to fetch only this computer's engine.

Other models: `--model qwen --model-repo OWNER/REPO-GGUF` (any Hugging Face GGUF repo).
Compare models on the same questions:

    python3 -m cartridge setup MyPack --model smollm3
    python3 -m cartridge setup MyPack --model qwen --model-repo OWNER/REPO-GGUF
    python3 -m cartridge compare MyPack dmso_questions.txt -m smollm3,qwen   # writes compare.md

## Modes
- **Search-only (default):** returns the best matching passages with source + location. If the files don't cover the question: "Not in my files."
- **LLM mode:** run any OpenAI-compatible local server (llama.cpp `llama-server`, llamafile, Ollama) and build with
  `--llm-endpoint http://localhost:8080/v1/chat/completions`. The model answers using ONLY retrieved passages and cites them.

## Roadmap
1. Bundle a llamafile + small quantized model inside the pack (true one-folder USB package)
2. Embedding-based retrieval alongside keyword search
3. Optional LoRA adapter for tone/format
4. Desktop UI wizard
