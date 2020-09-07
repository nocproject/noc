# ---------------------------------------------------------------------
# Vendor: Rotek
# OS:     BT
# ---------------------------------------------------------------------
# Copyright (C) 2007-2017 The NOC Project
# See LICENSE for details
# ---------------------------------------------------------------------

# NOC modules
from noc.core.profile.base import BaseProfile


class Profile(BaseProfile):
    name = "Rotek.BT"
    # to one SNMP GET request
    snmp_metrics_get_chunk = 2
    # Timeout for snmp GET request
    snmp_metrics_get_timeout = 3

    PORT_TYPE = {
        1: "Порт датчика двери",
        2: "Порт датчика температуры",
        3: "Порт нагрузки",
        5: "Порт АКБ",
        9: "Порт мониторинга напряжения сети",
    }

    IFACE_NAME = {1: "door", 2: "temperature", 3: "load", 5: "ups", 9: "v220"}
