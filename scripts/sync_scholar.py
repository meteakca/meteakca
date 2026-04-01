#!/usr/bin/env python3
"""
Sync publications from Semantic Scholar to Hugo content files.
Generates individual Markdown files in content/scholar-publications/.

Uses the free Semantic Scholar API (no key required for basic use):
https://api.semanticscholar.org/graph/v1

Usage:
    python scripts/sync_scholar.py

Requires:
    pip install requests PyYAML
"""

import re
import sys
import time
import yaml
import requests
from pathlib import Path

S2_AUTHOR_ID = "2803529"  # Mete Akcaoglu on Semantic Scholar
OUTPUT_DIR = Path("content/scholar-publications")
S2_BASE = "https://api.semanticscholar.org/graph/v1"
PAPER_FIELDS = "title,year,authors,venue,abstract,citationCount,externalIds,openAccessPdf,publicationDate"


def apa_author(name: str) -> str:
    """Convert 'First [Middle] Last' to 'Last, F. M.' APA format."""
    parts = name.strip().split()
    if len(parts) == 1:
        return parts[0]
    last = parts[-1]
    initials = " ".join(p[0].upper() + "." for p in parts[:-1])
    return f"{last}, {initials}"


def apa_author_list(authors: list) -> str:
    """Format a list of author names in APA reference-list style."""
    if not authors:
        return ""
    apa = [apa_author(a) for a in authors]
    if len(apa) == 1:
        return apa[0]
    if len(apa) == 2:
        return f"{apa[0]}, & {apa[1]}"
    # APA allows up to 20 authors; truncate with ellipsis beyond that
    if len(apa) > 20:
        apa = apa[:19] + ["..."] + [apa[-1]]
    return ", ".join(apa[:-1]) + ", & " + apa[-1]


def slugify(text: str) -> str:
    text = text.lower().strip()
    text = re.sub(r"[^\w\s-]", "", text)
    text = re.sub(r"[\s_]+", "-", text)
    text = re.sub(r"-{2,}", "-", text)
    return text.strip("-")[:80]


def s2_get(url: str, params: dict = None, retries: int = 3) -> dict:
    """GET with simple retry on 429 rate-limit responses."""
    for attempt in range(retries):
        resp = requests.get(url, params=params, timeout=30)
        if resp.status_code == 429:
            wait = int(resp.headers.get("Retry-After", 10)) + attempt * 5
            print(f"  Rate limited — waiting {wait}s...")
            time.sleep(wait)
            continue
        resp.raise_for_status()
        return resp.json()
    raise RuntimeError(f"Failed after {retries} attempts: {url}")


def fetch_all_papers(author_id: str) -> list:
    papers = []
    offset = 0
    limit = 100
    while True:
        data = s2_get(
            f"{S2_BASE}/author/{author_id}/papers",
            params={"fields": PAPER_FIELDS, "limit": limit, "offset": offset},
        )
        batch = data.get("data", [])
        papers.extend(batch)
        print(f"  Fetched {len(papers)} papers so far...")
        if len(batch) < limit:
            break
        offset += limit
        time.sleep(1)  # be polite
    return papers


def write_publication(paper: dict, output_dir: Path, index: int) -> Path:
    title = (paper.get("title") or f"Publication {index}").strip()
    slug = slugify(title) or f"publication-{index}"

    pub_dir = output_dir / slug
    pub_dir.mkdir(parents=True, exist_ok=True)
    filepath = pub_dir / "index.md"

    authors = [a["name"] for a in paper.get("authors", []) if a.get("name")]
    year = paper.get("year") or ""
    abstract = (paper.get("abstract") or "").strip()
    venue = (paper.get("venue") or "").strip()
    citation_count = int(paper.get("citationCount") or 0)

    # Build Scholar URL from external IDs if available
    ext = paper.get("externalIds") or {}
    doi = ext.get("DOI", "")
    scholar_url = ""
    if ext.get("CorpusId"):
        scholar_url = f"https://www.semanticscholar.org/paper/{paper['paperId']}"

    # Open access PDF
    oa = paper.get("openAccessPdf") or {}
    eprint_url = oa.get("url", "")

    date_str = f"{year}-01-01T00:00:00Z" if year else "2000-01-01T00:00:00Z"

    # Build APA citation string (stored in frontmatter for use in templates)
    year_part = f"({year})" if year else "(n.d.)"
    author_part = apa_author_list(authors)
    venue_part = f" *{venue}*." if venue else "."
    apa_citation = f"{author_part} {year_part}. {title}{venue_part}"

    frontmatter = {
        "title": title,
        "authors": authors,
        "apa_citation": apa_citation,
        "date": date_str,
        "publication": venue,
        "abstract": abstract,
        "citation_count": citation_count,
        "scholar_url": scholar_url,
        "eprint_url": eprint_url,
        "doi": doi,
        "draft": False,
        "featured": False,
    }

    for key in ("publication", "abstract", "scholar_url", "eprint_url", "doi"):
        if not frontmatter[key]:
            del frontmatter[key]

    yaml_block = yaml.dump(
        frontmatter,
        allow_unicode=True,
        default_flow_style=False,
        sort_keys=False,
    )
    filepath.write_text(f"---\n{yaml_block}---\n", encoding="utf-8")
    return filepath


def main() -> int:
    output_dir = OUTPUT_DIR
    output_dir.mkdir(parents=True, exist_ok=True)

    index_file = output_dir / "_index.md"
    if not index_file.exists():
        index_file.write_text(
            "---\ntitle: Publications\ncms_exclude: true\n---\n",
            encoding="utf-8",
        )

    print(f"Fetching papers for Semantic Scholar author ID: {S2_AUTHOR_ID}")
    try:
        papers = fetch_all_papers(S2_AUTHOR_ID)
    except Exception as exc:
        print(f"ERROR fetching papers: {exc}")
        return 1

    total = len(papers)
    if total == 0:
        print("ERROR: 0 papers returned — check the author name or Semantic Scholar coverage.")
        return 1
    print(f"\nFound {total} papers. Writing Hugo files...\n")

    seen_slugs: dict[str, int] = {}
    success = 0
    errors = 0

    for i, paper in enumerate(papers):
        title = (paper.get("title") or f"publication-{i}").strip()
        print(f"[{i+1}/{total}] {title[:70]}")

        base_slug = slugify(title) or f"publication-{i}"
        if base_slug in seen_slugs:
            seen_slugs[base_slug] += 1
            # adjust slug on the paper dict so write_publication uses the right folder
            paper["_slug"] = f"{base_slug}-{seen_slugs[base_slug]}"
            base_slug = paper["_slug"]
        else:
            seen_slugs[base_slug] = 0

        try:
            filepath = write_publication(paper, output_dir, i)
            print(f"  Saved → {filepath}  [{paper.get('citationCount', 0)} citations]")
            success += 1
        except Exception as exc:
            print(f"  ERROR: {exc}")
            errors += 1

    print(f"\nDone. {success} written, {errors} errors.")
    return 0 if errors == 0 else 1


if __name__ == "__main__":
    sys.exit(main())
