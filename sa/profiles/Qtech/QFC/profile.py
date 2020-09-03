# ---------------------------------------------------------------------
# Vendor: Qtech
# OS:     BFC_PBIC_S
# ---------------------------------------------------------------------
# Copyright (C) 2007-2018 The NOC Project
# See LICENSE for details
# ---------------------------------------------------------------------


# Python module
import re

# NOC module
from noc.core.profile.base import BaseProfile
from noc.core.snmp.get import parse_get_response_strict


class Profile(BaseProfile):
    name = "Qtech.QFC"
    # to one SNMP GET request
    snmp_metrics_get_chunk = 1
    # Timeout for snmp GET request
    snmp_metrics_get_timeout = 5

    snmp_response_parser = parse_get_response_strict

    matchers = {
        "is_lite": {"platform": {"$regex": "QFC-PBIC-LITE"}},
    }

    rx_interface_name = re.compile(r"^\d+$")

    PORT_TYPE = {
        5: "Цифровой вход",
        6: "Реле",
        8: "Внутренний датчик температуры",
        9: "Наружный датчик температуры",
        13: "Вход сигнала ИБП",
        27: "Вход сигнала Счетчика",
    }

    IFACE_NAME = {5: "input", 6: "relay", 8: "tempIn", 9: "tempOut", 13: "ups", 27: "elMeter"}

    def convert_interface_name(self, s):
        """
        >>> Profile().convert_interface_name("5")
        'temp1'
        """
        match = self.rx_interface_name.match(s)
        if not match:
            return s
        else:
            return self.IFACE_NAME.get(int(s))

    def check_oid(self):
        if self.is_lite:
            return 103
        return 102
