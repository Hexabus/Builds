"""Prose retrieval test: the full text of Moby-Dick (1.3 MB of 19th-century narrative, ~1,800 passages).

    python3 tests/fetch_moby_dick.py              # once; clones the public-domain text
    python3 tests/test_moby_questions.py          # builds a temp pack and checks every question
    python3 tests/test_moby_questions.py --write-questions FILE   # plain question list for `compare`
"""
import sys
from pathlib import Path

HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE))
from retrieval_runner import run  # noqa: E402

# Known retrieval misses on this corpus (see CLAUDE.md): both are vocabulary gaps that keyword search cannot bridge.
#  - "artificial leg": the book says "ivory leg ... fashioned from the polished bone", and the rare word "artificial"
#    (8 passages, none relevant) outweighs everything else in the question.
#  - the Parsee: the answering passages never repeat the question's other words ("name", "boat", "crew") closely enough.
XFAIL = {
    "what is Ahab's artificial leg made from",
    "what is the name of the Parsee in Ahab's boat crew",
}

if __name__ == "__main__":
    sys.exit(run("Moby-Dick", HERE / "data" / "moby_dick" / "moby_dick.txt", HERE / "moby_questions.tsv",
                 "python3 tests/fetch_moby_dick.py", XFAIL, sys.argv[1:]))
