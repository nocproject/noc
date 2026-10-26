# ----------------------------------------------------------------------
# Ensure ClickHouse database schema
# ----------------------------------------------------------------------
# Copyright (C) 2007-2026 The NOC Project
# See LICENSE for details
# ----------------------------------------------------------------------

# Python modules
import logging

# NOC modules
from noc.config import config

from ..bi.dictionaries.loader import loader as bi_dictionary_loader
from .connect import ClickhouseClient, connection
from .info import TableInfo
from .loader import loader

logger = logging.getLogger(__name__)


def ensure_bi_models(connect: ClickhouseClient | None = None, allow_type: bool = False) -> bool:
    logger.info("Ensuring BI models:")
    # Ensure fields
    allow_type |= config.clickhouse.enable_migrate_type
    changed = False
    for name in loader:
        model = loader[name]
        if not model:
            continue
        logger.info(f"Ensure table {model._meta.db_table}")
        changed |= model.ensure_schema(connect=connect)
        changed |= model.ensure_table(connect=connect)
        changed |= model.ensure_views(connect=connect, changed=changed)
    return changed


def ensure_dictionary_models(
    connect: ClickhouseClient | None = None, allow_type: bool = False
) -> bool:
    logger.info("Ensuring Dictionaries:")
    # Ensure fields
    allow_type |= config.clickhouse.enable_migrate_type
    changed = False
    for name in bi_dictionary_loader:
        model = bi_dictionary_loader[name]
        if not model:
            continue
        logger.info(f"Ensure dictionary {model._meta.db_table}")
        table_changed = model.ensure_table(connect=connect)
        changed |= table_changed
        if table_changed:
            logger.info("[%s] Drop Dictionary", name)
            model.drop_dictionary(connect=connect)
            model.ensure_views(connect=connect)
        changed |= model.ensure_dictionary(connect=connect)
    return changed


def ensure_pm_scopes(connect: ClickhouseClient | None = None, allow_type: bool = False) -> bool:
    # NOC modules
    from noc.pm.models.metricscope import MetricScope

    logger.info("Ensuring PM scopes")
    allow_type |= config.clickhouse.enable_migrate_type
    changed = False
    for s in MetricScope.objects.all():
        logger.info(f"Ensure scope {s.table_name}")
        changed |= s.ensure_table(connect=connect, allow_type=allow_type)
    return changed


def ensure_all_pm_scopes() -> bool:
    if not config.clickhouse.cluster or config.clickhouse.cluster_topology == "1":
        # Standalone configuration
        return ensure_pm_scopes()
    # Replicated configuration
    ch = connection(read_only=False)
    for host, port in ch.execute(
        "SELECT host_address, port FROM system.clusters WHERE cluster = %s",
        args=[config.clickhouse.cluster],
    ):
        c = connection(host=host, port=port, read_only=False)
        ensure_pm_scopes(c)


def ensure_report_ds_scopes(
    connect: ClickhouseClient | None = None, allow_type: bool = False
) -> bool:
    # NOC modules
    from noc.core.datasources.base import data_source_loader

    logger.info("Ensuring Report BI")
    allow_type |= config.clickhouse.enable_migrate_type
    changed = False
    for ds in data_source_loader:
        ds = data_source_loader.get(ds)
        if not hasattr(ds, "name"):
            continue
        if not ds.clickhouse_mirror():
            logger.info("[%s] Clickhouse mirror not enabled. Skipping", ds.name)
            continue
        logger.info("Ensure Report DataSources %s", ds.name)
        changed |= ds.ensure_table(connect=connect)
        changed |= ds.ensure_views(connect=connect)
    return changed


def sync_ch_policies() -> bool:
    """Create CHPolicy when necessary."""
    # NOC modules
    from noc.main.models.chpolicy import CHPolicy
    from noc.pm.models.metricscope import MetricScope

    seen = {p.table for p in CHPolicy.objects.all()}
    # Collect tables from pm scopes
    tables: list[str] = [ms._get_raw_db_table() for ms in MetricScope.objects.all()]
    # Collect BI models
    for name in loader:
        model = loader[name]
        if model:
            tables.append(model._get_raw_db_table())
    # Create CHPolicy
    changed = False
    for t in tables:
        if t not in seen:
            CHPolicy(table=t, is_active=False, ttl=0).save()
            changed = True
    return changed


DAY = 24 * 3600


def ensure_ch_policies(connect: ClickhouseClient | None = None) -> bool:
    # NOC modules
    from noc.main.models.chpolicy import CHPolicy

    changed = False
    policy_ttl: dict[str, int] = {
        p.table: p.ttl * DAY for p in CHPolicy.objects.filter(is_active=True)
    }
    if not policy_ttl:
        return changed
    for ti in TableInfo.iter_for_tables(policy_ttl):
        ttl = policy_ttl.get(ti.name) or 0
        if ttl == ti.table_ttl:
            continue  # Already applied
        if ttl:
            logger.info("[%s] setting ttl to %s", ti.name, ttl)
            sql = f"ALTER TABLE {ti.name} MODIFY TTL ts + INTERVAL {ttl} SECOND"
        else:
            logger.info("[%s] disabling ttl", ti.name)
            sql = f"ALTER TABLE {ti.name} REMOVE TTL"
        if connect is None:
            connect = connection()
        connect.execute(sql)
    return changed
