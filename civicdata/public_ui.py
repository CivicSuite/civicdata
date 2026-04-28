"""Accessible public sample UI for CivicData Bridge."""


def render_public_lookup_page() -> str:
    """Return a static, dependency-free HTML page for browser QA."""

    return """<!doctype html>
<html lang="en">
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1">
<link rel="icon" href="data:,">
<title>CivicData Bridge - open data preparation</title>
<style>
:root{--ink:#17231d;--green:#1e6b4f;--mint:#d9f2e6;--gold:#c4943d;--paper:#fffaf0}
body{margin:0;font-family:"Aptos","Segoe UI",sans-serif;color:var(--ink);background:radial-gradient(circle at 20% 0,#dff7ef,transparent 32rem),linear-gradient(135deg,#eef9f3,var(--paper))}
header,main,footer{width:min(1080px,calc(100% - 32px));margin:auto}
header{padding:52px 0 20px}.eyebrow{text-transform:uppercase;letter-spacing:.14em;color:var(--green);font-weight:900}
h1{font:800 clamp(2.35rem,7vw,5.2rem)/.95 Georgia,serif;margin:.1em 0}.lede{font-size:1.2rem;line-height:1.6;max-width:850px}
.grid{display:grid;grid-template-columns:repeat(2,minmax(0,1fr));gap:18px}.card{background:rgba(255,255,255,.91);border:1px solid #b6d8c8;border-radius:24px;padding:24px;box-shadow:0 18px 36px #263b3118}
.badge{display:inline-block;background:var(--green);color:white;padding:.5rem .85rem;border-radius:999px;font-weight:900}
code{background:var(--mint);padding:.1rem .35rem;border-radius:.35rem}:focus-visible{outline:4px solid var(--gold);outline-offset:3px}@media(max-width:720px){.grid{grid-template-columns:1fr}header{padding-top:34px}}
</style>
</head>
<body>
<header>
  <p class="eyebrow">CivicSuite / CivicData Bridge</p>
  <h1>Open-data packages with review gates built in.</h1>
  <p class="lede">CivicData Bridge v0.1.1 helps staff normalize municipal datasets, draft data dictionaries, prepare CKAN-ready package metadata, and assemble records-retention archive checklists.</p>
  <p><span class="badge">Shipping v0.1.1</span></p>
</header>
<main>
  <section class="grid" aria-label="CivicData release status">
    <article class="card"><h2>What ships</h2><ul><li>Dataset field normalization.</li><li>Data-dictionary drafting.</li><li>CKAN package metadata drafts.</li><li>PII/exemption redaction preflight.</li><li>Archive-bundle and publication checklists.</li></ul></article>
    <article class="card"><h2>Human approval required</h2><p>Every export must clear staff approval, redaction/exemption review, retention checks, and open-data license confirmation before publication.</p></article>
    <article class="card"><h2>Boundaries</h2><p>No live CKAN publication, no BI dashboards, no data warehouse, no long-term storage, no autonomous redaction, and no external connector runtime ships in v0.1.1.</p></article>
    <article class="card"><h2>Dependency</h2><p>Pinned to <code>civiccore==0.3.0</code>. CivicCore remains dependency-only; it never imports from CivicData.</p></article>
  </section>
</main>
<footer><p>Apache 2.0 code. CC BY 4.0 docs. Run locally by the city.</p></footer>
</body>
</html>"""
