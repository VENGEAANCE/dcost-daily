# Full Charge polish, November 3, 2026

Intent: serve readers scanning the daily Tesla, EV and AI digest and drivers comparing home charging with gas. Preserve the documented battery wordmark, black base, Barlow typography, blue actions and mint savings. Improve legibility and keyboard use without adding new product claims or changing the live dataset.

Changes:
- Compact mobile header, larger touch targets, readable fine print, consistent panels and table spacing, and wrapping for long state names and calls to action.
- Menu expanded state, Escape/outside-click dismissal, keyboard focus handling, skip link, current-page semantics, associated field labels and filter states.
- Digest load recovery, reading-progress focus retention and validated saved indices.
- Home savings and calculator prices load from rates.json rather than stale inline prices. Negative savings use neutral text.
- Generator date formatting and UTF-8 file I/O work on Windows; regenerated all 92 generated pages with the refreshed asset version.

Validation:
- 97 HTML pages checked in local Chrome at 1280 and 390 widths (194 checks), without document-level horizontal overflow or JavaScript page errors.
- Exercised mobile menu, calculator mileage updates and California price selection, charger filters, reading persistence and focus, and failed digest/rate requests.
- `python scripts/check_routes.py`: 6,693 internal links/assets and every sitemap destination resolve; HTML has no em dashes. Existing /share and /og-image Worker endpoints are excluded from static resolution.
- `python scripts/gen_pages.py`, JavaScript syntax checks, and `git diff --check` pass.
- data/*, config.js, chargers.js, vehicles.js, robots.txt and sitemap.xml are unchanged.

Screenshots below are local static renders. External requests were blocked during the automated capture: Google Fonts use their configured fallback, failed story thumbnails disappear, and the Beehiiv embed is blank. External newsletter submission, remote image delivery and Worker responses were not tested. No deployment was run.

| Page | 1280 | 390 |
| --- | --- | --- |
| Home | [Desktop](home-1280.png) | [Mobile](home-390.png) |
| Calculator | [Desktop](calculator-1280.png) | [Mobile](calculator-390.png) |
| California | [Desktop](state-1280.png) | [Mobile](state-390.png) |
