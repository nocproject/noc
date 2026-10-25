# NOC Tests — Agent Guidelines

## Test Architecture

Tests run via **pytest**. All configuration lives in `tests/conftest.py`. The test suite manages a full infrastructure stack: PostgreSQL, MongoDB, ClickHouse, Kafka, plus custom test containers (dropbear SSHD, telnetd, SNMPD, SSHTD). No real Docker daemons or external services are required — everything spins up via fixtures.

### pytest markers
- `@pytest.mark.run_on_setup` — these tests run first (database initialization only). Use for setup tests that must complete before any other test runs.
- `@with_timing(name)` — decorator in conftest.py that measures execution time of wrapped functions and tracks them for the terminal summary report. Used for performance measurement.

### Test file naming
All test files: `test_<name>.py` (snake_case). Directory-organized tests match domain structure under `tests/<domain>/`.

```
tests/                      # root-level standalone unit tests
  conftest.py              # pytest configuration, fixtures, timing
  utils.py                 # shared utilities (check_protocol, etc.)
  test_0000_init_db.py     # database initialization marker
  ...                      # many standalone unit tests for core modules
  
tests/<domain>/            # domain-specific integration tests
  <vendor>/                # vendor- or platform-specific subtests
  factory/                  # builder patterns for complex objects
  collator/                 # confdb collation logic
  normalizer/               # normalization test cases
  syntax/                   # parsing syntax test suites
```

## Test Types and When to Use Each

### Unit Tests (`tests/test_*.py`)
For functions, modules, and classes without dependencies. Fast, isolated tests under 1 second each. These get grouped with "other tests" in timing summary if under THRESHOLD (configurable, typically 1s).

### Integration Tests (`tests/<domain>/`)
For features requiring database interaction, external protocol communication, or multi-module coordination. These use `database` fixture which:
1. Creates PostgreSQL, MongoDB, ClickHouse, Kafka service containers via Docker Compose infrastructure
2. Runs migrations (PostgreSQL + ClickHouse) via migration commands
3. Syncs collections from the `collections/` directory for reference data
4. Loads MIBs and JSON fixtures
5. Ensures indexes are built

### Database fixture lifecycle
```python
@pytest.mark.run_on_startup
def test_init_db(database):  # database = session-scoped; setup first
    """Runs once per suite — triggers full DB initialization."""
```

Tests requiring the `database` fixture are deferred until after init tests complete. The `run_on_startup` marker ensures this ordering.

### Infrastructure containers (in CI)
The py-tests workflow spins up these services via --mount tmpfs for data:
- PostgreSQL 16 (port 5432): creds noc/noc/noc
- MongoDB 4.4 (port 27017): user noc, password noc, auth source admin
- ClickHouse 23 (port 8123): tmpfs-backed data dir
- Kafka 3.6.2 (port 9092/9093): single-node cluster
- testdropbear: SSH server for protocol tests port 10001
- testtelnetd: Telnet server port 10002
- testsnmpd: SNMP agent port 161/udp
- testsshd: another SSH server (OpenSSH, port 10004)

## Fixtures and Patterns

### Session-scoped fixtures in conftest.py
| Fixture         | Purpose                              | Scope   |
|------------------|--------------------------------------|---------|
| `db_postgres`    | Creates/cleans PostgreSQL test DB    | session |
| `db_mongo`       | Creates/cleans MongoDB test DB       | session |
| `db_clickhouse`  | Initializes ClickHouse for tests     | session |
| `db_kafka`       | Sets up test Kafka cluster           | session |
| `database`       | Full stack: creates + migrates data  | session |

Never use instance-scoped fixtures where session-scoped would work — creating DB instances per-test is slow and fragile. The `database` fixture handles the entire setup lifecycle.

### Fixture loading for test data
Fixtures are loaded from JSON files specified in `config.tests.fixtures_paths`. Each file contains an array of objects with schema:
```json
{
  "$model": "noc.main.models.Handler",
  "name": "test_handler",
  "description": "Test handler fixture"
}
```

Data fields prefixed with `$` are metadata. Non-prefixed fields map to model attributes or FK references. Cross-record FK references are supported — if a fixture field name matches an existing FK target, the loader resolves it automatically by querying the database. This means fixture import order does NOT matter.

### Protocol checking utility
Use `tests/utils.py::check_protocol` to verify an implementation class matches an expected interface:
```python
from tests.utils import check_protocol

check_protocol(ExpectedProtoClass, ActualImplClass)
```

## CI Pipeline

Run via `.github/workflows/py-tests.yml`:
1. **py-lint**: ruff format --diff + ruff check (quiet mode) — runs on all Python files including root directory
2. **py-test**: full test suite with --coverage (--cov, --cov-branch, --cov-report=xml)
3. Uploads coverage to Codecov ONLY on master branch push or if PR has the "coverage" label

### Run locally
```bash
# With coverage (slow):
pytest --maxfail=10 --cov --cov-branch --cov-report=text tests/

# Without coverage (fast):
pytest --maxfail=10 tests/
```

Environment variables are typically set in NOC settings — do NOT manually override them outside of CI/CI environment:
- `DJANGO_SETTINGS_MODULE=noc.settings`
- Database connection env vars (`NO*_ADDRESSES`) for all databases used by the test domain
- Service connection vars for Kafka, msgstream, etc.
- Feature flags via `NOC_FEATURES_*`

## Test Writing Conventions

1. **Test in the correct location:** unit tests go at root level (`test_<name>.py`), domain tests under `tests/<domain>/`. Keep unit tests fast — if a test uses the `database` fixture, it belongs in an integration directory rather than root.
2. **No mocks for external services** unless they are truly optional (SNMPD, Telnet servers). Always use the real infrastructure fixtures where available to catch real-world issues that mocked services won't reveal.
3. **Database fixtures:** always use session-scoped `database` fixture for DB-dependent tests. Never spin up DB per-test or per-function. The `run_on_setup` marker is required for any test that triggers database creation.
4. **Name tests descriptively:** function name should describe the scenario being tested, not just the method under test. Use `test_` prefix (snake_case) matching the pattern of existing test files.
