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

    LITE_PORT_TYPE = {
        5: "Цифровой вход",
        6: "Реле",
        8: "Внутренний датчик температуры",
        9: "Наружный датчик температуры",
        13: "Вход сигнала ИБП",
        27: "Вход сигнала Счетчика",
    }

    LIGHT_PORT_TYPE = {
        5: "Цифровой вход",
        6: "Реле",
        9: "Датчик температуры 1",
        10: "Датчик температуры 2",
        13: "Вход сигнала ИБП",
        16: "Вход сигнала Счетчика",
    }

    LITE_IFACE_NAME = {5: "input", 6: "relay", 8: "tempIn", 9: "tempOut", 13: "ups", 27: "elMeter"}
    LIGHT_IFACE_NAME = {5: "input", 6: "relay", 8: "temp1", 9: "temp2", 16: "elMeter"}
