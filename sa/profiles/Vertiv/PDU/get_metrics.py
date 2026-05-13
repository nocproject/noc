# ---------------------------------------------------------------------
# Vertiv.PDU.get_metrics
# ---------------------------------------------------------------------
# Copyright (C) 2007-2026 The NOC Project
# See LICENSE for details
# ---------------------------------------------------------------------

# NOC modules
from noc.sa.profiles.Generic.get_metrics import Script as GetMetricsScript
from noc.core.script.metrics import scale


class Script(GetMetricsScript):
    name = "Vertiv.PDU.get_metrics"

    SENSOR_OID_SCALE = {
        "1.3.6.1.4.1.21239.5.2.3.2.1.4.1": scale(0.1, 2),
        "1.3.6.1.4.1.21239.5.2.3.2.1.4.2": scale(0.1, 2),
        "1.3.6.1.4.1.21239.5.2.3.2.1.4.3": scale(0.1, 2),
        "1.3.6.1.4.1.21239.5.2.3.2.1.8.1": scale(0.01, 2),
        "1.3.6.1.4.1.21239.5.2.3.2.1.8.2": scale(0.01, 2),
        "1.3.6.1.4.1.21239.5.2.3.2.1.8.3": scale(0.01, 2),
    }
