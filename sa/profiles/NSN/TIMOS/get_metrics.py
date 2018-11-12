# -*- coding: utf-8 -*-
# ----------------------------------------------------------------------
# NSN.TIMOS.get_metrics
# ----------------------------------------------------------------------
# Copyright (C) 2007-2018 The NOC Project
# See LICENSE for details
# ----------------------------------------------------------------------

from noc.sa.profiles.Generic.get_metrics import Script as GetMetricsScript
from noc.core.script.metrics import percent


class Script(GetMetricsScript):
    name = "NSN.TIMOS.get_metrics"
