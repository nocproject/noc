# NOC Platform — Agent Guidelines

## Overview

NOC is a telecom-grade Operation Support System (OSS) for service providers and enterprise NOCs. It manages network inventory, performance monitoring, fault management, device discovery, and provisioning at scale. All library versions are pinned in pyproject.toml — do not assume any specific version; always check pyproject.toml or devcontainer for dependencies.

The codebase follows a modular architecture similar to Django apps — each "application" is its own directory with models, migrations, and domain-specific logic. `core/` contains framework services (I/O loops, protocols, data sources, middleware). `services/` provides microservices implementation.

## Code Conventions

- **Formatter:** `ruff format`. Run on all Python files: `ruff format .`.
  Prefer running in devcontainer to guarantee correct ruff version.

- **Linter:** `ruff check`. Run `ruff check .` across the entire repository

- **Type checking:** `mypy` — not strict yet, but new code must be typed wherever possible.

- **__init__.py:** Only root `/noc/__init__.py` may contain code (module loader). All other `__init__.py` files MUST be empty (`# type: ignore`).

- **Language:** English only in code artifacts — comments, docstrings, logs, CLI output, configs. Never Russian or any other language.

- **FastAPI Response:** use `JSONResponse(content=data)`, NOT ~~`ORJSONResponse`~~ — it's deprecated and Pydantic-native serialization is faster.

## Encoding

NOC uses UTF-8 for all text data — no `smart_text()` needed. All strings, HTTP responses, ClickHouse query results, and file I/O are UTF-8. Python `.decode()` with the default UTF-8 encoding is sufficient; never fall back to `smart_text` as a "safe" alternative.

## Architecture

### Applications (Django-style)
Each application is a top-level directory with the same structure:

```<app>
  migrations/   # migration set for this app
  models/       # ORM models, each in own module
  handlers/     # handlers functions
```

All applications below share this same structure. Thea are enumerated in `INSTALLED_APPS` constant in `settings.py`. They will eventually be collapsed into a single consolidated directory in future:

- `aaa` `bi`, `cm`,  `crm`, `dev`, `dns`, `fm`, `gis`, `inv`, `ip`, `kb`, `main`, `maintenance`, `peer`, `phone`, `pm`, `project`, `sa`, `sla`, `support`, `vc`, `wf`

Each application contains its own set of models and migrations. Some are business logic modules (e.g., `fm/` for fault management, `inv/` for inventory), some are utility apps with no models but supporting services (e.g., `main/` for system configuration). Do not assume a directory maps to a single model — each contains an app registry entry, and the models inside define the domain.

### Core Framework (`core/`)
Shared infrastructure services — these are NOT Django apps. They provide framework-level functionality used across domains. Each module is a standalone component:

- `ioloop/` — Event loop utilities (async scheduling engine)
- `cache/` — Redis/memcached abstraction
- `http/` — HTTP client/facade
- `loader/` — Plugin loading mechanism
- `protocol/` — Model decorators
- `models/` — Dataclass definitions
- `mongo/` — MongoDB integration, custom field types
- `confdb/` — Configuration database utilities
- `protocols/` — Python Protocol type definitions
- `datastream/` — Data stream infrastructure
- `datasources/` — Telemetry pipelines

### Services (`services/`)
Microservices running one or more independent instances. Each exposes a specific function:

- `web/` — Django-based web server (main app entry point)
- `runner/` — Scheduled task scheduler
- `worker/` — Async background job processor
- `nbi/` — Northbound Interface API
- Others: mib, ping, classifier, correlator, selfmon, topo, syslogcollector, etc.

Some services are pooled (i.e., serving managed objects from dedicated pool). Each service may contain card templates (`templates/`) for the NOC UI; see Templates below.

### CLI Commands (`commands/`)
CLI binaries live in `commands/`. Each command is implemented as a module class with a `run()` entry point. They are invoked via `./noc <command_name>`. Do not add CLI commands directly to Python files — always use the commands directory structure. Examples: `./noc collection sync`, `./noc fix apply <name>`.

### Fixes (`fixes/`)
Data correction scripts for fixing database errors. These are NOT run automatically — they must be triggered explicitly by a user or tech support engineer at their recommendation. They are invoked via `./noc fix apply <fix_name>`. Each fix in the directory is a self-contained data correction routine; never add new logic to a running service just to "patch" a data issue.

### Compiled MIBs (`cmibs/`)
Python modules generated from raw SNMP MIB files. Produced by the CLI command `./noc mib make-cmib`. These allow symbolic variable names in code instead of raw OIDs; they are generated artifacts, NOT source files. Do not edit `cmibs/` manually — regenerate via CLI when original MIBs change.

### Collections (`collections/`)
Data seeding mechanism for reference data (MIBs, model types, workflow definitions). Pushed to live installations via `./noc collection sync`. Sync compares collection contents against the database and adds/updates/deletes records. Do not manually edit under collections — these are meant to be imported into version control and pushed to environments.

### Templates (`templates/`)
Jinja2 templates for card rendering in NOC UI. Each may have its own namespace for template lookup. Not Django templates — use only Jinja2 syntax. See `services/<domain>/` for card-specific template references.

## Zone Files (Documentation Boundaries)

These are NOT code directories — they mark logical documentation boundaries for the project:

- **[tests/AGENTS.md](tests/AGENTS.md)** — pytest fixtures, infrastructure containers (Postgres/MongoDB/ClickHouse/Kafka), CI py-tests.yml
- **[ui/AGENTS.md](ui/AGENTS.md)** — frontend TypeScript workspaces, webpack bundles, Playwright E2E testing
- **[ansible/AGENTS.md](ansible/AGENTS.md)** — NOC provisioning roles, system_roles, custom library/lookup_plugins, Molecule test suites
- **[sa/profiles/AGENTS.md](sa/profiles/AGENTS.md)** — device profiles (108+ vendors), SNMP MIB rules, custom_path cascade inheritance, OID conventions per model
- **[docs/AGENTS.md](docs/AGENTS.md)** — MkDocs-material build chain, multi-language docs structure (en/ru), documentation style guide and contributing process

Load the relevant zone file from above ONLY when working in that context. Root AGENTS.md remains the single source of truth for shared conventions.

## CI/CD Pipeline

All automation lives in `.github/workflows/`:

- `py-tests.yml` — Python tests + ruff linting + coverage upload
- `js-tests.yml` — JavaScript/TypeScript linting
- `infra-image.yml` — Infrastructure image build
- `docker-master.yml` — Docker image publication on master/main branch only
- `build-docs.yml` — MkDocs documentation generation
- `ui-master.yml` — UI bundle and deployment
- `codeql.yml` — Security scanning via CodeQL

Python changes must pass py-tests.yml linting before merge. JavaScript → js-tests.yml. Docker images are published on master/main branch only.

## Legacy / Unmaintained

- **[docker/](docker/)** — Old test infrastructure (legacy docker-compose). Deprecated, unmaintained, and no longer relevant. Do not reference or modify this directory for any task.
- **`dist/`, `requirements/`, `var/`** — Build artifacts, old dependency files, and runtime data directories. Never check into version control. Treat as auto-generated / ephemeral.

## Licensing

NOC is copyrighted by Gufo Labs (2007–present). The license allows redistribution under BSD-style terms but **strictly prohibits**:

- Derivative products (any software/service based on or incorporating this code) without explicit written permission from Gufo Labs
- Commercial use — selling modified versions, bundling within a proprietary product, offering SaaS based on this code require prior written consent
- Use to develop competing commercial solutions without authorization

Any work you are doing that produces a derivative product must have been authorized by Gufo Labs in writing. If you are unsure whether your work constitutes a derivative product, ask the user first — do not proceed without confirming they have or will obtain the required permission from Gufo Labs.
