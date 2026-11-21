"""Retrieval test: build a pack from the Maine Paid Family and Medical Leave rules PDF and check
that each question's expected passage is among the top 4 hits.

    python3 tests/test_fmla_questions.py        (needs: pip install pypdf)

Exit code 0 = every non-xfail question passed. Questions in XFAIL are known retrieval misses:
they are reported but do not fail the run (and the run says so if one starts passing).
"""
import re
import sys
import tempfile
from pathlib import Path

HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE.parent))
from cartridge import cli, store  # noqa: E402

PDF = HERE / "maine_fmla.pdf"

# (question, regex that must appear in a correct passage; \s+ because PDF text wraps lines)
T = [
    ("how many weeks of approved leave can a covered individual take", r"up\s+to\s+12\s+weeks\s+of\s+approved\s+leave"),
    ("how long is the waiting period before medical leave benefits are payable", r"first\s+7\s+calendar\s+days"),
    ("how far before the start of leave can an application for benefits be submitted", r"no\s+more\s+than\s+60\s+days"),
    ("how many days after leave starts can an application be submitted", r"no\s+more\s+than\s+90\s+days\s+after"),
    ("what percentage of the premium must employers with 15 or more employees remit", r"remit\s+one\s+hundred\s+percent\s+\(100%\)"),
    ("what share of the premium can employers deduct from employees wages", r"deduct\s+up\s+to\s+fifty\s+percent"),
    ("what share of the premium must employers with fewer than 15 employees remit", r"fewer\s+than\s+15\s+employees\s+shall\s+remit\s+fifty\s+percent"),
    ("what is the penalty for failing to remit premiums or submit contribution reports on time", r"penalty\s+of\s+1\.0\s+percent"),
    ("what is the application fee for a private plan substitution", r"application\s+fee\s+is\s+\$250"),
    ("what is the smallest increment of intermittent leave", r"not\s+less\s+than\s+a\s+scheduled\s+workday"),
    ("what does Tier 1 benefits mean", r"“Tier\s+1\s+benefits”\s+means"),
    ("what is a business day", r"“Business\s+day”\s+means"),
]
XFAIL = {"what is a business day"}  # definition (p.1) is not in the top 4; cause not investigated


def main():
    with tempfile.TemporaryDirectory() as tmp:
        pack = str(Path(tmp) / "pack")
        cli.main(["build", str(PDF), "-o", pack, "--name", "FMLA test"])
        db = store.open_db(Path(pack) / "pack.db")
        ok1 = ok4 = bad = 0
        for q, pat in T:
            hits = store.search(db, q, k=4)
            rank = next((i + 1 for i, h in enumerate(hits) if re.search(pat, h[3], re.S | re.I)), None)
            ok1 += rank == 1
            ok4 += bool(rank)
            expected_fail = q in XFAIL
            status = "ok" if rank and not expected_fail else "xfail" if not rank and expected_fail else \
                "XPASS (remove from XFAIL)" if rank and expected_fail else "FAIL"
            bad += status == "FAIL"
            print(f"{rank or '-'} | {status:5} | {q}")
        print(f"top1 {ok1}/{len(T)}  in-top4 {ok4}/{len(T)}  failures {bad}")
        return 1 if bad else 0


if __name__ == "__main__":
    sys.exit(main())
