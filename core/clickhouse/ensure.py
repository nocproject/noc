# ----------------------------------------------------------------------
# Ensure ClickHouse database schema
# ----------------------------------------------------------------------
# Copyright (C) 2007-2018 The NOC Project
# See LICENSE for details
# ----------------------------------------------------------------------

# Python modules
import logging

# NOC modules
from noc.config import config
from .loader import loader
from ..bi.dictionaries.loader import loader as bi_dictionary_loader

logger = logging.getLogger(__name__)


def ensure_bi_models(connect=None):
    logger.info("Ensuring BI models:")
    # Ensure fields
    changed = False
    for name in loader:
        model = loader[name]
        if not model:
            continue
        logger.info("Ensure table %s" % model._meta.db_table)
        changed |= model.ensure_schema(connect=connect)
        changed |= model.ensure_table(connect=connect)
        changed |= model.ensure_views(connect=connect, changed=changed)
    return changed


def ensure_dictionary_models(connect=None):
    logger.info("Ensuring Dictionaries:")
    # Ensure fields
    changed = False
    for name in bi_dictionary_loader:
        model = bi_dictionary_loader[name]
        if not model:
            continue
        logger.info("Ensure dictionary %s" % model._meta.db_table)
        table_changed = model.ensure_table(connect=connect)
        changed |= table_changed
        if table_changed:
            logger.info("[%s] Drop Dictionary", name)
            model.drop_dictionary(connect=connect)
            model.ensure_views(connect=connect)
        changed |= model.ensure_dictionary(connect=connect)
    return changed


def ensure_pm_scopes(connect=None):
    from noc.pm.models.metricscope import MetricScope

    logger.info("Ensuring PM scopes")
    changed = False
    for s in MetricScope.objects.all():
        logger.info("Ensure scope %s" % s.table_name)
        changed |= s.ensure_table(connect=connect)
    return changed


def ensure_all_pm_scopes():
    from noc.core.clickhouse.connect import connection

    if not config.clickhouse.cluster or config.clickhouse.cluster_topology == "1":
        # Standalone configuration
        ensure_pm_scopes()
        return
    # Replicated configuration
    ch = connection(read_only=False)
    for host, port in ch.execute(
        "SELECT host_address, port FROM system.clusters WHERE cluster = %s",
        args=[config.clickhouse.cluster],
    ):
        c = connection(host=host, port=port, read_only=False)
        ensure_pm_scopes(c)


def ensure_report_ds_scopes(connect=None):
    from noc.core.datasources.loader import loader

    logger.info("Ensuring Report BI")
    changed = False
    for ds in loader:
        ds = loader[ds]
        if not ds.clickhouse_mirror:
            continue
        logger.info("Ensure Report DataSources %s", ds.name)
        changed |= ds.ensure_table(connect=connect)
    return changed
