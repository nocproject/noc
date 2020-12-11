# ---------------------------------------------------------------------
# Vendor: Qtech
# OS:     QFC
# ---------------------------------------------------------------------
# Copyright (C) 2007-2020 The NOC Project
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
        6: "Цифровой выход",
        7: "V220",
        8: "Внутренний датчик температуры",
        9: "Наружный датчик температуры",
        13: "Вход сигнала ИБП",
        27: "Вход сигнала Счетчика",
    }

    LIGHT_PORT_TYPE = {
        5: "Цифровой вход 1",
        6: "Цифровой вход 2",
        7: "Цифровой вход 3",
        8: "Цифровой вход 4",
        9: "Реле 1",
        10: "Реле 2",
        12: "V220",
        13: "Внутренний датчик температуры",
        14: "Наружный датчик температуры",
        29: "Вход сигнала Счетчика",
    }

    LITE_IFACE_NAME = {
        5: "input",
        6: "output",
        7: "v220",
        8: "tempIn",
        9: "tempOut",
        13: "ups",
        27: "elMeter",
    }
    LIGHT_IFACE_NAME = {
        5: "in1",
        6: "in2",
        7: "in3",
        8: "in4",
        9: "relay1",
        10: "relay2",
        12: "V220",
        13: "tempIn",
        14: "tempOut",
        29: "elMeter",
    }
