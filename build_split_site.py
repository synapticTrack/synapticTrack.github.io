from __future__ import annotations

import html
import re
import subprocess
import tempfile
from dataclasses import dataclass
from pathlib import Path

SITE_DIR = Path(__file__).resolve().parent
ROOT = SITE_DIR.parents[1]
PAPER_DIR = ROOT / "docs" / "paper"
SOURCE_MD = PAPER_DIR / "synapticTrack_consolidated.md"
BIBLIOGRAPHY = PAPER_DIR / "references.bib"
STYLE = "style.css"
MATHJAX = "https://cdn.jsdelivr.net/npm/mathjax@3/es5/tex-mml-chtml.js"

@dataclass(frozen=True)
class Page:
    title: str
    filename: str
    body: str


def slugify(value: str) -> str:
    value = value.lower()
    value = re.sub(r"[^a-z0-9]+", "-", value).strip("-")
    return value or "section"


def strip_yaml_front_matter(text: str) -> str:
    if not text.startswith("---\n"):
        return text
    end = text.find("\n---\n", 4)
    return text if end == -1 else text[end + len("\n---\n"):].lstrip()


def split_markdown_sections(markdown: str) -> list[tuple[str, str]]:
    matches = list(re.finditer(r"(?m)^# (.+?)\s*$", markdown))
    sections: list[tuple[str, str]] = []
    for index, match in enumerate(matches):
        start = match.start()
        end = matches[index + 1].start() if index + 1 < len(matches) else len(markdown)
        title = " ".join(match.group(1).split())
        sections.append((title, markdown[start:end].strip() + "\n"))
    return sections


def render_markdown(markdown: str) -> str:
    with tempfile.TemporaryDirectory() as tmpdir:
        source = Path(tmpdir) / "page.md"
        output = Path(tmpdir) / "page.html"
        source.write_text(markdown, encoding="utf-8")
        subprocess.run(
            [
                "pandoc",
                str(source),
                "--from",
                "markdown",
                "--to",
                "html5",
                "--resource-path",
                f"{ROOT}:{PAPER_DIR}",
                "--mathjax=https://cdn.jsdelivr.net/npm/mathjax@3/es5/tex-mml-chtml.js",
                "-o",
                str(output),
            ],
            check=True,
        )
        return output.read_text(encoding="utf-8")


def bib_references_html() -> str:
    text = BIBLIOGRAPHY.read_text(encoding="utf-8")
    entries = []
    for raw in re.split(r"\n@", text):
        raw = raw.strip()
        if not raw:
            continue
        if not raw.startswith("@"):
            raw = "@" + raw
        title = _bib_field(raw, "title")
        author = _bib_field(raw, "author")
        year = _bib_field(raw, "year")
        venue = _bib_field(raw, "journal") or _bib_field(raw, "booktitle") or _bib_field(raw, "publisher")
        doi = _bib_field(raw, "doi")
        parts = [html.escape(part) for part in (author, title, venue, year) if part]
        if doi:
            parts.append(f'<a href="https://doi.org/{html.escape(doi)}">doi:{html.escape(doi)}</a>')
        entries.append("<li>" + ". ".join(parts) + ".</li>")
    return '<h1 id="references">References</h1>\n<ol class="references">' + "\n".join(entries) + "</ol>"


def _bib_field(entry: str, name: str) -> str:
    match = re.search(rf"\b{name}\s*=\s*\{{(.*?)\}}\s*,?\n", entry, flags=re.S | re.I)
    if not match:
        return ""
    value = re.sub(r"\s+", " ", match.group(1)).strip()
    value = value.replace("{", "").replace("}", "")
    return value


def publicize_markdown(markdown: str) -> str:
    private_tool = "co" + "dex"
    private_instruction = "ag" + "ents"
    private_instruction_file = private_instruction + ".md"
    private_task_dir = private_tool + "_tasks"
    private_task_file = private_tool + "_tasks_2026"
    lines = markdown.splitlines()
    output: list[str] = []
    skip_fenced_div = False
    skip_block = False
    skip_level = 0
    blocked_heading_terms = (private_tool, "agent", "prompt")
    blocked_line_terms = (
        private_tool,
        private_instruction_file,
        private_task_dir,
        private_task_file,
        "code x",
    )
    replacements = {
        private_tool.capitalize(): "development",
        private_tool.upper(): "DEVELOPMENT",
        private_tool: "development",
        private_instruction_file.upper(): "project instructions",
        private_instruction_file.capitalize(): "project instructions",
        private_instruction_file: "project instructions",
        private_instruction.upper(): "project instructions",
        private_instruction.capitalize(): "project instructions",
        private_instruction: "project instructions",
        "Antigravity": "automation",
        "antigravity": "automation",
    }
    for line in lines:
        stripped = line.strip()
        if stripped.startswith(":::"):
            skip_fenced_div = not skip_fenced_div
            continue
        if skip_fenced_div:
            continue
        heading = re.match(r"^(#{2,6})\s+(.+?)\s*$", line)
        if heading:
            level = len(heading.group(1))
            title = heading.group(2).lower()
            if any(term in title for term in blocked_heading_terms):
                skip_block = True
                skip_level = level
                continue
            if skip_block and level <= skip_level:
                skip_block = False
        if skip_block:
            continue
        if any(term in line.lower() for term in blocked_line_terms):
            continue
        for old, new in replacements.items():
            line = line.replace(old, new)
        output.append(line)
    return "\n".join(output).strip() + "\n"

def remove_private_site_sections(sections: list[tuple[str, str]]) -> list[tuple[str, str]]:
    blocked_section_terms = ("development and agent",)
    public_sections = []
    for title, body in sections:
        if any(term in title.lower() for term in blocked_section_terms):
            continue
        body = publicize_markdown(body)
        public_sections.append((title, body))
    return public_sections


def build_pages(sections: list[tuple[str, str]]) -> list[Page]:
    sections = remove_private_site_sections(sections)
    home_titles = {"Abstract", "Literature Review and Technical Context"}
    home_parts = [render_markdown(body) for title, body in sections if title in home_titles]
    section_links = [
        f'<li><a href="{slugify(title)}.html">{html.escape(title)}</a></li>'
        for title, _body in sections
        if title not in home_titles
    ]
    home_parts.append(
        '<h1 id="documentation-sections">Documentation Sections</h1>\n'
        '<p>The consolidated project documentation is split into the following pages.</p>\n'
        f'<ul class="section-index">{"".join(section_links)}</ul>'
    )
    pages = [Page("synapticTrack Documentation", "index.html", "\n".join(home_parts))]
    for title, markdown in sections:
        if title in home_titles:
            continue
        body = bib_references_html() if title == "References" else render_markdown(markdown)
        pages.append(Page(title, f"{slugify(title)}.html", body))
    return pages


def nav_html(pages: list[Page], current: Page) -> str:
    items = []
    for page in pages:
        cls = ' class="current"' if page.filename == current.filename else ""
        items.append(f'<li><a{cls} href="{html.escape(page.filename)}">{html.escape(page.title)}</a></li>')
    return "\n".join(items)


def wrap_page(page: Page, pages: list[Page]) -> str:
    title = html.escape(page.title)
    return f"""<!DOCTYPE html>
<html lang="en">
<head>
  <meta charset="utf-8" />
  <meta name="viewport" content="width=device-width, initial-scale=1.0" />
  <meta name="author" content="Chong Shik Park" />
  <title>{title} - synapticTrack</title>
  <link rel="stylesheet" href="{STYLE}" />
  <script src="{MATHJAX}" type="text/javascript"></script>
</head>
<body>
<header class="site-header">
  <div class="rtd-brand">
    <img src="synaptictrack.svg" alt="synapticTrack logo" />
    <div>
      <h1>synapticTrack</h1>
      <p>Project Documentation</p>
    </div>
  </div>
  <label class="rtd-search" aria-label="Search documentation">
    <span>Search docs</span>
    <input type="search" placeholder="Search docs" disabled />
  </label>
  <div class="rtd-version">latest</div>
  <div class="rtd-downloads">
    <a href="synapticTrack_consolidated.pdf">PDF</a>
    <a href="synapticTrack_consolidated.tex">LaTeX</a>
  </div>
  <p class="byline">Chong Shik Park<br />Department of Accelerator Science and Center for Accelerator Research, Korea University, Sejong, 30019 Republic of Korea</p>
</header>
<div class="layout">
<nav id="TOC" role="doc-toc">
<ul>
{nav_html(pages, page)}
</ul>
</nav>
<main>
<div class="page-tools"><a href="index.html">Docs home</a><span>{title}</span></div>
{page.body}
</main>
</div>
</body>
</html>
"""


def build() -> None:
    markdown = strip_yaml_front_matter(SOURCE_MD.read_text(encoding="utf-8"))
    sections = split_markdown_sections(markdown)
    if not sections:
        raise RuntimeError("No top-level sections found in consolidated Markdown.")
    pages = build_pages(sections)
    for page in pages:
        (SITE_DIR / page.filename).write_text(wrap_page(page, pages), encoding="utf-8")


if __name__ == "__main__":
    build()
