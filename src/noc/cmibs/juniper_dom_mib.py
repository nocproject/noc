# ----------------------------------------------------------------------
# JUNIPER-DOM-MIB
# Compiled MIB
# Do not modify this file directly
# Run ./noc mib make-cmib instead
# ----------------------------------------------------------------------
# Copyright (C) 2007-2024 The NOC Project
# See LICENSE for details
# ----------------------------------------------------------------------

# MIB Name
NAME = "JUNIPER-DOM-MIB"

# Metadata
LAST_UPDATED = "2018-02-11"
COMPILED = "2024-06-27"

# MIB Data: name -> oid
MIB = {
    "IF-MIB::ifDescr": "1.3.6.1.2.1.2.2.1.2",
    "IF-MIB::ifEntry": "1.3.6.1.2.1.2.2.1",
    "IF-MIB::ifIndex": "1.3.6.1.2.1.2.2.1.1",
    "IF-MIB::ifTable": "1.3.6.1.2.1.2.2",
    "IF-MIB::interfaces": "1.3.6.1.2.1.2",
    "JUNIPER-DOM-MIB::jnxDomAlarmCleared": "1.3.6.1.4.1.2636.4.18.0.2",
    "JUNIPER-DOM-MIB::jnxDomAlarmSet": "1.3.6.1.4.1.2636.4.18.0.1",
    "JUNIPER-DOM-MIB::jnxDomCurrentAlarmDate": "1.3.6.1.4.1.2636.3.60.1.1.1.1.2",
    "JUNIPER-DOM-MIB::jnxDomCurrentAlarms": "1.3.6.1.4.1.2636.3.60.1.1.1.1.1",
    "JUNIPER-DOM-MIB::jnxDomCurrentEntry": "1.3.6.1.4.1.2636.3.60.1.1.1.1",
    "JUNIPER-DOM-MIB::jnxDomCurrentModuleTemperature": "1.3.6.1.4.1.2636.3.60.1.1.1.1.8",
    "JUNIPER-DOM-MIB::jnxDomCurrentModuleTemperatureHighAlarmThreshold": "1.3.6.1.4.1.2636.3.60.1.1.1.1.21",
    "JUNIPER-DOM-MIB::jnxDomCurrentModuleTemperatureHighWarningThreshold": "1.3.6.1.4.1.2636.3.60.1.1.1.1.23",
    "JUNIPER-DOM-MIB::jnxDomCurrentModuleTemperatureLowAlarmThreshold": "1.3.6.1.4.1.2636.3.60.1.1.1.1.22",
    "JUNIPER-DOM-MIB::jnxDomCurrentModuleTemperatureLowWarningThreshold": "1.3.6.1.4.1.2636.3.60.1.1.1.1.24",
    "JUNIPER-DOM-MIB::jnxDomCurrentRxLaserPower": "1.3.6.1.4.1.2636.3.60.1.1.1.1.5",
    "JUNIPER-DOM-MIB::jnxDomCurrentRxLaserPowerHighAlarmThreshold": "1.3.6.1.4.1.2636.3.60.1.1.1.1.9",
    "JUNIPER-DOM-MIB::jnxDomCurrentRxLaserPowerHighWarningThreshold": "1.3.6.1.4.1.2636.3.60.1.1.1.1.11",
    "JUNIPER-DOM-MIB::jnxDomCurrentRxLaserPowerLowAlarmThreshold": "1.3.6.1.4.1.2636.3.60.1.1.1.1.10",
    "JUNIPER-DOM-MIB::jnxDomCurrentRxLaserPowerLowWarningThreshold": "1.3.6.1.4.1.2636.3.60.1.1.1.1.12",
    "JUNIPER-DOM-MIB::jnxDomCurrentTable": "1.3.6.1.4.1.2636.3.60.1.1.1",
    "JUNIPER-DOM-MIB::jnxDomCurrentTxLaserBiasCurrent": "1.3.6.1.4.1.2636.3.60.1.1.1.1.6",
    "JUNIPER-DOM-MIB::jnxDomCurrentTxLaserBiasCurrentHighAlarmThreshold": "1.3.6.1.4.1.2636.3.60.1.1.1.1.13",
    "JUNIPER-DOM-MIB::jnxDomCurrentTxLaserBiasCurrentHighWarningThreshold": "1.3.6.1.4.1.2636.3.60.1.1.1.1.15",
    "JUNIPER-DOM-MIB::jnxDomCurrentTxLaserBiasCurrentLowAlarmThreshold": "1.3.6.1.4.1.2636.3.60.1.1.1.1.14",
    "JUNIPER-DOM-MIB::jnxDomCurrentTxLaserBiasCurrentLowWarningThreshold": "1.3.6.1.4.1.2636.3.60.1.1.1.1.16",
    "JUNIPER-DOM-MIB::jnxDomCurrentTxLaserOutputPower": "1.3.6.1.4.1.2636.3.60.1.1.1.1.7",
    "JUNIPER-DOM-MIB::jnxDomCurrentTxLaserOutputPowerHighAlarmThreshold": "1.3.6.1.4.1.2636.3.60.1.1.1.1.17",
    "JUNIPER-DOM-MIB::jnxDomCurrentTxLaserOutputPowerHighWarningThreshold": "1.3.6.1.4.1.2636.3.60.1.1.1.1.19",
    "JUNIPER-DOM-MIB::jnxDomCurrentTxLaserOutputPowerLowAlarmThreshold": "1.3.6.1.4.1.2636.3.60.1.1.1.1.18",
    "JUNIPER-DOM-MIB::jnxDomCurrentTxLaserOutputPowerLowWarningThreshold": "1.3.6.1.4.1.2636.3.60.1.1.1.1.20",
    "JUNIPER-DOM-MIB::jnxDomCurrentWarnings": "1.3.6.1.4.1.2636.3.60.1.1.1.1.4",
    "JUNIPER-DOM-MIB::jnxDomDigitalMonitoring": "1.3.6.1.4.1.2636.3.60.1.1",
    "JUNIPER-DOM-MIB::jnxDomDigitalLaneMonitoring": "1.3.6.1.4.1.2636.3.60.1.2",
    "JUNIPER-DOM-MIB::jnxDomModuleLaneTable": "1.3.6.1.4.1.2636.3.60.1.2.1",
    "JUNIPER-DOM-MIB::jnxDomCurrentLaneEntry": "1.3.6.1.4.1.2636.3.60.1.2.1.1",
    "JUNIPER-DOM-MIB::jnxDomLaneIndex": "1.3.6.1.4.1.2636.3.60.1.2.1.1.1",
    "JUNIPER-DOM-MIB::jnxDomCurrentLaneAlarms": "1.3.6.1.4.1.2636.3.60.1.2.1.1.2",
    "JUNIPER-DOM-MIB::jnxDomCurrentLaneAlarmDate": "1.3.6.1.4.1.2636.3.60.1.2.1.1.3",
    "JUNIPER-DOM-MIB::jnxDomLaneLastAlarms": "1.3.6.1.4.1.2636.3.60.1.2.1.1.4",
    "JUNIPER-DOM-MIB::jnxDomCurrentLaneWarnings": "1.3.6.1.4.1.2636.3.60.1.2.1.1.5",
    "JUNIPER-DOM-MIB::jnxDomCurrentLaneRxLaserPower": "1.3.6.1.4.1.2636.3.60.1.2.1.1.6",
    "JUNIPER-DOM-MIB::jnxDomCurrentLaneTxLaserBiasCurrent": "1.3.6.1.4.1.2636.3.60.1.2.1.1.7",
    "JUNIPER-DOM-MIB::jnxDomCurrentLaneTxLaserOutputPower": "1.3.6.1.4.1.2636.3.60.1.2.1.1.8",
    "JUNIPER-DOM-MIB::jnxDomCurrentLaneLaserTemperature": "1.3.6.1.4.1.2636.3.60.1.2.1.1.9",
    "JUNIPER-DOM-MIB::jnxDomLastAlarms": "1.3.6.1.4.1.2636.3.60.1.1.1.1.3",
    "JUNIPER-DOM-MIB::jnxDomMib": "1.3.6.1.4.1.2636.3.60.1",
    "JUNIPER-DOM-MIB::jnxDomNotificationPrefix": "1.3.6.1.4.1.2636.4.18.0",
    "JUNIPER-SMI::jnxDomMibRoot": "1.3.6.1.4.1.2636.3.60",
    "JUNIPER-SMI::jnxDomNotifications": "1.3.6.1.4.1.2636.4.18",
    "JUNIPER-SMI::jnxMibs": "1.3.6.1.4.1.2636.3",
    "JUNIPER-SMI::jnxTraps": "1.3.6.1.4.1.2636.4",
    "JUNIPER-SMI::juniperMIB": "1.3.6.1.4.1.2636",
    "SNMPv2-SMI::dod": "1.3.6",
    "SNMPv2-SMI::enterprises": "1.3.6.1.4.1",
    "SNMPv2-SMI::internet": "1.3.6.1",
    "SNMPv2-SMI::iso": "1",
    "SNMPv2-SMI::mgmt": "1.3.6.1.2",
    "SNMPv2-SMI::mib-2": "1.3.6.1.2.1",
    "SNMPv2-SMI::org": "1.3",
    "SNMPv2-SMI::private": "1.3.6.1.4",
}

DISPLAY_HINTS = {}
