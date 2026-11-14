---
name: sage-pdf-editing
description: Make precise PDF changes or redactions while checking layout and residual content.
---

Preserve the original and inspect page dimensions, text spans/fonts, annotations,
attachments, and raster images relevant to the requested change. Establish which
regions may change. Use an available PDF library in an isolated environment when
needed; retrieve its current documentation for unfamiliar APIs.
For visual corrections, preserve positioning and fonts where practical and check
that replacement text fits. Content-stream substitutions depend on encoding and
font mappings; never assume a plain byte replacement reaches every occurrence.
For redaction, remove underlying content using a real redaction workflow. Painting
over text or changing a visible identifier does not establish anonymization.
Inspect raster text, metadata, annotations, hidden layers, and attachments within
the requested scope. Do not claim secure removal from a visual comparison alone.

Render before/after pages at the same resolution and inspect changed regions.
Check extracted text and relevant metadata for residual content, then reopen the
saved result. Report the checks actually performed and any unresolved scope.
