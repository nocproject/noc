# ---------------------------------------------------------------------
# Rotek.BT.get_metrics
# ---------------------------------------------------------------------
# Copyright (C) 2007-2022 The NOC Project
# See LICENSE for details
# ---------------------------------------------------------------------

# NOC modules
from noc.sa.profiles.Generic.get_metrics import Script as GetMetricsScript
from noc.core.script.metrics import scale


class Script(GetMetricsScript):
    name = "Rotek.BT.get_metrics"

    SENSOR_OID_SCALE = {
        "1.3.6.1.4.1.41752.911.10.1.2.0": scale(0.01, 2),
        "1.3.6.1.4.1.41752.911.10.1.3.0": scale(0.01, 2),
        "1.3.6.1.4.1.41752.911.10.1.4.0": scale(0.01, 2),
        "1.3.6.1.4.1.41752.911.10.1.5.0": scale(0.01, 2),
        "1.3.6.1.4.1.41752.911.10.1.6.0": scale(0.01, 2),
        "1.3.6.1.4.1.41752.911.10.1.13.2.0": scale(0.01, 2),
        "1.3.6.1.4.1.41752.911.10.1.13.3.0": scale(0.001, 2),
        "1.3.6.1.4.1.41752.911.10.1.13.4.0": scale(0.01, 2),
        "1.3.6.1.4.1.41752.911.10.1.13.5.0": scale(0.01, 2),
        "1.3.6.1.4.1.41752.911.10.1.13.6.0": scale(0.01, 2),
        "1.3.6.1.4.1.41752.911.10.1.13.7.0": scale(0.01, 2),
        "1.3.6.1.4.1.41752.911.10.1.13.8.0": scale(0.01, 2),
        "1.3.6.1.4.1.41752.911.10.1.13.9.0": scale(0.01, 2),
        "1.3.6.1.4.1.41752.911.10.1.13.10.0": scale(0.000001, 2),
        "1.3.6.1.4.1.41752.911.10.1.13.13.0": scale(0.001, 2),
    }
