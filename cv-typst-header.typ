// ─────────────────────────────────────────────────────────
// Mete Akcaoglu · CV — Typst header
// ─────────────────────────────────────────────────────────

#let navy     = rgb("#1A3A5C")
#let navy-mid = rgb("#2C5282")
#let accent   = rgb("#3A7BD5")
#let muted    = rgb("#718096")

// ── Page ──────────────────────────────────────────────────
#set page(
  paper: "us-letter",
  margin: (x: 1in, y: 0.85in),
  footer: context {
    set text(size: 7.5pt, fill: muted)
    align(center)[Mete Akcaoglu · Page #counter(page).display()]
  }
)

// ── Typography ────────────────────────────────────────────
#set text(font: "Helvetica", size: 10pt, fill: rgb("#2D3748"))
#set par(leading: 0.6em, spacing: 0.9em)
#set list(indent: 0.5em, body-indent: 0.4em, marker: [•])
#set enum(indent: 0.5em, body-indent: 0.4em)

// H1 — name/header block
#show heading.where(level: 1): it => block(below: 0.5em, {
  text(font: "Palatino", size: 20pt, weight: "bold", fill: navy, it.body)
  v(0.15em)
  line(length: 100%, stroke: 2pt + navy)
})

// H2 — section headings
#show heading.where(level: 2): it => block(above: 1.5em, below: 0.65em, {
  text(font: "Palatino", size: 11pt, weight: "bold", fill: navy, upper(it.body))
  v(0.12em)
  line(length: 100%, stroke: 1.5pt + navy)
})

// H3 — subsection headings
#show heading.where(level: 3): it => block(above: 1em, below: 0.4em,
  text(font: "Palatino", size: 10pt, weight: "bold", fill: navy-mid, it.body)
)

// Definition lists → two-column date | content
#show terms.item: it => grid(
  columns: (1.25in, 1fr),
  gutter: 0.8em,
  align(right + top, text(size: 8.5pt, fill: muted, it.term)),
  it.description
)

// Tables — strip borders, mute first column
#set table(stroke: none, inset: (x: 0pt, y: 3pt))
#show table.cell.where(x: 0): set text(size: 8.5pt, fill: muted)

// Links
#show link: set text(fill: accent)
