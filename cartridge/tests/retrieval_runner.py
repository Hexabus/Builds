"""Shared retrieval-test runner for the large-document tests (Django docs, Moby-Dick).

A question file is TSV: question <TAB> regex that must appear in a correct passage <TAB> expected answer.
A question passes if a passage matching its regex is in the top 4 hits. An empty regex means the question is
out of scope and must be rejected ("Not in my files."). XFAIL entries are reported but do not fail the run;
one that starts passing is reported as XPASS.
"""
import re
import sys
import tempfile
import time
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))
from cartridge import ask, cli, store  # noqa: E402


def load(tsv):
    rows = []
    for line in Path(tsv).read_text("utf8").splitlines():
        if line.strip() and not line.startswith("#"):
            q, pat, ans = line.split("\t")
            rows.append((q, pat, ans))
    return rows


def run(name, docs, tsv, fetch_hint, xfail=frozenset(), argv=()):
    rows = load(tsv)
    if "--write-questions" in argv:
        Path(argv[list(argv).index("--write-questions") + 1]).write_text(
            f"# {name} questions (generated from {Path(tsv).name})\n" + "\n".join(q for q, _, _ in rows) + "\n", "utf8")
        return 0
    if not Path(docs).exists():
        sys.exit(f"Document missing. Run: {fetch_hint}")
    with tempfile.TemporaryDirectory() as tmp:
        pack = Path(tmp) / "pack"
        t0 = time.time()
        cli.main(["build", str(docs), "-o", str(pack), "--name", name])
        print(f"build: {time.time() - t0:.1f}s")
        db = store.open_db(pack / "pack.db")
        ok1 = ok4 = bad = 0
        n_pos = sum(1 for _, p, _ in rows if p)
        for q, pat, ans in rows:
            hits = [h for h in store.search(db, q, k=4) if h[0] >= ask.MIN_COVERAGE]
            if not pat:  # out of scope: nothing should survive the coverage gate
                status = "ok" if not hits else "FAIL"
                bad += status == "FAIL"
                print(f"{'-':>2} | {status:5} | {q}" + ("" if not hits else f"   (got {hits[0][1]} {hits[0][2]})"))
                continue
            rank = next((i + 1 for i, h in enumerate(hits) if re.search(pat, h[3], re.S | re.I)), None)
            ok1 += rank == 1
            ok4 += bool(rank)
            xf = q in xfail
            status = ("ok" if rank and not xf else "xfail" if not rank and xf
                      else "XPASS (remove from XFAIL)" if rank and xf else "FAIL")
            bad += status == "FAIL"
            print(f"{rank or '-':>2} | {status:5} | {q}")
        print(f"top1 {ok1}/{n_pos}  in-top4 {ok4}/{n_pos}  failures {bad}")
        return 1 if bad else 0
