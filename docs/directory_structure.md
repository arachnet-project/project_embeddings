**File:** `docs/directory_structure.md`

---

### Arachnet Clinical Embeddings — Directory Structure

The project uses two separate storage locations on OCI. The first is on the boot volume and contains all code, configuration, documentation and logs. The second is on a separately attached block volume and contains all data files.

---

#### Boot Volume — /home/opc/project_embeddings

This is the main project root. All code, configuration, scripts, documentation and logs live here.

**Configuration**
- `/home/opc/project_embeddings/config/` — all YAML configuration files for all phases

**Documentation**
- `/home/opc/project_embeddings/docs/` — all project documentation in Markdown format, including phase plans, directory structure, infrastructure specification and architecture decisions

**Logs**
- `/home/opc/project_embeddings/log/` — runtime log files from all phases and scripts

**Python Source — /home/opc/project_embeddings/src/**

Shared utilities, Phase 0:
- `/home/opc/project_embeddings/src/common/` — shared utilities used by all phases
- `/home/opc/project_embeddings/src/common/config_loader.py` — YAML reader and environment variable exporter
- `/home/opc/project_embeddings/src/common/db_connection.py` — Oracle 23ai connection helper
- `/home/opc/project_embeddings/src/common/logger.py` — structured logging utility
- `/home/opc/project_embeddings/src/common/exceptions.py` — project-wide exception hierarchy

Phase modules:
- `/home/opc/project_embeddings/src/ingestion/` — Phase 1, RF2 ingestion pipeline
- `/home/opc/project_embeddings/src/policy/` — Phase 2, MRCM and semantic policy layer
- `/home/opc/project_embeddings/src/embedding/` — Phase 3, embedding engine
- `/home/opc/project_embeddings/src/query/` — Phase 4, query and inference layer
- `/home/opc/project_embeddings/src/compliance/` — Phase 5, compliance, audit and governance

**Bash Scripts — /home/opc/project_embeddings/scripts/**

- `/home/opc/project_embeddings/scripts/common/` — Phase 0, orchestrator and shared Bash utilities including logger.sh
- `/home/opc/project_embeddings/scripts/ingestion/` — Phase 1
- `/home/opc/project_embeddings/scripts/policy/` — Phase 2
- `/home/opc/project_embeddings/scripts/embedding/` — Phase 3
- `/home/opc/project_embeddings/scripts/query/` — Phase 4
- `/home/opc/project_embeddings/scripts/compliance/` — Phase 5

---

#### Data Volume — /mnt/snomed_data

This is a separately attached OCI block volume. It is mounted at `/mnt/snomed_data` and contains all data files. Keeping data separate from code simplifies backup, volume expansion, and data lifecycle management independently of the application.

- `/mnt/snomed_data/rf2/` — SNOMED CT RF2 source files, downloaded manually from MLDS. Read-only during pipeline execution.
- `/mnt/snomed_data/parquet/` — Parquet files converted from RF2 TSV files during Phase 1 ingestion. Generated and managed by the pipeline.

---

#### Notes

Each Python directory under `src/` contains an `__init__.py` file making it a proper Python package. This allows clean imports across phases, for example:

```python
from common.logger import get_logger
from common.db_connection import get_connection
```

The data volume path `/mnt/snomed_data` must be mounted before any Phase 1 script is executed. Mount configuration is documented in `docs/infrastructure.md`.