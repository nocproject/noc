# -*- coding: utf-8 -*-
##----------------------------------------------------------------------
## Huawei.VRP.get_metrics
##----------------------------------------------------------------------
## Copyright (C) 2007-2016 The NOC Project
## See LICENSE for details
##----------------------------------------------------------------------

from noc.sa.profiles.Generic.get_metrics import Script as GetMetricsScript
from noc.core.script.metrics import percent


class Script(GetMetricsScript):
    name = "Huawei.VRP.get_metrics"

