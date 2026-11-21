"""Download the Django documentation (BSD licensed) for large-corpus retrieval tests. Stdlib only.

    python3 tests/fetch_django_docs.py            ->  tests/data/django_docs/  (about 680 .txt files, 6.5 MB)

Fetches the pinned Django source release from PyPI and keeps only its docs/ folder. The text is not
committed (tests/data/ is gitignored); the version is pinned so the question answer keys stay valid.
"""
import io
import json
import sys
import tarfile
import urllib.request
from pathlib import Path

VERSION = "6.1.3"
DEST = Path(__file__).resolve().parent / "data" / "django_docs"


def main():
    if DEST.exists() and any(DEST.rglob("*.txt")):
        print(f"already present: {DEST}")
        return 0
    meta = json.load(urllib.request.urlopen(f"https://pypi.org/pypi/django/{VERSION}/json", timeout=60))
    url = next(u["url"] for u in meta["urls"] if u["packagetype"] == "sdist")
    print(f"downloading {url}")
    blob = urllib.request.urlopen(url, timeout=300).read()
    n = 0
    with tarfile.open(fileobj=io.BytesIO(blob)) as t:
        for m in t.getmembers():
            parts = Path(m.name).parts  # django-X.Y.Z/docs/...
            if len(parts) < 3 or parts[1] != "docs" or not m.isfile() or not m.name.endswith((".txt", ".rst")):
                continue
            rel = Path(*parts[2:])
            if ".." in rel.parts:
                continue
            out = DEST / rel
            out.parent.mkdir(parents=True, exist_ok=True)
            out.write_bytes(t.extractfile(m).read())
            n += 1
    print(f"wrote {n} files to {DEST}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
