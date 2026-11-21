"""Turn files and URLs into (location, text) chunks. Stdlib only; PDF needs optional pypdf."""
import re
import zipfile
from html.parser import HTMLParser
from pathlib import Path
from urllib.request import Request, urlopen

TEXT_EXT = {".txt", ".md", ".markdown", ".csv", ".log", ".json", ".rst"}


class _HTMLText(HTMLParser):
    SKIP = {"script", "style", "nav", "footer", "noscript", "svg"}

    def __init__(self):
        super().__init__()
        self.parts, self._skip = [], 0

    def handle_starttag(self, tag, attrs):
        if tag in self.SKIP:
            self._skip += 1
        elif tag in {"p", "div", "br", "li", "h1", "h2", "h3", "h4", "tr"}:
            self.parts.append("\n")

    def handle_endtag(self, tag):
        if tag in self.SKIP and self._skip:
            self._skip -= 1

    def handle_data(self, data):
        if not self._skip:
            self.parts.append(data)


def html_to_text(html):
    p = _HTMLText()
    p.feed(html)
    return re.sub(r"\n\s*\n+", "\n\n", "".join(p.parts)).strip()


def read_docx(path):
    with zipfile.ZipFile(path) as z:
        xml = z.read("word/document.xml").decode("utf8", "ignore")
    xml = re.sub(r"</w:p>", "\n\n", xml)
    return re.sub(r"<[^>]+>", "", xml)


def read_pdf(path):
    try:
        from pypdf import PdfReader
    except ImportError:
        raise RuntimeError("PDF support needs: pip install pypdf")
    pages = []
    for i, page in enumerate(PdfReader(str(path)).pages, 1):
        pages.append((f"p.{i}", page.extract_text() or ""))
    return pages


_ITEM = re.compile(r"(?:\d+[.)]|[-*•]|\(?[A-Za-z][.)])\s")  # "1. ", "- ", "a) "


def _paragraphs(text, limit):
    """Paragraphs, with a list kept in one piece together with the line that introduces it.

    "Django provides three modes:" followed by items 1., 2., 3. (and their indented continuation
    paragraphs) becomes one block, so a chunk boundary cannot cut the list after item 2. Blocks are
    capped at `limit` characters; a longer list is split as before.
    """
    blocks, open_list = [], False
    for raw in re.split(r"\n\s*\n", text):
        p = raw.strip()
        if not p:
            continue
        item, cont = bool(_ITEM.match(p)), raw[:1].isspace()
        if blocks and open_list and (item or cont) and len(blocks[-1]) + len(p) + 2 <= limit:
            blocks[-1] += "\n\n" + p
        else:
            blocks.append(p)
            open_list = p.endswith(":") or item
    return blocks


def chunk(text, loc_prefix="", size=900, overlap=150):
    """Split on paragraphs, pack to ~size chars, carry a little overlap."""
    paras = _paragraphs(text, size * 1.5)
    chunks, buf, n = [], "", 1
    for p in paras:
        while len(p) > size * 1.5:  # very long paragraph: hard split
            cut = p.rfind(". ", 0, size) + 1 or size
            chunks.append(p[:cut].strip())
            p = p[max(cut - overlap, 0):] if cut > overlap else p[cut:]
        if buf and len(buf) + len(p) > size:
            chunks.append(buf)
            buf = buf[-overlap:] + "\n\n" + p
        else:
            buf = (buf + "\n\n" + p) if buf else p
    if buf:
        chunks.append(buf)
    return [(f"{loc_prefix}#{i}".lstrip("#") if not loc_prefix else f"{loc_prefix} §{i}", c)
            for i, c in enumerate(chunks, 1) if len(c.strip()) > 20]


def load_file(path):
    """Return list of (loc, text) chunks for a file, or None if unsupported."""
    path = Path(path)
    ext = path.suffix.lower()
    if ext in TEXT_EXT:
        return chunk(path.read_text("utf8", "ignore"))
    if ext in {".html", ".htm"}:
        return chunk(html_to_text(path.read_text("utf8", "ignore")))
    if ext == ".docx":
        return chunk(read_docx(path))
    if ext == ".pdf":
        out = []
        for loc, text in read_pdf(path):
            out += chunk(text, loc)
        return out
    return None


def load_url(url):
    req = Request(url, headers={"User-Agent": "cartridge/0.1"})
    with urlopen(req, timeout=30) as r:
        raw = r.read().decode(r.headers.get_content_charset() or "utf8", "ignore")
    ctype = r.headers.get_content_type()
    text = html_to_text(raw) if "html" in ctype else raw
    return chunk(text)
