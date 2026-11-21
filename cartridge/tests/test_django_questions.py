"""Large-corpus retrieval test: the Django 6.1 documentation (~680 files, ~10k passages).

    python3 tests/fetch_django_docs.py            # once; downloads the pinned docs from PyPI
    python3 tests/test_django_questions.py        # builds a temp pack and checks every question
    python3 tests/test_django_questions.py --write-questions FILE   # plain question list for `compare`

Questions, check patterns and expected answers live in django_questions.tsv. A question passes if a
passage matching its pattern is in the top 4 hits. Questions with an empty pattern must be rejected
("Not in my files."). Exit code 0 = no question failed (XFAIL entries are reported, not counted).
"""
import re
import sys
import tempfile
import time
from pathlib import Path

HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE.parent))
from cartridge import ask, cli, store  # noqa: E402

DOCS = HERE / "data" / "django_docs"
# Known retrieval misses on this corpus (see CLAUDE.md):
#  - TIME_ZONE: "time zone" is an everyday phrase in these docs, so 170 passages match; the one that defines the
#    setting ranks about 10th even after preferring passages that spell the identifier literally.
#  - three fetch modes: the passage that lists FETCH_RAISE does not mention "6.1", so the version filter hides it
#    and the question's words ("three", "fetch", "modes") are too common to single it out.
XFAIL = {
    "what is the default value of the TIME_ZONE setting",
    "what are the three fetch modes in Django 6.1",
}


def load():
    rows = []
    for line in (HERE / "django_questions.tsv").read_text("utf8").splitlines():
        if line.strip() and not line.startswith("#"):
            q, pat, ans = line.split("\t")
            rows.append((q, pat, ans))
    return rows


def main():
    rows = load()
    if "--write-questions" in sys.argv:
        Path(sys.argv[sys.argv.index("--write-questions") + 1]).write_text(
            "# Django 6.1 docs questions (generated from django_questions.tsv)\n" + "\n".join(q for q, _, _ in rows) + "\n", "utf8")
        return 0
    if not DOCS.exists():
        sys.exit("Docs missing. Run: python3 tests/fetch_django_docs.py")
    with tempfile.TemporaryDirectory() as tmp:
        pack = Path(tmp) / "pack"
        t0 = time.time()
        cli.main(["build", str(DOCS), "-o", str(pack), "--name", "Django docs"])
        print(f"build: {time.time() - t0:.1f}s")
        db = store.open_db(pack / "pack.db")
        ok1 = ok4 = bad = 0
        n_pos = sum(1 for _, p, _ in rows if p)
        for q, pat, ans in rows:
            hits = [h for h in store.search(db, q, k=4) if h[0] >= ask.MIN_COVERAGE]
            if not pat:  # out-of-scope: nothing should survive the coverage gate
                status = "ok" if not hits else "FAIL"
                bad += status == "FAIL"
                print(f"{'-':>2} | {status:5} | {q}" + ("" if not hits else f"   (got {hits[0][1]} {hits[0][2]})"))
                continue
            rank = next((i + 1 for i, h in enumerate(hits) if re.search(pat, h[3], re.S | re.I)), None)
            ok1 += rank == 1
            ok4 += bool(rank)
            xf = q in XFAIL
            status = ("ok" if rank and not xf else "xfail" if not rank and xf
                      else "XPASS (remove from XFAIL)" if rank and xf else "FAIL")
            bad += status == "FAIL"
            print(f"{rank or '-':>2} | {status:5} | {q}")
        print(f"top1 {ok1}/{n_pos}  in-top4 {ok4}/{n_pos}  failures {bad}")
        return 1 if bad else 0


if __name__ == "__main__":
    sys.exit(main())
