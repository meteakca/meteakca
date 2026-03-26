#!/usr/bin/env python3
"""
Sync publications from Google Scholar to Hugo content files.
Generates individual Markdown files in content/scholar-publications/.

Usage:
    python scripts/sync_scholar.py

Requires:
    pip install scholarly PyYAML
"""

import re
import sys
import yaml
from pathlib import Path

SCHOLAR_ID = "0y1b0oEAAAAJ"
OUTPUT_DIR = Path("content/scholar-publications")


def slugify(text: str) -> str:
    """Convert a title to a URL-friendly slug."""
    text = text.lower().strip()
    text = re.sub(r"[^\w\s-]", "", text)
    text = re.sub(r"[\s_]+", "-", text)
    text = re.sub(r"-{2,}", "-", text)
    text = text.strip("-")
    return text[:80]


def parse_authors(authors_raw) -> list:
    """Parse scholarly's author string or list into a clean list."""
    if not authors_raw:
        return []
    if isinstance(authors_raw, list):
        return [a.strip() for a in authors_raw if a.strip()]
    # String like "A Smith, B Jones and C Williams"
    authors_str = str(authors_raw)
    # scholarly sometimes uses " and " before the last author
    authors_str = authors_str.replace(" and ", ", ")
    return [a.strip() for a in authors_str.split(",") if a.strip()]


def write_publication(pub_data: dict, output_dir: Path, index: int) -> Path:
    """Write a single publication as a Hugo Markdown file."""
    bib = pub_data.get("bib", {})

    title = (bib.get("title") or f"Publication {index}").strip()
    slug = slugify(title)
    if not slug:
        slug = f"publication-{index}"

    pub_dir = output_dir / slug
    pub_dir.mkdir(parents=True, exist_ok=True)
    filepath = pub_dir / "index.md"

    authors = parse_authors(bib.get("author", ""))
    year = str(bib.get("pub_year", "")).strip()
    abstract = (bib.get("abstract") or "").strip()
    venue = (
        bib.get("venue")
        or bib.get("journal")
        or bib.get("booktitle")
        or bib.get("conference")
        or ""
    ).strip()
    citation_count = int(pub_data.get("num_citations", 0) or 0)
    scholar_url = (pub_data.get("pub_url") or "").strip()
    eprint_url = (pub_data.get("eprint_url") or "").strip()

    # Build ISO date
    date_str = f"{year}-01-01T00:00:00Z" if year else "2000-01-01T00:00:00Z"

    frontmatter = {
        "title": title,
        "authors": authors,
        "date": date_str,
        "publication": venue,
        "abstract": abstract,
        "citation_count": citation_count,
        "scholar_url": scholar_url,
        "eprint_url": eprint_url,
        "draft": False,
        "featured": False,
    }

    # Remove empty optional fields to keep files tidy
    for key in ("publication", "abstract", "scholar_url", "eprint_url"):
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
    try:
        from scholarly import scholarly as scholar_api
    except ImportError:
        print("ERROR: 'scholarly' package not installed. Run: pip install scholarly")
        return 1

    output_dir = OUTPUT_DIR
    output_dir.mkdir(parents=True, exist_ok=True)

    # Write section index if missing
    index_file = output_dir / "_index.md"
    if not index_file.exists():
        index_file.write_text(
            "---\ntitle: Publications\ncms_exclude: true\n---\n",
            encoding="utf-8",
        )

    print(f"Fetching Google Scholar profile: {SCHOLAR_ID}")
    try:
        author = scholar_api.search_author_id(SCHOLAR_ID)
        author = scholar_api.fill(author, sections=["basics", "publications"])
    except Exception as exc:
        print(f"ERROR fetching author profile: {exc}")
        return 1

    publications = author.get("publications", [])
    total = len(publications)
    # Use only the data already returned by the author profile fetch — no
    # per-publication fill() calls, which trigger Scholar's bot detection.
    print(f"Found {total} publications. Writing files...\n")

    seen_slugs: dict[str, int] = {}
    success = 0
    errors = 0

    for i, pub in enumerate(publications):
        raw_title = pub.get("bib", {}).get("title", f"publication-{i}")
        print(f"[{i+1}/{total}] {raw_title[:70]}")

        # Deduplicate slugs
        title = raw_title.strip()
        base_slug = slugify(title) or f"publication-{i}"
        if base_slug in seen_slugs:
            seen_slugs[base_slug] += 1
            pub.setdefault("bib", {})["_slug_override"] = f"{base_slug}-{seen_slugs[base_slug]}"
        else:
            seen_slugs[base_slug] = 0

        try:
            filepath = write_publication(pub, output_dir, i)
            citations = pub.get("num_citations", 0) or 0
            print(f"  Saved: {filepath}  [{citations} citations]")
            success += 1
        except Exception as exc:
            print(f"  ERROR writing file: {exc}")
            errors += 1

    print(f"\nDone. {success} publications written, {errors} errors.")
    print(f"Output directory: {output_dir}")
    return 0 if errors == 0 else 1


if __name__ == "__main__":
    sys.exit(main())
