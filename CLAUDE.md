# meteakcaoglu.com

Quarto website, deployed to GitHub Pages by `.github/workflows/deploy.yml` on push to `master`. `_site/` is not tracked.

## Layout
- `index.qmd`: landing page (byline strip, Latest Writing, Selected Work, News)
- `about.qmd`: photo, bio, and fact sheet; Research Interests; all News
- `research.qmd`, `projects.qmd`, `teaching.qmd`, `blog.qmd`, `posts/`
- `cv.qmd` (public) and `cv-dean.qmd` (dean-facing); `UPDATES.md` is the CV queue drained by `/cv-sync`
- `news.yml`: news items for the landing page and About
- `_includes/`: footer and custom EJS listing templates
- `site-styles.css`: all styling; Swiss brand tokens (see `~/swiss-brand-tokens.md`) plus `--shade` for hover and panel fills

## Conventions
- Every post needs `image:` in its front matter, or the landing lead story shows an empty box. Marks live in `images/marks/`; all are Claude-made (disclosed in the footer).
- `_filters/post-mark.lua` (via `posts/_metadata.yml`) shows a post's `images/marks/posts/` mark inline after its first paragraph. A post can place its own `{.post-mark}` image instead, or opt out with `post-mark: false`.
- Links to live artifacts (dashboards, prototypes, preprints) go in a `::: {.artifact-box}` with an `{.artifact-kicker}` span, a bold title, one line of text, and `{.artifact-cta}` button links.
- Selected Work cards in `index.qmd` copy text from `projects.qmd`; edit both.
- Custom EJS listings: Pandoc re-reads the output as markdown, so keep each item on one line inside a block `<div>`.
- Citation stats ("h-index N · N citations") live in `cv.qmd`, `cv-dean.qmd`, `research.qmd`, and `about.qmd`; `scripts/check-scholar.py` (gitignored) matches that exact pattern.
- Screen-only page frame: outer grey `#c8c5bd`, a 40px `--rule` band around the sheet on three sides (`box-shadow` spread). Print is untouched.

## Verifying a deploy
Poll with a cache-busting query against a genuinely new marker. If it doesn't land, check the run via the public Actions API (`gh` isn't installed); a Pages "Timeout reached" failure redeploys with an empty commit.
