"""Download the full text of Moby-Dick (Project Gutenberg #2701, public domain) for a prose retrieval test.

    python3 tests/fetch_moby_dick.py          ->  tests/data/moby_dick/moby_dick.txt  (1.3 MB, 135 chapters + epilogue)

Clones the GITenberg mirror of the book with git (shallow) and keeps only the UTF-8 text file. The text is not
committed (tests/data/ is gitignored).
"""
import shutil
import subprocess
import sys
import tempfile
from pathlib import Path

REPO = "https://github.com/GITenberg/Moby-Dick--Or-The-Whale_2701"
DEST = Path(__file__).resolve().parent / "data" / "moby_dick" / "moby_dick.txt"


def main():
    if DEST.exists():
        print(f"already present: {DEST}")
        return 0
    with tempfile.TemporaryDirectory() as tmp:
        subprocess.run(["git", "clone", "-q", "--depth", "1", REPO, tmp + "/src"], check=True,
                       env={**__import__("os").environ, "GIT_LFS_SKIP_SMUDGE": "1"})
        DEST.parent.mkdir(parents=True, exist_ok=True)
        text = (Path(tmp) / "src" / "2701-0.txt").read_text("utf-8-sig")
        DEST.write_text(text, "utf-8")
    print(f"wrote {DEST} ({DEST.stat().st_size / 1e6:.1f} MB)")
    return 0


if __name__ == "__main__":
    sys.exit(main())
