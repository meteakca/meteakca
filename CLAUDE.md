# meteakcaoglu.com

Quarto website, deployed to GitHub Pages by `.github/workflows/deploy.yml` on push to `master`. `_site/` is not tracked.

## Layout
- `index.qmd`: landing page (two-column intro, Latest Writing lead + dated rows, then Selected Work and News & Papers side by side)
- `about.qmd`: photo, bio, and fact sheet; Research Interests; all News
- `research.qmd`, `projects.qmd`, `teaching.qmd`, `blog.qmd`, `posts/`
- `cv.qmd` (public) and `cv-dean.qmd` (dean-facing); `UPDATES.md` is the CV queue drained by `/cv-sync`
- `news.yml`: news items for the landing page and About
- `_includes/`: footer and custom EJS listing templates
- `site-styles.css`: all styling; Swiss brand tokens (see `~/swiss-brand-tokens.md`) plus `--shade` for hover and panel fills

## Conventions
- Every post needs `image:` in its front matter, or the landing lead story shows an empty box. `lead: false` keeps a post out of the lead slot (it shows as a dated row); the newest post without it leads. Marks live in `images/marks/`; all are Claude-made (disclosed in the footer).
- `_filters/post-mark.lua` (via `posts/_metadata.yml`) floats a post's `images/marks/posts/` mark to the right of its first paragraph (stacked on phones). A post can place that image itself (`{.post-mark}`, or `{.post-mark .left}` to float left), or opt out with `post-mark: false`.
- Conversation posts (e.g. the Modest Proposal post) use chat bubbles: wrap the transcript in `:::: {.chat}`, each turn in `::: {.msg .me}` (right, dark) or `::: {.msg .ai}` (left, shaded), starting with a `[Name]{.msg-who}` label.
- The home intro shows the MA monogram (`images/marks/monogram.svg`); the photo stays on About.
- Links to live artifacts (dashboards, prototypes, preprints) go in a `::: {.artifact-box}` with an `{.artifact-kicker}` span, a bold title, one line of text, and `{.artifact-cta}` button links.
- Selected Work cards in `index.qmd` copy text from `projects.qmd`; edit both.
- Custom EJS listings: Pandoc re-reads the output as markdown, so keep each item on one line inside a block `<div>`.
- Citation stats ("h-index N · N citations") live in `cv.qmd`, `cv-dean.qmd`, `research.qmd`, and `about.qmd`; `scripts/check-scholar.py` (gitignored) matches that exact pattern.
- Screen-only page frame: outer grey `#c8c5bd`, a 40px `--rule` band around the sheet on three sides (`box-shadow` spread). Print is untouched.
- Sheet width: site pages use `page-layout: full` (in `_quarto.yml`) and a 1040px sheet, screen only. The private CVs and letters set `page-layout: article` and stay at 803px. Print output is unchanged (checked by diffing PDF text before and after).
- Left rail: posts, plus pages with `body-classes: rail-page` (Research, Teaching), get a 200px left column for the date, tags, § numbers, and `dl` labels, with a ~736px text column; it folds to one column below 900px. These pages have no rules between sections, only one `--rule` gray rule under the page header.
- `news.yml` items with `kind: paper` show a "Paper" tag; they fill the landing page's News & Papers rail.

## Verifying a deploy
Poll with a cache-busting query against a genuinely new marker. If it doesn't land, check the run via the public Actions API (`gh` isn't installed); a Pages "Timeout reached" failure redeploys with an empty commit.
