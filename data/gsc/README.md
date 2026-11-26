# Search Console exports

Select the dcostdaily.com domain property in Google Search Console. If it is missing, add the domain property, add the TXT record Google supplies to Cloudflare DNS, and click Verify in Search Console. Wait for the Performance report to contain data.

In Performance > Search results, select Web and the longest available date range, up to 16 months. Record the actual first and last dates. Export the Queries and Pages tables for the same filters and dates as CSV. Place the files in this folder using the names below. Raw exports are ignored by Git.

| File | Columns |
| --- | --- |
| queries.csv | Top queries (or Query), Clicks, Impressions, CTR, Position |
| pages.csv | Top pages (or Page), Clicks, Impressions, CTR, Position |
| queries-pages.csv (optional) | Query, Page, Clicks, Impressions, CTR, Position |

The optional paired export provides query-level URL attribution. The separate Queries and Pages tables do not identify which URL earned an individual query's impressions.

From the repository root, substitute the actual export dates for the placeholders.

~~~sh
python3 scripts/gsc_gaps.py --start YYYY-MM-DD --end YYYY-MM-DD
~~~

Review the ranked opportunities in docs/gsc-gaps/report.md against the actual content of each matching page. If an existing guide covers the intent, update that page. Use the impressions, clicks and positions in the report as the baseline for a later post-publication comparison.
