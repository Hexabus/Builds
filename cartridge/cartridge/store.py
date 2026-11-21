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


# --- exact-match signals -------------------------------------------------------------------------
# Plain keyword search loses three kinds of question: ones naming an identifier (SESSION_COOKIE_AGE is
# split into common words), ones naming a version ("6.1": one-character tokens are discarded), and
# "what is X" questions, where a passage that merely repeats X outranks the one that defines it.
_IDENT = re.compile(r"\b[A-Za-z0-9]+(?:_[A-Za-z0-9]+)+\b")  # SESSION_COOKIE_AGE, FETCH_PEERS
_VERSION = re.compile(r"\b\d+(?:\.\d+)+\b")  # 6.1, 3.12
_DEFINE = re.compile(r"^\s*(?:what\s+(?:is|are|does)|define|meaning\s+of)\s+(?:an?\s+|the\s+)?"
                     r"(?P<subj>.+?)\s*(?:\bmeans?\b)?\??\s*$", re.I)


def _phrase(words):
    return '"' + " ".join(words) + '"'


def _fetch(db, match, limit, restrict=None):
    """Passages matching an FTS expression, best BM25 first. `restrict` = FTS phrase every hit must contain."""
    sql = """SELECT s.name, c.loc, c.text FROM chunks c JOIN sources s ON s.id = c.source_id
             WHERE chunks MATCH ?"""
    args = [match]
    if restrict:
        sql += " AND c.rowid IN (SELECT rowid FROM chunks WHERE chunks MATCH ?)"
        args.append(restrict)
    try:
        return db.execute(sql + " ORDER BY bm25(chunks) LIMIT ?", (*args, limit)).fetchall()
    except sqlite3.OperationalError:  # malformed FTS expression: just skip this signal
        return []


def _exact_hits(db, question, keep, limit=20):
    """Passages that match the question's identifiers, versions or definition subject exactly.

    Order: definitions of the asked-about term, then passages containing the question's identifier(s),
    then passages containing its version number(s) together with its other key terms.
    """
    hits = []
    idents = [_phrase(re.findall(r"[A-Za-z0-9]+", m.group(0).lower())) for m in _IDENT.finditer(question)]
    m = _DEFINE.match(question)
    if m and not idents:
        words = re.findall(r"[A-Za-z0-9]+", m.group("subj"))
        if 0 < len(words) <= 4:
            w = r"\s+".join(re.escape(x) for x in words)
            # "X" means ... (legal/rule style)   or   glossary style:  X<newline>    Definition...
            pat = re.compile(r"[“\"]\s*" + w + r"s?\s*[”\"]\s+(?:means|has)|^\s*" + w + r"\s*\n\s+[A-Z]", re.I | re.M)
            hits += [r for r in _fetch(db, _phrase([x.lower() for x in words]), 2000) if pat.search(r[2])][:limit]
    if idents:  # the identifier is a strong signal on its own; other terms only rank within its matches
        ph = " AND ".join(idents)
        found = _fetch(db, " OR ".join([ph] + [f'"{t}"' for t in keep]), 200, restrict=ph)
        # FTS sees "TIME_ZONE" as the words "time zone"; passages that spell the identifier literally win
        lits = [m.group(0) for m in _IDENT.finditer(question)]
        found.sort(key=lambda r: not all(l in r[2] for l in lits))  # stable: BM25 order kept within groups
        hits += found[:limit]
    versions = [_phrase(v.group(0).split(".")) for v in _VERSION.finditer(question)]
    if versions and keep:  # a version number alone is weak; require another key term too
        hits += _fetch(db, " AND ".join(versions) + " AND (" + " OR ".join(f'"{t}"' for t in keep) + ")", limit)
    return hits


def search(db, question, k=4):
    """Return [(coverage, source_name, loc, text)], best first.

    Exact matches on identifiers, version numbers and "what is X" definitions (see _exact_hits)
    come first, followed by the keyword ranking of _keyword_search. They get coverage 1.0.
    """
    base = _keyword_search(db, question, 60)
    terms = list(dict.fromkeys(_terms(question)))
    keep = terms
    if terms:
        total = db.execute("SELECT COUNT(*) FROM chunks").fetchone()[0] or 1
        keep = [t for t in terms
                if db.execute("SELECT COUNT(*) FROM chunks WHERE chunks MATCH ?", (f'"{t}"',)).fetchone()[0] / total <= 0.30] or terms
    out, seen = [], set()
    for name, loc, text in _exact_hits(db, question, keep):
        if (name, loc) not in seen:
            seen.add((name, loc))
            out.append((1.0, name, loc, text))
    for h in base:
        if (h[1], h[2]) not in seen:
            seen.add((h[1], h[2]))
            out.append(h)
    return out[:k]


def _keyword_search(db, question, k=4):
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
