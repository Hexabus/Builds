"""Engine + model management: fetch llama.cpp and a GGUF model into a pack, run them locally.

Pack layout after `cartridge setup`:
    engine/<platform>/llama-server[.exe]   (one folder per OS/CPU you chose)
    models/<file>.gguf
Everything is plain files, so the whole pack folder can sit on a USB drive.
"""
import atexit
import json
import os
import platform
import re
import shutil
import socket
import subprocess
import sys
import tarfile
import time
import urllib.request
import zipfile
from pathlib import Path

LLAMA_API = "https://api.github.com/repos/ggml-org/llama.cpp/releases/latest"

# platform key -> suffix of the official llama.cpp release asset (CPU builds, work everywhere)
ASSET_SUFFIX = {
    "win-x64": "bin-win-cpu-x64.zip",
    "win-arm64": "bin-win-cpu-arm64.zip",
    "linux-x64": "bin-ubuntu-x64.tar.gz",
    "linux-arm64": "bin-ubuntu-arm64.tar.gz",
    "mac-arm64": "bin-macos-arm64.tar.gz",
    "mac-x64": "bin-macos-x64.tar.gz",
}
ALL_USB = ["win-x64", "linux-x64", "mac-arm64", "mac-x64"]

# Short names -> Hugging Face GGUF repos. Anything else: pass --model-repo owner/name.
PRESETS = {
    "smollm3": "ggml-org/SmolLM3-3B-GGUF",
    "llama32-1b": "bartowski/Llama-3.2-1B-Instruct-GGUF",
}


def current_platform():
    osn = {"Windows": "win", "Linux": "linux", "Darwin": "mac"}.get(platform.system(), "linux")
    m = platform.machine().lower()
    arch = "arm64" if m in ("arm64", "aarch64") else "x64"
    return f"{osn}-{arch}"


def _get(url, accept_json=False):
    h = {"User-Agent": "cartridge/0.1"}
    if accept_json:
        h["Accept"] = "application/json"
    return urllib.request.urlopen(urllib.request.Request(url, headers=h), timeout=60)


def download(url, dest, label=""):
    dest = Path(dest)
    dest.parent.mkdir(parents=True, exist_ok=True)
    part = dest.with_name(dest.name + ".part")
    done = part.stat().st_size if part.exists() else 0
    req = urllib.request.Request(url, headers={"User-Agent": "cartridge/0.1",
                                               **({"Range": f"bytes={done}-"} if done else {})})
    with urllib.request.urlopen(req, timeout=60) as r:
        if done and r.status != 206:
            done = 0  # server ignored Range; start over
        total = int(r.headers.get("Content-Length", 0)) + done
        with open(part, "ab" if done else "wb") as f:
            got = done
            while True:
                buf = r.read(1 << 20)
                if not buf:
                    break
                f.write(buf)
                got += len(buf)
                if total:
                    print(f"\r  {label} {got / 1e6:,.0f}/{total / 1e6:,.0f} MB", end="", flush=True)
    print()
    part.replace(dest)


def _safe_extract(archive, dest):
    dest = Path(dest)
    dest.mkdir(parents=True, exist_ok=True)
    root = dest.resolve()
    if str(archive).endswith(".zip"):
        with zipfile.ZipFile(archive) as z:
            for n in z.namelist():
                if not (root / n).resolve().is_relative_to(root):
                    raise RuntimeError(f"unsafe path in archive: {n}")
            z.extractall(dest)
    else:
        with tarfile.open(archive) as t:
            for m in t.getmembers():
                if not (root / m.name).resolve().is_relative_to(root):
                    raise RuntimeError(f"unsafe path in archive: {m.name}")
            try:
                t.extractall(dest, filter="data")
            except TypeError:  # Python < 3.12
                t.extractall(dest)


def find_server(pack, plat=None):
    exe = "llama-server.exe" if (plat or current_platform()).startswith("win") else "llama-server"
    base = Path(pack) / "engine" / (plat or current_platform())
    for p in base.rglob(exe) if base.exists() else []:
        return p
    return None


def fetch_engine(pack, platforms):
    rel = json.load(_get(LLAMA_API, True))
    assets = {a["name"]: a["browser_download_url"] for a in rel.get("assets", [])}
    print(f"llama.cpp {rel.get('tag_name')}")
    for plat in platforms:
        if find_server(pack, plat):
            print(f"  engine for {plat}: already present")
            continue
        suffix = ASSET_SUFFIX[plat]
        name = next((n for n in assets if n.endswith(suffix) and "cudart" not in n), None)
        if not name:
            sys.exit(f"No release asset ending in '{suffix}'. Assets: {sorted(assets)[:40]}")
        tmp = Path(pack) / "engine" / f".{name}"
        download(assets[name], tmp, f"engine {plat}")
        _safe_extract(tmp, Path(pack) / "engine" / plat)
        tmp.unlink()
        srv = find_server(pack, plat)
        if srv and not plat.startswith("win"):
            for f in srv.parent.iterdir():
                if f.is_file() and not f.suffix:
                    f.chmod(0o755)


def fetch_model(pack, model_repo, quant="Q4_K_M"):
    info = json.load(_get(f"https://huggingface.co/api/models/{model_repo}", True))
    files = [s["rfilename"] for s in info.get("siblings", []) if s["rfilename"].endswith(".gguf")]
    cands = [f for f in files if "mmproj" not in f.lower() and not re.search(r"-0000\d-of-", f)]
    pick = next((f for f in cands if quant.lower() in f.lower()), None)
    if not pick:
        sys.exit(f"No {quant} .gguf in {model_repo}. Files: {cands}")
    dest = Path(pack) / "models" / Path(pick).name
    if dest.exists():
        print(f"  model already present: {dest.name}")
    else:
        download(f"https://huggingface.co/{model_repo}/resolve/main/{pick}", dest, dest.name)
    return f"models/{dest.name}"


# ---------------------------------------------------------------- running

class Server:
    """Starts llama-server on a free local port; stops it on exit."""

    def __init__(self, pack, model_rel, ctx=4096):
        self.exe = find_server(pack)
        if not self.exe:
            sys.exit(f"No engine for this computer ({current_platform()}) in {pack}/engine. "
                     f"Run: python -m cartridge setup {pack} --platforms current")
        model = Path(pack) / model_rel
        if not model.exists():
            sys.exit(f"Model file missing: {model}")
        s = socket.socket()
        s.bind(("127.0.0.1", 0))
        self.port = s.getsockname()[1]
        s.close()
        flags = subprocess.CREATE_NO_WINDOW if os.name == "nt" else 0
        self.proc = subprocess.Popen(
            [str(self.exe), "-m", str(model), "--host", "127.0.0.1", "--port", str(self.port),
             "-c", str(ctx), "-t", str(max(os.cpu_count() or 2, 2))],
            cwd=self.exe.parent, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL,
            creationflags=flags)
        atexit.register(self.stop)
        self.endpoint = f"http://127.0.0.1:{self.port}/v1/chat/completions"

    def wait(self, timeout=240):
        print("Loading model…", end="", flush=True)
        t0 = time.time()
        while time.time() - t0 < timeout:
            if self.proc.poll() is not None:
                sys.exit("\nModel server exited early (not enough RAM, or incompatible CPU?).")
            try:
                with urllib.request.urlopen(f"http://127.0.0.1:{self.port}/health", timeout=2) as r:
                    if r.status == 200:
                        print(" ready.")
                        return self
            except Exception:
                time.sleep(1)
                print(".", end="", flush=True)
        self.stop()
        sys.exit("\nTimed out waiting for the model to load.")

    def stop(self):
        if self.proc and self.proc.poll() is None:
            self.proc.terminate()
            try:
                self.proc.wait(timeout=5)
            except Exception:
                self.proc.kill()
