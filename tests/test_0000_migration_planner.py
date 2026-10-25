# ----------------------------------------------------------------------
# Migration planner tests
# ----------------------------------------------------------------------
# Copyright (C) 2007-2026 The NOC Project
# See LICENSE for details
# ----------------------------------------------------------------------

# Python modules
from pathlib import Path

# NOC modules
from noc.config import config
from noc.core.migration.runner import MigrationRunner
from noc.settings import INSTALLED_APPS


def test_migration_plan() -> None:
    """Check migration discovery and explicit dependency ordering."""
    plan = list(MigrationRunner.iter_plan())
    plan_names = [migration.get_name() for migration in plan]

    expected_names: set[str] = set()
    custom_path = Path(config.path.custom_path) if config.path.custom_path else None
    for app in INSTALLED_APPS:
        if not app.startswith("noc."):
            continue
        app = app[4:]
        for path in config.get_customized_paths(app, "migrations"):
            root = Path(path)
            is_custom = custom_path is not None and root.is_relative_to(custom_path)
            if not root.is_absolute() and not is_custom:
                root = config.noc_base / root
            expected_names.update(
                f"{app}.{migration_path.stem}"
                for migration_path in root.rglob("*.py")
                if migration_path.stem not in {"__init__", "init"}
            )

    actual_names = set(plan_names)
    assert len(plan_names) == len(actual_names), "Migration plan contains duplicate migrations"
    assert actual_names == expected_names, (
        f"Migration plan mismatch: missing={sorted(expected_names - actual_names)}, "
        f"unexpected={sorted(actual_names - expected_names)}"
    )

    positions: dict[str, int] = {
        migration_name: position for position, migration_name in enumerate(plan_names)
    }
    for migration in plan:
        migration_name = migration.get_name()
        for dependency_app, dependency_name in migration.depends_on:
            dependency = f"{dependency_app}.{dependency_name}"
            assert dependency in positions, (
                f"{migration_name} depends on missing migration {dependency}"
            )
            assert positions[dependency] < positions[migration_name], (
                f"{migration_name} is scheduled before dependency {dependency}"
            )
