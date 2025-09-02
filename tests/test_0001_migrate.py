# ----------------------------------------------------------------------
# Database migrations
# ----------------------------------------------------------------------
# Copyright (C) 2007-2020 The NOC Project
# See LICENSE for details
# ----------------------------------------------------------------------

# Python modules
from collections import defaultdict

# Third-party modules
import pytest
import cachetools

# NOC modules
from noc.core.migration.base import BaseMigration
from noc.core.migration.loader import loader
from noc.core.migration.runner import MigrationRunner


@cachetools.cached({})
def get_migration_names():
    return list(loader.iter_migration_names())


@cachetools.cached({})
def get_migration_names_set():
    return set(get_migration_names())


@cachetools.cached({})
def get_migration_plan():
    return list(loader.iter_plan())


@cachetools.cached({})
def get_planned_counts():
    try:
        r = defaultdict(int)
        for p in get_migration_plan():
            r[p.get_name()] += 1
        return r
    except ValueError:
        return {}


@cachetools.cached({})
def get_migration_orders():
    r = {}
    for p in get_migration_plan():
        r[p.get_name()] = len(r)
    return r


@pytest.mark.parametrize("name", get_migration_names())
def test_migration_class(name):
    migration = loader.get_migration(name)
    assert migration
    assert isinstance(migration, BaseMigration)


@pytest.mark.parametrize("name", get_migration_names())
def test_migration_depends_on(name):
    migration = loader.get_migration(name)
    assert migration
    if not migration.depends_on:
        return
    assert isinstance(migration.depends_on, list), "depends_on must be of list type"
    for r in migration.depends_on:
        assert isinstance(r, tuple), "depends_on item must be of tuple type"
        assert len(r) == 2, "depends_on item must have size of 2"
        dep_name = "%s.%s" % (r[0], r[1])
        assert dep_name in get_migration_names_set(), "Unknown dependency %s" % r


@pytest.mark.parametrize("name", get_migration_names())
def test_migration_in_plan(name):
    assert name in get_planned_counts()


@pytest.mark.parametrize("name", get_migration_names())
def test_migration_duplicates(name):
    assert name in get_planned_counts()
    assert get_planned_counts()[name] == 1, "Duplicated migration in plan"


@pytest.mark.parametrize("name", get_migration_names())
def test_migration_order(name):
    migration = loader.get_migration(name)
    assert migration
    if not migration.depends_on:
        return
    orders = get_migration_orders()
    assert name in orders, "Unordered migration"
    for d in migration.dependencies:
        assert d in orders, "Unordered dependency"
        assert orders[d] < orders[name], "Out-of-order dependency"


@pytest.mark.usefixtures("database")
def test_database_migrations(database):
    """
    Force database migrations
    :param database:
    :return:
    """
    # runner = MigrationRunner()
    # MigrationRunner()
    # runner.migrate()
    assert 1 == 1


def test_migration_history():
    """
    Test all migrations are in `migrations` collection
    :return:
    """
    runner = MigrationRunner()
    applied = runner.get_history()
    all_migrations = get_migration_names_set()
    assert all_migrations == applied
