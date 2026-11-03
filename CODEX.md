# CODEX.md

## What this site is
dcostdaily.com is "dcost daily": a static site (plain HTML, CSS and JS, no framework) with a daily Tesla, EV and AI news digest, an EV vs gas calculator, a chargers page, and SEO cost pages generated from EIA and EPA data. It deploys to the Cloudflare Pages project `dcost-daily`.

## Redesign goal
The `redesign-fullcharge` branch is the "Full Charge" restyle: black base, white text, Tesla blue accent, mint for EV savings, Barlow fonts, battery-cell wordmark. Keep refining the look and make it consistent on every page, at 1280 and 390 widths.

## Rules
- Keep every live route working: `/`, `/chargers`, `/calculator`, `/archive`, `/ev-cost/*`, `/ev-vs-gas/*`, `/compare/*`, `/tesla/*`, `/guides/*`, `robots.txt`, `sitemap.xml` and the 404 page.
- Keep the live data: `data/*.json`, `chargers.js` picks and the `dcostdaily-20` Amazon tag in `config.js`. Do not hardcode numbers that `data/rates.json` supplies.
- Generated pages come from `scripts/gen_pages.py` and `scripts/gen_compare.py`. Change the generator, then regenerate, instead of hand-editing generated HTML.
- No em-dashes in any page text.
- No production deploys. Deploys stay manual and are approved by Jared. A preview deploy of a branch is fine; production (`--branch main`) is not.
- Never commit secrets: no tokens, API keys, `.env` files, credentials or affiliate account answers. The Cloudflare token lives outside the repo and must never be read or printed.
- Open a PR for every change, with screenshots at 1280 and 390 widths. Do not merge.
