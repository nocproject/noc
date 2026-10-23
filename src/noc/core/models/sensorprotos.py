# ----------------------------------------------------------------------
# Sensor Metric Protocols types
# ----------------------------------------------------------------------
# Copyright (C) 2007-2025 The NOC Project
# See LICENSE for details
# ----------------------------------------------------------------------

# Python modules
import enum


class SensorProtocol(enum.Enum):
    MODBUS_RTU = "modbus_rtu"
    MODBUS_ASCII = "modbus_ascii"
    MODBUS_TCP = "modbus_tcp"
    SNMP = "snmp"
    IPMI = "ipmi"
    REMOTE_PULL = "remote_pull"
    REMOTE_PUSH = "remote_push"
    OTHER = "other"
