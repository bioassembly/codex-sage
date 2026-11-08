---
name: sage-sequence-analysis
description: Process sequence, alignment, variant, or indexed genomic files using Biopython and pysam.
---

Choose a streaming parser for large FASTA/FASTQ/BAM/CRAM/VCF files. Inspect headers,
reference contigs, indexes, coordinate conventions, and compression before querying.
Distinguish zero-based half-open intervals from one-based inclusive coordinates;
test an interval boundary against a tiny known fixture. Verify strand, reference
build, alternate alleles, and sample mapping before joining datasets.
Use Biopython for sequence/structure parsing and transformations; use pysam for
htslib-backed alignment, variant, and tabix access. Check installed versions and
API docs rather than guessing methods. Use context managers and preserve headers.
CRAM decoding may require the exact reference. Coordinate-sorted alignment and a
matching index are prerequisites for indexed region queries. Report filters for
secondary/supplementary alignments, duplicates, mapping/base quality, and missing
values. Counts require explicit units and denominators (reads, pairs, molecules).
For Entrez, follow NCBI rate/contact requirements, batch and cache requests, and
never embed API keys in committed scripts. Validate parse counts and output round
trips using small fixtures before scaling. Preserve source files.
References: [Biopython](https://biopython.org/docs/latest/),
[pysam](https://pysam.readthedocs.io/en/latest/),
[SAM/VCF specifications](https://samtools.github.io/hts-specs/).
