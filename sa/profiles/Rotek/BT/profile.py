# ---------------------------------------------------------------------
# Vendor: Rotek
# OS:     BT
# ---------------------------------------------------------------------
# Copyright (C) 2007-2020 The NOC Project
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

    matchers = {
        "is_4250lsr": {"platform": {"$regex": r"4250LSR"}},
        "is_6037_v1": {"platform": {"$regex": r"6037.+[Vv]1"}},
    }

    PORT_TYPE = {
        1: "Порт датчика двери",
        2: "Порт датчика температуры",
        4: "Порт нагрузки",
        6: "Порт АКБ",
        9: "Порт мониторинга напряжения сети",
    }

    IFACE_NAME = {1: "door", 2: "temperature", 4: "load", 6: "ups", 9: "v220"}
