# Scientific validation supplements

These locally maintained checks supplement the complete upstream skill manuals.
They are procedural checks, not claims of improved scientific accuracy.

- For Nextflow, trace samples and channel shapes through the actual workflow,
  inspect process inputs/outputs and resolved configuration, and exercise stub
  execution before a production run when the pipeline supports it. Keep resource,
  executor, queue/account, container, and reference choices explicit for SLURM.
- For long-read and large sequence files, prefer streaming/chunked processing and
  verify record identifiers, lengths, quality fields, compression, and ordering
  using representative records. Avoid loading the complete dataset merely to
  inspect its shape.
- For structural formats such as mmCIF, choose a parser for the actual format and
  inspect how model, chain, and residue identifiers are represented. Retrieve the
  installed library's official documentation for API details instead of treating
  a PDB example as a universal parser recipe.
- For indexed genomic access, verify the reference build, index, coordinate
  convention, sort order, and relevant flags. Distinguish reads, molecules,
  alignments, records, and samples when counting.
- For discrepancies in reports, trace filters, denominators, normalization and
  aggregation back to source records. Record software/reference versions and
  reproduction commands, and verify the exported report or figure.
- Use an isolated project Python environment or conda environment; do not modify
  system Python protections. Inspect running jobs/resources before heavy work.
  Keep private sample identifiers and credentials out of shared notes and exports.
