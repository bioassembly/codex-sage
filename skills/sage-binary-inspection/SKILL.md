---
name: sage-binary-inspection
description: Inspect relevant opaque binaries, packaged apps, bytecode, or minified bundles without source.
---

Use this workflow only when the artifact is relevant to the task and readable
source is unavailable. Start with file metadata, hashes, format, architecture,
imports, exports, and targeted strings. Prefer installed file/readelf/nm/objdump,
archive tools, source maps, or format-specific disassemblers.
If rea is installed, inspect its help and use the appropriate static inspection
command. Do not install a large reverse engineering suite just because a directory
contains binaries. Scope extraction and tool output to the question; save large
artifacts in scratch space and query specific symbols or offsets.
Do not execute untrusted binaries, attach to processes, or modify devices beyond
the user's scope. Label static observations, inferred behavior, and unavailable
decompiler output separately. Strings alone do not establish control flow.
Keep proprietary contents and credentials out of external tools or shared reports.
