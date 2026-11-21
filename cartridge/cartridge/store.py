"""SQLite FTS5 knowledge store. One file = one knowledge pack. Pure stdlib."""
import re
import sqlite3

SCHEMA = """
CREATE TABLE IF NOT EXISTS sources(
    id INTEGER PRIMARY KEY, name TEXT, kind TEXT, added TEXT DEFAULT CURRENT_TIMESTAMP);
CREATE VIRTUAL TABLE IF NOT EXISTS chunks USING fts5(
    text, source_id UNINDEXED, loc UNINDEXED, tokenize='porter unicode61');
"""

STOP = set("a an and are as at be by for from has have how i in is it of on or that the this to was what when where which who why will with you your do does can".split())


def open_db(path):
    db = sqlite3.connect(path)
    db.executescript(SCHEMA)
    return db


def add_source(db, name, kind, chunks):
    cur = db.execute("INSERT INTO sources(name, kind) VALUES(?,?)", (name, kind))
    sid = cur.lastrowid
    db.executemany(
        "INSERT INTO chunks(text, source_id, loc) VALUES(?,?,?)",
        [(text, sid, loc) for loc, text in chunks],
    )
    db.commit()
    return len(chunks)


def _terms(q):
    return [w for w in re.findall(r"[A-Za-z0-9]+", q.lower()) if w not in STOP and len(w) > 1]


def _query(q):
    return " OR ".join(f'"{w}"' for w in _terms(q))


def _stem(w):
    return re.sub(r"(ing|ed|es|s)$", "", w) if len(w) > 4 else w


def _coverage(terms, text):
    """Fraction of distinct query terms that appear in the passage (crude stem match)."""
    words = {_stem(w) for w in re.findall(r"[a-z0-9]+", text.lower())}
    uniq = set(terms)
    return sum(1 for t in uniq if _stem(t) in words) / len(uniq)


def search(db, question, k=4):
    """Return [(coverage, source_name, loc, text)], best first.

    Terms found in >30% of passages (e.g. "leave" in a rulebook about leave) carry no signal, so
    they are dropped from matching when other terms remain. Passages are ranked by the
    IDF-weighted share of the question's terms they contain; BM25 breaks ties.
    coverage (0..1) is that weighted share, used by the caller to decide "not in my files".
    """
    import math
    terms = list(dict.fromkeys(_terms(question)))
    if not terms:
        return []
    total = db.execute("SELECT COUNT(*) FROM chunks").fetchone()[0] or 1
    df = {t: db.execute("SELECT COUNT(*) FROM chunks WHERE chunks MATCH ?", (f'"{t}"',)).fetchone()[0]
          for t in terms}
    keep = [t for t in terms if df[t] / total <= 0.30] or terms
    idf = {t: math.log(1 + total / (1 + df[t])) for t in keep}
    fq = " OR ".join(f'"{t}"' for t in keep)
    rows = db.execute(
        """SELECT s.name, c.loc, c.text, bm25(chunks)
           FROM chunks c JOIN sources s ON s.id = c.source_id
           WHERE chunks MATCH ? ORDER BY bm25(chunks) LIMIT 60""",
        (fq,),
    ).fetchall()
    denom = sum(idf.values()) or 1
    scored = []
    for name, loc, text, bm in rows:
        words = {_stem(w) for w in re.findall(r"[a-z0-9]+", text.lower())}
        cov = sum(idf[t] for t in keep if _stem(t) in words) / denom
        scored.append((cov, -bm, name, loc, text))
    scored.sort(reverse=True)
    return [(c, n, l, t) for c, _, n, l, t in scored[:k]]


def stats(db):
    n_s = db.execute("SELECT COUNT(*) FROM sources").fetchone()[0]
    n_c = db.execute("SELECT COUNT(*) FROM chunks").fetchone()[0]
    return n_s, n_c
