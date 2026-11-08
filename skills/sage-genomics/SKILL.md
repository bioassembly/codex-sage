---
name: sage-genomics
description: Build, debug, or run Nextflow DSL2 and nf-core pipelines, including cluster resource configuration.
---

Discover the engine and pipeline revision, executor, container engine, samplesheet
schema, reference build, and available environments before proposing commands.
Use the selected release's official documentation; do not assume current flags
apply to an older pipeline. Pin revisions and preserve raw inputs and metadata.
Trace sample IDs and tuple/channel shape through upstream and downstream processes.
Check joins, cardinality, queue versus reusable values, output collisions, and cache
inputs. Keep process dependencies explicit and use existing nf-core conventions.
Run the narrowest nf-test, stub, or tiny fixture first, then validate scientific
outputs on known inputs. Stub success checks wiring, not biological correctness.
Inspect CPU, RAM, disk, active jobs, and scheduler policy before costly runs. Never
cancel active jobs or alter environments merely to make a test pass. Use conda run
or existing containers/venvs; do not force installs into system Python.
Record versions, parameters, reference provenance, checksums where practical, and
filter denominators. Treat clinical identifiers and genomic inputs as private;
only send externally when the user's task and data permissions authorize it.
Consult [Nextflow](https://www.nextflow.io/docs/latest/) and
[nf-core](https://nf-co.re/docs) for exact version-specific syntax.
