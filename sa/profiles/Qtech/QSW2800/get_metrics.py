# -*- coding: utf-8 -*-
# ---------------------------------------------------------------------
# Qtech.QSW2800.get_metrics
# ---------------------------------------------------------------------
# Copyright (C) 2007-2019 The NOC Project
# See LICENSE for details
# ---------------------------------------------------------------------

# Python modules
from __future__ import absolute_import

# NOC modules
from noc.sa.profiles.Generic.get_metrics import Script as GetMetricsScript
from .oidrules.slot import SlotRule
from .oidrules.enterprise import EnterpriseRule


class Script(GetMetricsScript):
    name = "Qtech.QSW2800.get_metrics"

    OID_RULES = [SlotRule, EnterpriseRule]
