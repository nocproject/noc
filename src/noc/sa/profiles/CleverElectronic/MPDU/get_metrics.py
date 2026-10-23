# ---------------------------------------------------------------------
# CleverElectronic.MPDU.get_metrics
# ---------------------------------------------------------------------
# Copyright (C) 2007-2026 The NOC Project
# See LICENSE for details
# ---------------------------------------------------------------------

# NOC modules
from noc.sa.profiles.Generic.get_metrics import Script as GetMetricsScript
from noc.core.script.metrics import scale


class Script(GetMetricsScript):
    name = "CleverElectronic.MPDU.get_metrics"

    SENSOR_OID_SCALE = {
        "1.3.6.1.4.1.30966.8.1.2.1.4.0": scale(100, 2),
        "1.3.6.1.4.1.30966.8.1.2.2.4.0": scale(100, 2),
        "1.3.6.1.4.1.30966.8.1.2.3.4.0": scale(100, 2),
    }
