import requests
import json
from datetime import datetime

AUTHOR_ID = "2803529"
API_BASE = "https://api.semanticscholar.org/graph/v1"

def fetch_all_papers(author_id):
    """Fetch all papers for an author including full fields."""
    url = f"{API_BASE}/author/{author_id}/papers?fields=title,year,authors,venue,publicationTypes,citationCount,externalIds"
    response = requests.get(url)
    if response.status_code == 200:
        return response.json().get('data', [])
    else:
        print(f"Error {response.status_code}: {response.text}")
        return []

def format_author_name(author_name):
    """Format to 'Lastname, F.' and highlight Mete Akcaoglu."""
    parts = author_name.split()
    if not parts: return author_name
    last_name = parts[-1]
    first_initial = parts[0][0] if parts else ""
    formatted = f"{last_name}, {first_initial}."
    if "Akcaoglu" in last_name:
        return f"**{formatted}**"
    return formatted

def generate_markdown(papers):
    """Sort and categorize papers for the CV."""
    papers.sort(key=lambda x: x.get('year') or 0, reverse=True)
    
    journals = []

    for p in papers:
        year = p.get('year') or "n.d."
        title = p.get('title')
        venue = p.get('venue') or "Preprint/Other"
        citations = p.get('citationCount', 0)
        authors = ", ".join([format_author_name(a['name']) for a in p.get('authors', [])])
        
        pub_types = p.get('publicationTypes') or []

        # Only include items Semantic Scholar explicitly classifies as JournalArticle.
        # Conference papers, preprints, and ambiguous items are listed manually in cv.qmd.
        if 'JournalArticle' not in pub_types:
            continue

        entry = f"- {authors} ({year}). {title}. *{venue}*. [Citations: {citations}]"
        journals.append(entry)

    content = ["### Peer-Reviewed Journal Articles (auto-synced from Semantic Scholar)\n"]

    if journals:
        content.extend(journals)
        content.append("")
        
    return "\n".join(content)

def main():
    print(f"Syncing publications for Author ID: {AUTHOR_ID}...")
    papers = fetch_all_papers(AUTHOR_ID)
    
    if not papers:
        print("No papers retrieved.")
        return
        
    markdown = generate_markdown(papers)
    
    with open("publications.qmd", "w", encoding="utf-8") as f:
        f.write(markdown)
        
    print(f"Successfully synced {len(papers)} publications to publications.qmd")

if __name__ == "__main__":
    main()
