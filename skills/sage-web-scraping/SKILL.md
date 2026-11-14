---
name: sage-web-scraping
description: Extract a structured dataset from web pages or a documented web API.
---

Define fields, source URLs, pagination boundaries, and an example output record.
Prefer a documented API or static HTML retrieval when it contains the required
data. Use browser interaction when rendering or a supported authenticated flow
requires it. Reuse an available connector for its service.
Inspect actual markup and sample records before selecting fields. Handle missing
values, encoding, duplicates, pagination cycles, and units explicitly. Bound
requests, use suitable rate limits/retries, and preserve retrieval timestamps and
source attribution. Keep account credentials and unrelated page data out of
results. Validate counts, representative records, and termination conditions.
Save a reproducible extraction method and distinguish unavailable records from
empty values. Avoid loading complete page dumps when selected fields suffice.
