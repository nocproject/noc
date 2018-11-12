# -*- coding: utf-8 -*-
# ----------------------------------------------------------------------
# Ensure ClickHouse database schema
# ----------------------------------------------------------------------
# Copyright (C) 2007-2018 The NOC Project
# See LICENSE for details
# ----------------------------------------------------------------------

# Python modules
from __future__ import absolute_import
import os
import logging
# NOC modules
from noc.config import config
from .loader import loader

logger = logging.getLogger(__name__)
BIMODELS_PREFIX = os.path.join("bi", "models")


def ensure_bi_models(connect=None):
    logger.info("Ensuring BI models:")
    # Ensure fields
    changed = False
    for name in loader.iter_models():
        model = loader.get_model(name)
        if not model:
            continue
        logger.info("Ensure table %s" % model._meta.db_table)
        changed |= model.ensure_table(connect=connect)
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
    for host, port in ch.execute("SELECT host_address, port FROM system.clusters WHERE cluster = %s",
                                 args=[config.clickhouse.cluster]):
        c = connection(host=host, port=port, read_only=False)
        ensure_pm_scopes(c)
