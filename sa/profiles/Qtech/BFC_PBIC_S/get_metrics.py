# ---------------------------------------------------------------------
# Qtech.BFC_PBIC_S.get_metrics
# ---------------------------------------------------------------------
# Copyright (C) 2007-2020 The NOC Project
# See LICENSE for details
# ---------------------------------------------------------------------

# NOC modules
from noc.sa.profiles.Generic.get_metrics import Script as GetMetricsScript, metrics
from noc.core.script.metrics import scale


class Script(GetMetricsScript):
    name = "Qtech.BFC_PBIC_S.get_metrics"
