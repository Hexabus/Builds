"""Large-corpus retrieval test: the Django 6.1 documentation (~680 files, ~10k passages).

    python3 tests/fetch_django_docs.py            # once; downloads the pinned docs from PyPI
    python3 tests/test_django_questions.py        # builds a temp pack and checks every question
    python3 tests/test_django_questions.py --write-questions FILE   # plain question list for `compare`
"""
import sys
from pathlib import Path

HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE))
from retrieval_runner import run  # noqa: E402

XFAIL = set()  # known retrieval misses (none right now)

if __name__ == "__main__":
    sys.exit(run("Django docs", HERE / "data" / "django_docs", HERE / "django_questions.tsv",
                 "python3 tests/fetch_django_docs.py", XFAIL, sys.argv[1:]))
