# Third-party notices

`skills/ponytail`, `skills/grill-with-docs`, `skills/grilling`, and
`skills/domain-modeling` are original pinned
upstream packages from DietrichGebert/ponytail and mattpocock/skills. Their complete
files and original invocation policies are preserved. Native loader mapping lives
outside the packages. Reviewed revisions and original hashes are tracked in the
source manifests.

Both upstream works use the following MIT license. The notices apply to their
respective upstream material:

Copyright (c) 2026 DietrichGebert

Copyright (c) 2026 Matt Pocock

Permission is hereby granted, free of charge, to any person obtaining a copy
of this software and associated documentation files (the "Software"), to deal
in the Software without restriction, including without limitation the rights
to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
copies of the Software, and to permit persons to whom the Software is
furnished to do so, subject to the following conditions:

The above copyright notice and this permission notice shall be included in all
copies or substantial portions of the Software.

THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE
SOFTWARE.

## Unmodified Trail of Bits skills

`skills/variant-analysis` and `skills/differential-review` are unmodified skill
directories from [trailofbits/skills](https://github.com/trailofbits/skills),
including their authors' assets and references. Trail of Bits retains attribution.
They are licensed separately under CC-BY-SA-4.0; the complete upstream license is
in [third_party/licenses/trailofbits-skills.txt](third_party/licenses/trailofbits-skills.txt).
Source revisions and original Git blob hashes are in `third_party/lock.json`.
No endorsement by Trail of Bits is implied.

## Unmodified Vercel skill

`skills/vercel-react-best-practices` is the unmodified `skills/react-best-practices`
directory from [vercel-labs/agent-skills](https://github.com/vercel-labs/agent-skills).
The upstream skill identifies Vercel as author and declares MIT in its frontmatter.
The reviewed repository tree contains no separate LICENSE file; this distribution
preserves the upstream metadata and records that limitation rather than inventing
an upstream copyright notice. Original file hashes are in `third_party/lock.json`.

## RTK

RTK OSS is downloaded separately from the official `rtk-ai/rtk` release. Its
version, edition, asset URLs, and checksums are tracked in `third_party/lock.json`.
The upstream project identifies its OSS hook/filter edition as Apache-2.0.
Its license is preserved in [third_party/licenses/rtk-oss.txt](third_party/licenses/rtk-oss.txt).
No RTK binary or pipeline engine is vendored in this repository.

## Additional sibling skill sources

Sibling recipes also vendor reviewed Matt Pocock engineering/setup packages,
Obra Superpowers workflows, Anthropic MCP/browser skills, and K-Dense scientific
skills. Individual manifests identify which packages each client ships.
Superpowers' MIT license is retained in `third_party/licenses/superpowers.txt`.
Anthropic's per-package LICENSE.txt files are preserved with those packages.
K-Dense's repository MIT license is retained in
`third_party/licenses/scientific-agent-skills.md`; original package metadata also
identifies the respective library licenses.

One Anthropic MCP evaluation helper has an explicit correctness patch to process
all tool requests in a response. The original source hash, patched hash, and
patch file are recorded. Three Vercel compiled-guide aliases are also declared.
Ponytail, grill-with-docs, grilling, and domain-modeling have no content patches.
