# -*- coding: utf-8 -*-
# ----------------------------------------------------------------------
# Ensure ClickHouse database schema
# ----------------------------------------------------------------------
# Copyright (C) 2007-2017 The NOC Project
# See LICENSE for details
# ----------------------------------------------------------------------

# Python modules
import os
import logging

logger = logging.getLogger(__name__)


def ensure_bi_models(connection=None):
    from noc.core.clickhouse.model import Model

    logger.info("Ensuring BI models:")
    models = set()
    # Get models
    for f in os.listdir("bi/models"):
        if f.startswith("_") or not f.endswith(".py"):
            continue
        mn = f[:-3]
        model = Model.get_model_class(mn)
        if model:
            models.add(model)
    # Ensure fields
    changed = False
    for model in models:
        logger.info("Ensure table %s" % model._meta.db_table)
        changed |= model.ensure_table(connect=connection)
    return changed


def ensure_pm_scopes(connection=None):
    from noc.pm.models.metricscope import MetricScope
    logger.info("Ensuring PM scopes")
    changed = False
    for s in MetricScope.objects.all():
        logger.info("Ensure scope %s" % s.table_name)
        changed |= s.ensure_table(connect=connection)
    return changed
