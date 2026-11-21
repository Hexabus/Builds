"""cartridge: build portable, cited, offline knowledge packs.

  python -m cartridge build  <folder|url ...> -o PACK [--name NAME]
  python -m cartridge add    PACK <folder|url ...>
  python -m cartridge setup  PACK --model smollm3 [--platforms all]   (download engine + model)
  python -m cartridge ask    PACK "question" [-m MODEL]   (omit question for interactive chat)
  python -m cartridge compare PACK questions.txt -m smollm3,other   (answers side by side)
  python -m cartridge models PACK
  python -m cartridge info   PACK
"""
import argparse
import json
import shutil
import sys
import time
from pathlib import Path

from . import ingest, runtime, store
from .ask import answer

PKG = Path(__file__).resolve().parent

LAUNCH_SH = """#!/bin/sh
cd "$(dirname "$0")" && python3 -m cartridge ask . "$@"
"""
LAUNCH_BAT = """@echo off\r
cd /d "%~dp0"\r
where py >nul 2>&1 && (py -3 -m cartridge ask . %*) || (python -m cartridge ask . %*)\r
pause\r
"""


def _ingest(db, targets):
    total = 0
    for t in targets:
        if t.startswith(("http://", "https://")):
            items = [(t, "url", lambda t=t: ingest.load_url(t))]
        else:
            p = Path(t)
            if not p.exists():
                print(f"  skip {t}: no such file or folder")
                continue
            files = [p] if p.is_file() else sorted(x for x in p.rglob("*") if x.is_file())
            items = [(str(f.relative_to(p.parent if p.is_file() else p)), "file",
                      lambda f=f: ingest.load_file(f)) for f in files]
        for name, kind, loader in items:
            try:
                chunks = loader()
            except Exception as e:
                print(f"  skip {name}: {e}")
                continue
            if not chunks:
                print(f"  skip {name}: unsupported or empty")
                continue
            n = store.add_source(db, name, kind, chunks)
            total += n
            print(f"  + {name}: {n} passages")
    return total


def _load(pack):
    pack = Path(pack)
    mpath = pack / "manifest.json"
    if not mpath.exists():
        sys.exit(f"{pack} is not a cartridge pack (no manifest.json)")
    return pack, json.loads(mpath.read_text()), store.open_db(pack / "pack.db")


def cmd_build(a):
    out = Path(a.output)
    out.mkdir(parents=True, exist_ok=True)
    manifest = {"name": a.name or out.name, "version": 1, "llm_endpoint": a.llm_endpoint,
                "llm_model": None}
    (out / "manifest.json").write_text(json.dumps(manifest, indent=2))
    db = store.open_db(out / "pack.db")
    print(f"Building '{manifest['name']}'")
    if _ingest(db, a.sources) == 0:
        sys.exit("No usable sources: nothing was indexed, so no pack was built.")
    # make the pack self-contained: copy the (stdlib-only) code beside the data
    dst = out / "cartridge"
    if dst.exists():
        shutil.rmtree(dst)
    shutil.copytree(PKG, dst, ignore=shutil.ignore_patterns("__pycache__"))
    (out / "ask.sh").write_text(LAUNCH_SH)
    (out / "ask.sh").chmod(0o755)
    (out / "ask.bat").write_text(LAUNCH_BAT)
    (out / "ask.command").write_text(LAUNCH_SH)  # double-clickable on macOS
    (out / "ask.command").chmod(0o755)
    s, c = store.stats(db)
    print(f"Done: {s} sources, {c} passages -> {out}/  (copy this folder to a USB drive)")


def cmd_add(a):
    pack, _, db = _load(a.pack)
    _ingest(db, a.sources)
    print("Now: %d sources, %d passages" % store.stats(db))


def cmd_info(a):
    pack, m, db = _load(a.pack)
    print(f"{m['name']}: %d sources, %d passages" % store.stats(db))
    for name, kind in db.execute("SELECT name, kind FROM sources"):
        print(f"  {kind:4} {name}")


def _pick_model(m, name):
    models = m.get("models", {})
    if not models:
        return None, None
    name = name or m.get("default_model") or next(iter(models))
    if name not in models:
        sys.exit(f"Unknown model '{name}'. Available: {', '.join(models)}")
    return name, models[name]


def cmd_setup(a):
    pack, m, db = _load(a.pack)
    plats = (runtime.ALL_USB if a.platforms == "all"
             else [runtime.current_platform()] if a.platforms == "current"
             else a.platforms.split(","))
    bad = [p for p in plats if p not in runtime.ASSET_SUFFIX]
    if bad:
        sys.exit(f"Unknown platform(s) {bad}. Choose from {list(runtime.ASSET_SUFFIX)}")
    repo = a.model_repo or runtime.PRESETS.get(a.model)
    if not repo:
        sys.exit(f"Unknown model '{a.model}'. Presets: {list(runtime.PRESETS)}; or pass --model-repo owner/name")
    try:
        runtime.fetch_engine(pack, plats)
        rel = runtime.fetch_model(pack, repo, a.quant)
    except OSError as e:  # urllib.error.URLError / HTTPError are OSErrors
        sys.exit(f"Download failed: {e}\nThis step needs internet (github.com and huggingface.co). "
                 "Re-run to resume partial downloads.")
    m.setdefault("models", {})[a.model] = rel
    m.setdefault("default_model", a.model)
    m["llm_endpoint"] = None  # local engine takes over
    (pack / "manifest.json").write_text(json.dumps(m, indent=2))
    print(f"Ready. Try: python -m cartridge ask {a.pack} \"your question\" -m {a.model}")


def cmd_models(a):
    pack, m, _ = _load(a.pack)
    for k, v in m.get("models", {}).items():
        mark = "*" if k == m.get("default_model") else " "
        print(f" {mark} {k}: {v}")
    if not m.get("models"):
        print("No models yet. Run: python -m cartridge setup PACK --model smollm3")


def cmd_ask(a):
    pack, m, db = _load(a.pack)
    name, rel = _pick_model(m, a.model)
    srv = runtime.Server(pack, rel).wait() if rel else None
    ep = srv.endpoint if srv else None
    try:
        if a.question:
            print(answer(db, m, " ".join(a.question), endpoint=ep)[0])
            return
        print(f"{m['name']}" + (f" [{name}]" if name else "") + " - ask a question (blank line to quit)")
        while True:
            try:
                q = input("\n> ").strip()
            except EOFError:
                break
            if not q:
                break
            print(answer(db, m, q, endpoint=ep)[0])
    finally:
        if srv:
            srv.stop()


def cmd_compare(a):
    pack, m, db = _load(a.pack)
    qs = [l.strip() for l in Path(a.questions).read_text("utf8").splitlines() if l.strip() and not l.startswith("#")]
    names = [x for x in (a.model or "").split(",") if x] or list(m.get("models", {}))
    if not names:
        sys.exit("No models set up. Run `setup` first.")
    results = {q: {} for q in qs}
    load_s, ans_s = {}, {n: [] for n in names}
    for name in names:
        _, rel = _pick_model(m, name)
        t0 = time.time()
        srv = runtime.Server(pack, rel).wait()
        load_s[name] = time.time() - t0
        try:
            for q in qs:
                t1 = time.time()
                results[q][name] = answer(db, m, q, endpoint=srv.endpoint)[0]
                dt = time.time() - t1
                ans_s[name].append(dt)
                results[q][name] += f"\n_({dt:.1f}s)_"
        finally:
            srv.stop()
    out = ["## Timing"]
    for name in names:
        t = ans_s[name]
        out.append(f"- **{name}**: load {load_s[name]:.1f}s; {len(t)} answers, "
                   f"avg {sum(t) / len(t):.1f}s, max {max(t):.1f}s")
    out.append("")
    for q in qs:
        out.append(f"### {q}")
        for name in names:
            out.append(f"**{name}:** {results[q][name]}\n")
    text = "\n".join(out)
    Path(a.out).write_text(text, "utf8")
    print(text)
    print(f"\nSaved to {a.out}")


def main(argv=None):
    ap = argparse.ArgumentParser(prog="cartridge", description=__doc__,
                                 formatter_class=argparse.RawDescriptionHelpFormatter)
    sub = ap.add_subparsers(dest="cmd", required=True)
    b = sub.add_parser("build")
    b.add_argument("sources", nargs="+")
    b.add_argument("-o", "--output", required=True)
    b.add_argument("--name")
    b.add_argument("--llm-endpoint", help="OpenAI-compatible chat URL, e.g. http://localhost:8080/v1/chat/completions")
    b.set_defaults(fn=cmd_build)
    d = sub.add_parser("add")
    d.add_argument("pack")
    d.add_argument("sources", nargs="+")
    d.set_defaults(fn=cmd_add)
    i = sub.add_parser("info")
    i.add_argument("pack")
    i.set_defaults(fn=cmd_info)
    q = sub.add_parser("ask")
    q.add_argument("pack")
    q.add_argument("question", nargs="*")
    q.add_argument("-m", "--model")
    q.set_defaults(fn=cmd_ask)
    t = sub.add_parser("setup")
    t.add_argument("pack")
    t.add_argument("--model", default="smollm3", help="preset name (%s) or any label with --model-repo" % ", ".join(runtime.PRESETS))
    t.add_argument("--model-repo", help="Hugging Face GGUF repo, e.g. owner/name")
    t.add_argument("--quant", default="Q4_K_M")
    t.add_argument("--platforms", default="current", help="current | all | comma list: " + ",".join(runtime.ASSET_SUFFIX))
    t.set_defaults(fn=cmd_setup)
    ml = sub.add_parser("models")
    ml.add_argument("pack")
    ml.set_defaults(fn=cmd_models)
    c = sub.add_parser("compare")
    c.add_argument("pack")
    c.add_argument("questions")
    c.add_argument("-m", "--model", help="comma-separated model names (default: all set up)")
    c.add_argument("-o", "--out", default="compare.md")
    c.set_defaults(fn=cmd_compare)
    a = ap.parse_args(argv)
    a.fn(a)
