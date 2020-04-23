# ----------------------------------------------------------------------
# HUAWEI-ENTITY-EXTENT-MIB
# Compiled MIB
# Do not modify this file directly
# Run ./noc mib make-cmib instead
# ----------------------------------------------------------------------
# Copyright (C) 2007-2020 The NOC Project
# See LICENSE for details
# ----------------------------------------------------------------------

# MIB Name
NAME = "HUAWEI-ENTITY-EXTENT-MIB"

# Metadata
LAST_UPDATED = "2011-07-15"
COMPILED = "2020-01-19"

# MIB Data: name -> oid
MIB = {
    "HUAWEI-ENTITY-EXTENT-MIB::hwEntityExtentMIB": "1.3.6.1.4.1.2011.5.25.31",
    "HUAWEI-ENTITY-EXTENT-MIB::hwEntityExtObjects": "1.3.6.1.4.1.2011.5.25.31.1",
    "HUAWEI-ENTITY-EXTENT-MIB::hwEntityState": "1.3.6.1.4.1.2011.5.25.31.1.1",
    "HUAWEI-ENTITY-EXTENT-MIB::hwEntityStateTable": "1.3.6.1.4.1.2011.5.25.31.1.1.1",
    "HUAWEI-ENTITY-EXTENT-MIB::hwEntityStateEntry": "1.3.6.1.4.1.2011.5.25.31.1.1.1.1",
    "HUAWEI-ENTITY-EXTENT-MIB::hwEntityAdminStatus": "1.3.6.1.4.1.2011.5.25.31.1.1.1.1.1",
    "HUAWEI-ENTITY-EXTENT-MIB::hwEntityOperStatus": "1.3.6.1.4.1.2011.5.25.31.1.1.1.1.2",
    "HUAWEI-ENTITY-EXTENT-MIB::hwEntityStandbyStatus": "1.3.6.1.4.1.2011.5.25.31.1.1.1.1.3",
    "HUAWEI-ENTITY-EXTENT-MIB::hwEntityAlarmLight": "1.3.6.1.4.1.2011.5.25.31.1.1.1.1.4",
    "HUAWEI-ENTITY-EXTENT-MIB::hwEntityCpuUsage": "1.3.6.1.4.1.2011.5.25.31.1.1.1.1.5",
    "HUAWEI-ENTITY-EXTENT-MIB::hwEntityCpuUsageThreshold": "1.3.6.1.4.1.2011.5.25.31.1.1.1.1.6",
    "HUAWEI-ENTITY-EXTENT-MIB::hwEntityMemUsage": "1.3.6.1.4.1.2011.5.25.31.1.1.1.1.7",
    "HUAWEI-ENTITY-EXTENT-MIB::hwEntityMemUsageThreshold": "1.3.6.1.4.1.2011.5.25.31.1.1.1.1.8",
    "HUAWEI-ENTITY-EXTENT-MIB::hwEntityMemSize": "1.3.6.1.4.1.2011.5.25.31.1.1.1.1.9",
    "HUAWEI-ENTITY-EXTENT-MIB::hwEntityUpTime": "1.3.6.1.4.1.2011.5.25.31.1.1.1.1.10",
    "HUAWEI-ENTITY-EXTENT-MIB::hwEntityTemperature": "1.3.6.1.4.1.2011.5.25.31.1.1.1.1.11",
    "HUAWEI-ENTITY-EXTENT-MIB::hwEntityTemperatureThreshold": "1.3.6.1.4.1.2011.5.25.31.1.1.1.1.12",
    "HUAWEI-ENTITY-EXTENT-MIB::hwEntityVoltage": "1.3.6.1.4.1.2011.5.25.31.1.1.1.1.13",
    "HUAWEI-ENTITY-EXTENT-MIB::hwEntityVoltageLowThreshold": "1.3.6.1.4.1.2011.5.25.31.1.1.1.1.14",
    "HUAWEI-ENTITY-EXTENT-MIB::hwEntityVoltageHighThreshold": "1.3.6.1.4.1.2011.5.25.31.1.1.1.1.15",
    "HUAWEI-ENTITY-EXTENT-MIB::hwEntityTemperatureLowThreshold": "1.3.6.1.4.1.2011.5.25.31.1.1.1.1.16",
    "HUAWEI-ENTITY-EXTENT-MIB::hwEntityOpticalPower": "1.3.6.1.4.1.2011.5.25.31.1.1.1.1.17",
    "HUAWEI-ENTITY-EXTENT-MIB::hwEntityCurrent": "1.3.6.1.4.1.2011.5.25.31.1.1.1.1.18",
    "HUAWEI-ENTITY-EXTENT-MIB::hwEntityMemSizeMega": "1.3.6.1.4.1.2011.5.25.31.1.1.1.1.19",
    "HUAWEI-ENTITY-EXTENT-MIB::hwEntityPortType": "1.3.6.1.4.1.2011.5.25.31.1.1.1.1.20",
    "HUAWEI-ENTITY-EXTENT-MIB::hwEntityDuplex": "1.3.6.1.4.1.2011.5.25.31.1.1.1.1.21",
    "HUAWEI-ENTITY-EXTENT-MIB::hwEntityOpticalPowerRx": "1.3.6.1.4.1.2011.5.25.31.1.1.1.1.22",
    "HUAWEI-ENTITY-EXTENT-MIB::hwEntityCpuUsageLowThreshold": "1.3.6.1.4.1.2011.5.25.31.1.1.1.1.23",
    "HUAWEI-ENTITY-EXTENT-MIB::hwEntityBoardPower": "1.3.6.1.4.1.2011.5.25.31.1.1.1.1.24",
    "HUAWEI-ENTITY-EXTENT-MIB::hwEntityCpuFrequency": "1.3.6.1.4.1.2011.5.25.31.1.1.1.1.25",
    "HUAWEI-ENTITY-EXTENT-MIB::hwEntitySupportFlexCard": "1.3.6.1.4.1.2011.5.25.31.1.1.1.1.26",
    "HUAWEI-ENTITY-EXTENT-MIB::hwEntityBoardClass": "1.3.6.1.4.1.2011.5.25.31.1.1.1.1.27",
    "HUAWEI-ENTITY-EXTENT-MIB::hwNseOpmStatus": "1.3.6.1.4.1.2011.5.25.31.1.1.1.1.28",
    "HUAWEI-ENTITY-EXTENT-MIB::hwEntityCpuMaxUsage": "1.3.6.1.4.1.2011.5.25.31.1.1.1.1.29",
    "HUAWEI-ENTITY-EXTENT-MIB::hwEntityCPUType": "1.3.6.1.4.1.2011.5.25.31.1.1.1.1.30",
    "HUAWEI-ENTITY-EXTENT-MIB::hwEntityMemoryType": "1.3.6.1.4.1.2011.5.25.31.1.1.1.1.31",
    "HUAWEI-ENTITY-EXTENT-MIB::hwEntityFlashSize": "1.3.6.1.4.1.2011.5.25.31.1.1.1.1.32",
    "HUAWEI-ENTITY-EXTENT-MIB::hwEntityIfUpTimes": "1.3.6.1.4.1.2011.5.25.31.1.1.1.1.33",
    "HUAWEI-ENTITY-EXTENT-MIB::hwEntityIfDownTimes": "1.3.6.1.4.1.2011.5.25.31.1.1.1.1.34",
    "HUAWEI-ENTITY-EXTENT-MIB::hwEntityCPUAvgUsage": "1.3.6.1.4.1.2011.5.25.31.1.1.1.1.35",
    "HUAWEI-ENTITY-EXTENT-MIB::hwEntityMemoryAvgUsage": "1.3.6.1.4.1.2011.5.25.31.1.1.1.1.36",
    "HUAWEI-ENTITY-EXTENT-MIB::hwRUModuleInfoTable": "1.3.6.1.4.1.2011.5.25.31.1.1.2",
    "HUAWEI-ENTITY-EXTENT-MIB::hwRUModuleInfoEntry": "1.3.6.1.4.1.2011.5.25.31.1.1.2.1",
    "HUAWEI-ENTITY-EXTENT-MIB::hwEntityBomId": "1.3.6.1.4.1.2011.5.25.31.1.1.2.1.1",
    "HUAWEI-ENTITY-EXTENT-MIB::hwEntityBomEnDesc": "1.3.6.1.4.1.2011.5.25.31.1.1.2.1.2",
    "HUAWEI-ENTITY-EXTENT-MIB::hwEntityBomLocalDesc": "1.3.6.1.4.1.2011.5.25.31.1.1.2.1.3",
    "HUAWEI-ENTITY-EXTENT-MIB::hwEntityManufacturedDate": "1.3.6.1.4.1.2011.5.25.31.1.1.2.1.4",
    "HUAWEI-ENTITY-EXTENT-MIB::hwEntityManufactureCode": "1.3.6.1.4.1.2011.5.25.31.1.1.2.1.5",
    "HUAWEI-ENTITY-EXTENT-MIB::hwEntityCLEICode": "1.3.6.1.4.1.2011.5.25.31.1.1.2.1.6",
    "HUAWEI-ENTITY-EXTENT-MIB::hwEntityUpdateLog": "1.3.6.1.4.1.2011.5.25.31.1.1.2.1.7",
    "HUAWEI-ENTITY-EXTENT-MIB::hwEntityArchivesInfoVersion": "1.3.6.1.4.1.2011.5.25.31.1.1.2.1.8",
    "HUAWEI-ENTITY-EXTENT-MIB::hwEntityOpenBomId": "1.3.6.1.4.1.2011.5.25.31.1.1.2.1.9",
    "HUAWEI-ENTITY-EXTENT-MIB::hwEntityIssueNum": "1.3.6.1.4.1.2011.5.25.31.1.1.2.1.10",
    "HUAWEI-ENTITY-EXTENT-MIB::hwEntityBoardType": "1.3.6.1.4.1.2011.5.25.31.1.1.2.1.11",
    "HUAWEI-ENTITY-EXTENT-MIB::hwOpticalModuleInfoTable": "1.3.6.1.4.1.2011.5.25.31.1.1.3",
    "HUAWEI-ENTITY-EXTENT-MIB::hwOpticalModuleInfoEntry": "1.3.6.1.4.1.2011.5.25.31.1.1.3.1",
    "HUAWEI-ENTITY-EXTENT-MIB::hwEntityOpticalMode": "1.3.6.1.4.1.2011.5.25.31.1.1.3.1.1",
    "HUAWEI-ENTITY-EXTENT-MIB::hwEntityOpticalWaveLength": "1.3.6.1.4.1.2011.5.25.31.1.1.3.1.2",
    "HUAWEI-ENTITY-EXTENT-MIB::hwEntityOpticalTransDistance": "1.3.6.1.4.1.2011.5.25.31.1.1.3.1.3",
    "HUAWEI-ENTITY-EXTENT-MIB::hwEntityOpticalVendorSn": "1.3.6.1.4.1.2011.5.25.31.1.1.3.1.4",
    "HUAWEI-ENTITY-EXTENT-MIB::hwEntityOpticalTemperature": "1.3.6.1.4.1.2011.5.25.31.1.1.3.1.5",
    "HUAWEI-ENTITY-EXTENT-MIB::hwEntityOpticalVoltage": "1.3.6.1.4.1.2011.5.25.31.1.1.3.1.6",
    "HUAWEI-ENTITY-EXTENT-MIB::hwEntityOpticalBiasCurrent": "1.3.6.1.4.1.2011.5.25.31.1.1.3.1.7",
    "HUAWEI-ENTITY-EXTENT-MIB::hwEntityOpticalRxPower": "1.3.6.1.4.1.2011.5.25.31.1.1.3.1.8",
    "HUAWEI-ENTITY-EXTENT-MIB::hwEntityOpticalTxPower": "1.3.6.1.4.1.2011.5.25.31.1.1.3.1.9",
    "HUAWEI-ENTITY-EXTENT-MIB::hwEntityOpticalType": "1.3.6.1.4.1.2011.5.25.31.1.1.3.1.10",
    "HUAWEI-ENTITY-EXTENT-MIB::hwEntityOpticalTransBW": "1.3.6.1.4.1.2011.5.25.31.1.1.3.1.11",
    "HUAWEI-ENTITY-EXTENT-MIB::hwEntityOpticalFiberType": "1.3.6.1.4.1.2011.5.25.31.1.1.3.1.12",
    "HUAWEI-ENTITY-EXTENT-MIB::hwEntityOpticalRxLowThreshold": "1.3.6.1.4.1.2011.5.25.31.1.1.3.1.13",
    "HUAWEI-ENTITY-EXTENT-MIB::hwEntityOpticalRxHighThreshold": "1.3.6.1.4.1.2011.5.25.31.1.1.3.1.14",
    "HUAWEI-ENTITY-EXTENT-MIB::hwEntityOpticalTxLowThreshold": "1.3.6.1.4.1.2011.5.25.31.1.1.3.1.15",
    "HUAWEI-ENTITY-EXTENT-MIB::hwEntityOpticalTxHighThreshold": "1.3.6.1.4.1.2011.5.25.31.1.1.3.1.16",
    "HUAWEI-ENTITY-EXTENT-MIB::hwEntityOpticalPlug": "1.3.6.1.4.1.2011.5.25.31.1.1.3.1.17",
    "HUAWEI-ENTITY-EXTENT-MIB::hwEntityOpticalDirectionType": "1.3.6.1.4.1.2011.5.25.31.1.1.3.1.18",
    "HUAWEI-ENTITY-EXTENT-MIB::hwEntityOpticalUserEeprom": "1.3.6.1.4.1.2011.5.25.31.1.1.3.1.19",
    "HUAWEI-ENTITY-EXTENT-MIB::hwEntityOpticalRxLowWarnThreshold": "1.3.6.1.4.1.2011.5.25.31.1.1.3.1.20",
    "HUAWEI-ENTITY-EXTENT-MIB::hwEntityOpticalRxHighWarnThreshold": "1.3.6.1.4.1.2011.5.25.31.1.1.3.1.21",
    "HUAWEI-ENTITY-EXTENT-MIB::hwEntityOpticalTxLowWarnThreshold": "1.3.6.1.4.1.2011.5.25.31.1.1.3.1.22",
    "HUAWEI-ENTITY-EXTENT-MIB::hwEntityOpticalTxHighWarnThreshold": "1.3.6.1.4.1.2011.5.25.31.1.1.3.1.23",
    "HUAWEI-ENTITY-EXTENT-MIB::hwMonitorInputTable": "1.3.6.1.4.1.2011.5.25.31.1.1.4",
    "HUAWEI-ENTITY-EXTENT-MIB::hwMonitorInputEntry": "1.3.6.1.4.1.2011.5.25.31.1.1.4.1",
    "HUAWEI-ENTITY-EXTENT-MIB::hwMonitorInputIndex": "1.3.6.1.4.1.2011.5.25.31.1.1.4.1.1",
    "HUAWEI-ENTITY-EXTENT-MIB::hwMonitorInputName": "1.3.6.1.4.1.2011.5.25.31.1.1.4.1.2",
    "HUAWEI-ENTITY-EXTENT-MIB::hwMonitorInputState": "1.3.6.1.4.1.2011.5.25.31.1.1.4.1.3",
    "HUAWEI-ENTITY-EXTENT-MIB::hwMonitorInputStateEnable": "1.3.6.1.4.1.2011.5.25.31.1.1.4.1.4",
    "HUAWEI-ENTITY-EXTENT-MIB::hwMonitorInputRowStatus": "1.3.6.1.4.1.2011.5.25.31.1.1.4.1.5",
    "HUAWEI-ENTITY-EXTENT-MIB::hwMonitorOutputTable": "1.3.6.1.4.1.2011.5.25.31.1.1.5",
    "HUAWEI-ENTITY-EXTENT-MIB::hwMonitorOutputEntry": "1.3.6.1.4.1.2011.5.25.31.1.1.5.1",
    "HUAWEI-ENTITY-EXTENT-MIB::hwMonitorOutputIndex": "1.3.6.1.4.1.2011.5.25.31.1.1.5.1.1",
    "HUAWEI-ENTITY-EXTENT-MIB::hwMonitorOutputRuleIndex": "1.3.6.1.4.1.2011.5.25.31.1.1.5.1.2",
    "HUAWEI-ENTITY-EXTENT-MIB::hwMonitorOutputMask": "1.3.6.1.4.1.2011.5.25.31.1.1.5.1.3",
    "HUAWEI-ENTITY-EXTENT-MIB::hwMonitorOutputKey": "1.3.6.1.4.1.2011.5.25.31.1.1.5.1.4",
    "HUAWEI-ENTITY-EXTENT-MIB::hwMonitorOutputRowStatus": "1.3.6.1.4.1.2011.5.25.31.1.1.5.1.5",
    "HUAWEI-ENTITY-EXTENT-MIB::hwEntPowerUsedInfoTable": "1.3.6.1.4.1.2011.5.25.31.1.1.6",
    "HUAWEI-ENTITY-EXTENT-MIB::hwEntPowerUsedInfoEntry": "1.3.6.1.4.1.2011.5.25.31.1.1.6.1",
    "HUAWEI-ENTITY-EXTENT-MIB::hwEntPowerUsedInfoBoardName": "1.3.6.1.4.1.2011.5.25.31.1.1.6.1.1",
    "HUAWEI-ENTITY-EXTENT-MIB::hwEntPowerUsedInfoBoardType": "1.3.6.1.4.1.2011.5.25.31.1.1.6.1.2",
    "HUAWEI-ENTITY-EXTENT-MIB::hwEntPowerUsedInfoBoardSlot": "1.3.6.1.4.1.2011.5.25.31.1.1.6.1.3",
    "HUAWEI-ENTITY-EXTENT-MIB::hwEntPowerUsedInfoPower": "1.3.6.1.4.1.2011.5.25.31.1.1.6.1.4",
    "HUAWEI-ENTITY-EXTENT-MIB::hwVirtualCableTestTable": "1.3.6.1.4.1.2011.5.25.31.1.1.7",
    "HUAWEI-ENTITY-EXTENT-MIB::hwVirtualCableTestEntry": "1.3.6.1.4.1.2011.5.25.31.1.1.7.1",
    "HUAWEI-ENTITY-EXTENT-MIB::hwVirtualCableTestIfIndex": "1.3.6.1.4.1.2011.5.25.31.1.1.7.1.1",
    "HUAWEI-ENTITY-EXTENT-MIB::hwVirtualCableTestPairStatus": "1.3.6.1.4.1.2011.5.25.31.1.1.7.1.2",
    "HUAWEI-ENTITY-EXTENT-MIB::hwVirtualCableTestPairLength": "1.3.6.1.4.1.2011.5.25.31.1.1.7.1.3",
    "HUAWEI-ENTITY-EXTENT-MIB::hwVirtualCableTestOperation": "1.3.6.1.4.1.2011.5.25.31.1.1.7.1.4",
    "HUAWEI-ENTITY-EXTENT-MIB::hwVirtualCableTestLastTime": "1.3.6.1.4.1.2011.5.25.31.1.1.7.1.5",
    "HUAWEI-ENTITY-EXTENT-MIB::hwVirtualCableTestPairAStatus": "1.3.6.1.4.1.2011.5.25.31.1.1.7.1.6",
    "HUAWEI-ENTITY-EXTENT-MIB::hwVirtualCableTestPairBStatus": "1.3.6.1.4.1.2011.5.25.31.1.1.7.1.7",
    "HUAWEI-ENTITY-EXTENT-MIB::hwVirtualCableTestPairCStatus": "1.3.6.1.4.1.2011.5.25.31.1.1.7.1.8",
    "HUAWEI-ENTITY-EXTENT-MIB::hwVirtualCableTestPairDStatus": "1.3.6.1.4.1.2011.5.25.31.1.1.7.1.9",
    "HUAWEI-ENTITY-EXTENT-MIB::hwVirtualCableTestPairALength": "1.3.6.1.4.1.2011.5.25.31.1.1.7.1.10",
    "HUAWEI-ENTITY-EXTENT-MIB::hwVirtualCableTestPairBLength": "1.3.6.1.4.1.2011.5.25.31.1.1.7.1.11",
    "HUAWEI-ENTITY-EXTENT-MIB::hwVirtualCableTestPairCLength": "1.3.6.1.4.1.2011.5.25.31.1.1.7.1.12",
    "HUAWEI-ENTITY-EXTENT-MIB::hwVirtualCableTestPairDLength": "1.3.6.1.4.1.2011.5.25.31.1.1.7.1.13",
    "HUAWEI-ENTITY-EXTENT-MIB::hwTemperatureThresholdTable": "1.3.6.1.4.1.2011.5.25.31.1.1.8",
    "HUAWEI-ENTITY-EXTENT-MIB::hwTemperatureThresholdEntry": "1.3.6.1.4.1.2011.5.25.31.1.1.8.1",
    "HUAWEI-ENTITY-EXTENT-MIB::hwEntityTempSlotId": "1.3.6.1.4.1.2011.5.25.31.1.1.8.1.1",
    "HUAWEI-ENTITY-EXTENT-MIB::hwEntityTempI2CId": "1.3.6.1.4.1.2011.5.25.31.1.1.8.1.2",
    "HUAWEI-ENTITY-EXTENT-MIB::hwEntityTempAddr": "1.3.6.1.4.1.2011.5.25.31.1.1.8.1.3",
    "HUAWEI-ENTITY-EXTENT-MIB::hwEntityTempChannel": "1.3.6.1.4.1.2011.5.25.31.1.1.8.1.4",
    "HUAWEI-ENTITY-EXTENT-MIB::hwEntityTempStatus": "1.3.6.1.4.1.2011.5.25.31.1.1.8.1.5",
    "HUAWEI-ENTITY-EXTENT-MIB::hwEntityTempValue": "1.3.6.1.4.1.2011.5.25.31.1.1.8.1.6",
    "HUAWEI-ENTITY-EXTENT-MIB::hwEntityTempMinorAlmThreshold": "1.3.6.1.4.1.2011.5.25.31.1.1.8.1.7",
    "HUAWEI-ENTITY-EXTENT-MIB::hwEntityTempMajorAlmThreshold": "1.3.6.1.4.1.2011.5.25.31.1.1.8.1.8",
    "HUAWEI-ENTITY-EXTENT-MIB::hwEntityTempFatalAlmThreshold": "1.3.6.1.4.1.2011.5.25.31.1.1.8.1.9",
    "HUAWEI-ENTITY-EXTENT-MIB::hwVoltageInfoTable": "1.3.6.1.4.1.2011.5.25.31.1.1.9",
    "HUAWEI-ENTITY-EXTENT-MIB::hwVoltageInfoEntry": "1.3.6.1.4.1.2011.5.25.31.1.1.9.1",
    "HUAWEI-ENTITY-EXTENT-MIB::hwEntityVolSlot": "1.3.6.1.4.1.2011.5.25.31.1.1.9.1.1",
    "HUAWEI-ENTITY-EXTENT-MIB::hwEntityVolI2CId": "1.3.6.1.4.1.2011.5.25.31.1.1.9.1.2",
    "HUAWEI-ENTITY-EXTENT-MIB::hwEntityVolAddr": "1.3.6.1.4.1.2011.5.25.31.1.1.9.1.3",
    "HUAWEI-ENTITY-EXTENT-MIB::hwEntityVolChannel": "1.3.6.1.4.1.2011.5.25.31.1.1.9.1.4",
    "HUAWEI-ENTITY-EXTENT-MIB::hwEntityVolStatus": "1.3.6.1.4.1.2011.5.25.31.1.1.9.1.5",
    "HUAWEI-ENTITY-EXTENT-MIB::hwEntityVolRequired": "1.3.6.1.4.1.2011.5.25.31.1.1.9.1.6",
    "HUAWEI-ENTITY-EXTENT-MIB::hwEntityVolCurValue": "1.3.6.1.4.1.2011.5.25.31.1.1.9.1.7",
    "HUAWEI-ENTITY-EXTENT-MIB::hwEntityVolRatio": "1.3.6.1.4.1.2011.5.25.31.1.1.9.1.8",
    "HUAWEI-ENTITY-EXTENT-MIB::hwEntityVolLowAlmMajor": "1.3.6.1.4.1.2011.5.25.31.1.1.9.1.9",
    "HUAWEI-ENTITY-EXTENT-MIB::hwEntityVolLowAlmFatal": "1.3.6.1.4.1.2011.5.25.31.1.1.9.1.10",
    "HUAWEI-ENTITY-EXTENT-MIB::hwEntityVolHighAlmMajor": "1.3.6.1.4.1.2011.5.25.31.1.1.9.1.11",
    "HUAWEI-ENTITY-EXTENT-MIB::hwEntityVolHighAlmFatal": "1.3.6.1.4.1.2011.5.25.31.1.1.9.1.12",
    "HUAWEI-ENTITY-EXTENT-MIB::hwFanStatusTable": "1.3.6.1.4.1.2011.5.25.31.1.1.10",
    "HUAWEI-ENTITY-EXTENT-MIB::hwFanStatusEntry": "1.3.6.1.4.1.2011.5.25.31.1.1.10.1",
    "HUAWEI-ENTITY-EXTENT-MIB::hwEntityFanSlot": "1.3.6.1.4.1.2011.5.25.31.1.1.10.1.1",
    "HUAWEI-ENTITY-EXTENT-MIB::hwEntityFanSn": "1.3.6.1.4.1.2011.5.25.31.1.1.10.1.2",
    "HUAWEI-ENTITY-EXTENT-MIB::hwEntityFanReg": "1.3.6.1.4.1.2011.5.25.31.1.1.10.1.3",
    "HUAWEI-ENTITY-EXTENT-MIB::hwEntityFanSpdAdjMode": "1.3.6.1.4.1.2011.5.25.31.1.1.10.1.4",
    "HUAWEI-ENTITY-EXTENT-MIB::hwEntityFanSpeed": "1.3.6.1.4.1.2011.5.25.31.1.1.10.1.5",
    "HUAWEI-ENTITY-EXTENT-MIB::hwEntityFanPresent": "1.3.6.1.4.1.2011.5.25.31.1.1.10.1.6",
    "HUAWEI-ENTITY-EXTENT-MIB::hwEntityFanState": "1.3.6.1.4.1.2011.5.25.31.1.1.10.1.7",
    "HUAWEI-ENTITY-EXTENT-MIB::hwEntityGlobalPara": "1.3.6.1.4.1.2011.5.25.31.1.1.11",
    "HUAWEI-ENTITY-EXTENT-MIB::hwEntityServiceType": "1.3.6.1.4.1.2011.5.25.31.1.1.11.1",
    "HUAWEI-ENTITY-EXTENT-MIB::hwPortBip8StatisticsTable": "1.3.6.1.4.1.2011.5.25.31.1.1.12",
    "HUAWEI-ENTITY-EXTENT-MIB::hwPortBip8StatisticsEntry": "1.3.6.1.4.1.2011.5.25.31.1.1.12.1",
    "HUAWEI-ENTITY-EXTENT-MIB::hwPhysicalPortBip8StatisticsEB": "1.3.6.1.4.1.2011.5.25.31.1.1.12.1.1",
    "HUAWEI-ENTITY-EXTENT-MIB::hwPhysicalPortBip8StatisticsES": "1.3.6.1.4.1.2011.5.25.31.1.1.12.1.2",
    "HUAWEI-ENTITY-EXTENT-MIB::hwPhysicalPortBip8StatisticsSES": "1.3.6.1.4.1.2011.5.25.31.1.1.12.1.3",
    "HUAWEI-ENTITY-EXTENT-MIB::hwPhysicalPortBip8StatisticsUAS": "1.3.6.1.4.1.2011.5.25.31.1.1.12.1.4",
    "HUAWEI-ENTITY-EXTENT-MIB::hwPhysicalPortBip8StatisticsBBE": "1.3.6.1.4.1.2011.5.25.31.1.1.12.1.5",
    "HUAWEI-ENTITY-EXTENT-MIB::hwPhysicalPortSpeed": "1.3.6.1.4.1.2011.5.25.31.1.1.12.1.6",
    "HUAWEI-ENTITY-EXTENT-MIB::hwEntityExtTraps": "1.3.6.1.4.1.2011.5.25.31.2",
    "HUAWEI-ENTITY-EXTENT-MIB::hwEntityExtTrapsPrefix": "1.3.6.1.4.1.2011.5.25.31.2.0",
    "HUAWEI-ENTITY-EXTENT-MIB::hwEntityExtTemperatureThresholdNotification": "1.3.6.1.4.1.2011.5.25.31.2.0.1",
    "HUAWEI-ENTITY-EXTENT-MIB::hwEntityExtVoltageLowThresholdNotification": "1.3.6.1.4.1.2011.5.25.31.2.0.2",
    "HUAWEI-ENTITY-EXTENT-MIB::hwEntityExtVoltageHighThresholdNotification": "1.3.6.1.4.1.2011.5.25.31.2.0.3",
    "HUAWEI-ENTITY-EXTENT-MIB::hwEntityExtCpuUsageThresholdNotfication": "1.3.6.1.4.1.2011.5.25.31.2.0.4",
    "HUAWEI-ENTITY-EXTENT-MIB::hwEntityExtMemUsageThresholdNotification": "1.3.6.1.4.1.2011.5.25.31.2.0.5",
    "HUAWEI-ENTITY-EXTENT-MIB::hwEntityExtOperEnabled": "1.3.6.1.4.1.2011.5.25.31.2.0.6",
    "HUAWEI-ENTITY-EXTENT-MIB::hwEntityExtOperDisabled": "1.3.6.1.4.1.2011.5.25.31.2.0.7",
    "HUAWEI-ENTITY-EXTENT-MIB::hwEntityExtMonitorBoardAbnormalNotification": "1.3.6.1.4.1.2011.5.25.31.2.0.8",
    "HUAWEI-ENTITY-EXTENT-MIB::hwEntityExtMonitorBoardNormalNotification": "1.3.6.1.4.1.2011.5.25.31.2.0.9",
    "HUAWEI-ENTITY-EXTENT-MIB::hwEntityExtMonitorPortAbnormalNotification": "1.3.6.1.4.1.2011.5.25.31.2.0.10",
    "HUAWEI-ENTITY-EXTENT-MIB::hwEntityExtMonitorPortNormalNotification": "1.3.6.1.4.1.2011.5.25.31.2.0.11",
    "HUAWEI-ENTITY-EXTENT-MIB::hwEntityExtCpuUsageLowThresholdNotfication": "1.3.6.1.4.1.2011.5.25.31.2.0.12",
    "HUAWEI-ENTITY-EXTENT-MIB::hwDevicePowerInfoObjects": "1.3.6.1.4.1.2011.5.25.31.3",
    "HUAWEI-ENTITY-EXTENT-MIB::hwDevicePowerInfoTotalPower": "1.3.6.1.4.1.2011.5.25.31.3.1",
    "HUAWEI-ENTITY-EXTENT-MIB::hwDevicePowerInfoUsedPower": "1.3.6.1.4.1.2011.5.25.31.3.2",
    "HUAWEI-ENTITY-EXTENT-MIB::hwEntityExtConformance": "1.3.6.1.4.1.2011.5.25.31.4",
    "HUAWEI-ENTITY-EXTENT-MIB::hwEntityExtCompliances": "1.3.6.1.4.1.2011.5.25.31.4.1",
    "HUAWEI-ENTITY-EXTENT-MIB::hwEntityExtGroups": "1.3.6.1.4.1.2011.5.25.31.4.2",
    "HUAWEI-ENTITY-EXTENT-MIB::hwPnpObjects": "1.3.6.1.4.1.2011.5.25.31.5",
    "HUAWEI-ENTITY-EXTENT-MIB::hwPnpInfo": "1.3.6.1.4.1.2011.5.25.31.5.1",
    "HUAWEI-ENTITY-EXTENT-MIB::hwHardwareCapaSequenceNo": "1.3.6.1.4.1.2011.5.25.31.5.1.1",
    "HUAWEI-ENTITY-EXTENT-MIB::hwPnpTraps": "1.3.6.1.4.1.2011.5.25.31.5.2",
    "HUAWEI-ENTITY-EXTENT-MIB::hwHardwareCapaChangeNotification": "1.3.6.1.4.1.2011.5.25.31.5.2.1",
    "HUAWEI-ENTITY-EXTENT-MIB::hwPnpOperateTable": "1.3.6.1.4.1.2011.5.25.31.5.3",
    "HUAWEI-ENTITY-EXTENT-MIB::hwPnpOperateEntry": "1.3.6.1.4.1.2011.5.25.31.5.3.1",
    "HUAWEI-ENTITY-EXTENT-MIB::hwFileGeneIndex": "1.3.6.1.4.1.2011.5.25.31.5.3.1.1",
    "HUAWEI-ENTITY-EXTENT-MIB::hwFileGeneOperState": "1.3.6.1.4.1.2011.5.25.31.5.3.1.2",
    "HUAWEI-ENTITY-EXTENT-MIB::hwFileGeneResourceType": "1.3.6.1.4.1.2011.5.25.31.5.3.1.3",
    "HUAWEI-ENTITY-EXTENT-MIB::hwFileGeneResourceID": "1.3.6.1.4.1.2011.5.25.31.5.3.1.4",
    "HUAWEI-ENTITY-EXTENT-MIB::hwFileGeneDestinationFile": "1.3.6.1.4.1.2011.5.25.31.5.3.1.5",
    "HUAWEI-ENTITY-EXTENT-MIB::hwFileGeneRowStatus": "1.3.6.1.4.1.2011.5.25.31.5.3.1.6",
    "HUAWEI-ENTITY-EXTENT-MIB::hwSystemGlobalObjects": "1.3.6.1.4.1.2011.5.25.31.6",
    "HUAWEI-ENTITY-EXTENT-MIB::hwEntitySystemNetID": "1.3.6.1.4.1.2011.5.25.31.6.1",
    "HUAWEI-ENTITY-EXTENT-MIB::hwEntitySoftwareName": "1.3.6.1.4.1.2011.5.25.31.6.2",
    "HUAWEI-ENTITY-EXTENT-MIB::hwEntitySoftwareVersion": "1.3.6.1.4.1.2011.5.25.31.6.3",
    "HUAWEI-ENTITY-EXTENT-MIB::hwEntitySoftwareVendor": "1.3.6.1.4.1.2011.5.25.31.6.4",
    "HUAWEI-ENTITY-EXTENT-MIB::hwEntitySystemModel": "1.3.6.1.4.1.2011.5.25.31.6.5",
    "HUAWEI-ENTITY-EXTENT-MIB::hwEntitySystemTime": "1.3.6.1.4.1.2011.5.25.31.6.6",
    "HUAWEI-ENTITY-EXTENT-MIB::hwEntitySystemMacAddress": "1.3.6.1.4.1.2011.5.25.31.6.7",
    "HUAWEI-ENTITY-EXTENT-MIB::hwEntitySystemReset": "1.3.6.1.4.1.2011.5.25.31.6.8",
    "HUAWEI-ENTITY-EXTENT-MIB::hwEntitySystemHealthInterval": "1.3.6.1.4.1.2011.5.25.31.6.9",
    "HUAWEI-ENTITY-EXTENT-MIB::hwEntitySystemNEId": "1.3.6.1.4.1.2011.5.25.31.6.10",
    "HUAWEI-ENTITY-EXTENT-MIB::hwHeartbeatObjects": "1.3.6.1.4.1.2011.5.25.31.7",
    "HUAWEI-ENTITY-EXTENT-MIB::hwHeartbeatConfig": "1.3.6.1.4.1.2011.5.25.31.7.1",
    "HUAWEI-ENTITY-EXTENT-MIB::hwEntityHeartbeatOnOff": "1.3.6.1.4.1.2011.5.25.31.7.1.1",
    "HUAWEI-ENTITY-EXTENT-MIB::hwEntityHeartbeatPeriod": "1.3.6.1.4.1.2011.5.25.31.7.1.2",
    "HUAWEI-ENTITY-EXTENT-MIB::hwHeartbeatTrapPrefix": "1.3.6.1.4.1.2011.5.25.31.7.2",
    "HUAWEI-ENTITY-EXTENT-MIB::hwEntityHeartbeatTrap": "1.3.6.1.4.1.2011.5.25.31.7.2.1",
    "HUAWEI-ENTITY-EXTENT-MIB::hwPreDisposeObjects": "1.3.6.1.4.1.2011.5.25.31.8",
    "HUAWEI-ENTITY-EXTENT-MIB::hwPreDisposeInfo": "1.3.6.1.4.1.2011.5.25.31.8.1",
    "HUAWEI-ENTITY-EXTENT-MIB::hwPreDisposeSequenceNo": "1.3.6.1.4.1.2011.5.25.31.8.1.1",
    "HUAWEI-ENTITY-EXTENT-MIB::hwPreDisposedTraps": "1.3.6.1.4.1.2011.5.25.31.8.2",
    "HUAWEI-ENTITY-EXTENT-MIB::hwInsertDiffFromPreDisposed": "1.3.6.1.4.1.2011.5.25.31.8.2.1",
    "HUAWEI-ENTITY-EXTENT-MIB::hwPreDisposedChangeNotification": "1.3.6.1.4.1.2011.5.25.31.8.2.2",
    "HUAWEI-ENTITY-EXTENT-MIB::hwPreDisposeConfigTable": "1.3.6.1.4.1.2011.5.25.31.8.3",
    "HUAWEI-ENTITY-EXTENT-MIB::hwPreDisposeConfigEntry": "1.3.6.1.4.1.2011.5.25.31.8.3.1",
    "HUAWEI-ENTITY-EXTENT-MIB::hwDisposeSlot": "1.3.6.1.4.1.2011.5.25.31.8.3.1.1",
    "HUAWEI-ENTITY-EXTENT-MIB::hwDisposeCardId": "1.3.6.1.4.1.2011.5.25.31.8.3.1.2",
    "HUAWEI-ENTITY-EXTENT-MIB::hwDisposeSbom": "1.3.6.1.4.1.2011.5.25.31.8.3.1.3",
    "HUAWEI-ENTITY-EXTENT-MIB::hwDisposeRowStatus": "1.3.6.1.4.1.2011.5.25.31.8.3.1.4",
    "HUAWEI-ENTITY-EXTENT-MIB::hwDisposeOperState": "1.3.6.1.4.1.2011.5.25.31.8.3.1.5",
    "HUAWEI-ENTITY-EXTENT-MIB::hwPreDisposeEntInfoTable": "1.3.6.1.4.1.2011.5.25.31.8.4",
    "HUAWEI-ENTITY-EXTENT-MIB::hwPreDisposeEntInfoEntry": "1.3.6.1.4.1.2011.5.25.31.8.4.1",
    "HUAWEI-ENTITY-EXTENT-MIB::hwDisposeEntPhysicalIndex": "1.3.6.1.4.1.2011.5.25.31.8.4.1.1",
    "HUAWEI-ENTITY-EXTENT-MIB::hwDisposeEntPhysicalDescr": "1.3.6.1.4.1.2011.5.25.31.8.4.1.2",
    "HUAWEI-ENTITY-EXTENT-MIB::hwDisposeEntPhysicalVendorType": "1.3.6.1.4.1.2011.5.25.31.8.4.1.3",
    "HUAWEI-ENTITY-EXTENT-MIB::hwDisposeEntPhysicalContainedIn": "1.3.6.1.4.1.2011.5.25.31.8.4.1.4",
    "HUAWEI-ENTITY-EXTENT-MIB::hwDisposeEntPhysicalClass": "1.3.6.1.4.1.2011.5.25.31.8.4.1.5",
    "HUAWEI-ENTITY-EXTENT-MIB::hwDisposeEntPhysicalParentRelPos": "1.3.6.1.4.1.2011.5.25.31.8.4.1.6",
    "HUAWEI-ENTITY-EXTENT-MIB::hwDisposeEntPhysicalName": "1.3.6.1.4.1.2011.5.25.31.8.4.1.7",
}

DISPLAY_HINTS = {
    "1.3.6.1.4.1.2011.5.25.31.1.1.1.1.30": (
        "OctetString",
        "255t",
    ),  # HUAWEI-ENTITY-EXTENT-MIB::hwEntityCPUType
    "1.3.6.1.4.1.2011.5.25.31.1.1.1.1.31": (
        "OctetString",
        "255t",
    ),  # HUAWEI-ENTITY-EXTENT-MIB::hwEntityMemoryType
    "1.3.6.1.4.1.2011.5.25.31.1.1.2.1.1": (
        "OctetString",
        "255t",
    ),  # HUAWEI-ENTITY-EXTENT-MIB::hwEntityBomId
    "1.3.6.1.4.1.2011.5.25.31.1.1.2.1.2": (
        "OctetString",
        "255t",
    ),  # HUAWEI-ENTITY-EXTENT-MIB::hwEntityBomEnDesc
    "1.3.6.1.4.1.2011.5.25.31.1.1.2.1.3": (
        "OctetString",
        "255t",
    ),  # HUAWEI-ENTITY-EXTENT-MIB::hwEntityBomLocalDesc
    "1.3.6.1.4.1.2011.5.25.31.1.1.2.1.4": (
        "OctetString",
        "2d-1d-1d,1d:1d:1d.1d,1a1d:1d",
    ),  # HUAWEI-ENTITY-EXTENT-MIB::hwEntityManufacturedDate
    "1.3.6.1.4.1.2011.5.25.31.1.1.2.1.6": (
        "OctetString",
        "255t",
    ),  # HUAWEI-ENTITY-EXTENT-MIB::hwEntityCLEICode
    "1.3.6.1.4.1.2011.5.25.31.1.1.2.1.7": (
        "OctetString",
        "255t",
    ),  # HUAWEI-ENTITY-EXTENT-MIB::hwEntityUpdateLog
    "1.3.6.1.4.1.2011.5.25.31.1.1.2.1.8": (
        "OctetString",
        "255t",
    ),  # HUAWEI-ENTITY-EXTENT-MIB::hwEntityArchivesInfoVersion
    "1.3.6.1.4.1.2011.5.25.31.1.1.2.1.9": (
        "OctetString",
        "255t",
    ),  # HUAWEI-ENTITY-EXTENT-MIB::hwEntityOpenBomId
    "1.3.6.1.4.1.2011.5.25.31.1.1.2.1.10": (
        "OctetString",
        "255t",
    ),  # HUAWEI-ENTITY-EXTENT-MIB::hwEntityIssueNum
    "1.3.6.1.4.1.2011.5.25.31.1.1.2.1.11": (
        "OctetString",
        "255t",
    ),  # HUAWEI-ENTITY-EXTENT-MIB::hwEntityBoardType
    "1.3.6.1.4.1.2011.5.25.31.1.1.3.1.4": (
        "OctetString",
        "255t",
    ),  # HUAWEI-ENTITY-EXTENT-MIB::hwEntityOpticalVendorSn
    "1.3.6.1.4.1.2011.5.25.31.5.1.1": (
        "OctetString",
        "255t",
    ),  # HUAWEI-ENTITY-EXTENT-MIB::hwHardwareCapaSequenceNo
    "1.3.6.1.4.1.2011.5.25.31.6.2": (
        "OctetString",
        "255t",
    ),  # HUAWEI-ENTITY-EXTENT-MIB::hwEntitySoftwareName
    "1.3.6.1.4.1.2011.5.25.31.6.3": (
        "OctetString",
        "255t",
    ),  # HUAWEI-ENTITY-EXTENT-MIB::hwEntitySoftwareVersion
    "1.3.6.1.4.1.2011.5.25.31.6.4": (
        "OctetString",
        "255t",
    ),  # HUAWEI-ENTITY-EXTENT-MIB::hwEntitySoftwareVendor
    "1.3.6.1.4.1.2011.5.25.31.6.5": (
        "OctetString",
        "255t",
    ),  # HUAWEI-ENTITY-EXTENT-MIB::hwEntitySystemModel
    "1.3.6.1.4.1.2011.5.25.31.6.6": (
        "OctetString",
        "255t",
    ),  # HUAWEI-ENTITY-EXTENT-MIB::hwEntitySystemTime
    "1.3.6.1.4.1.2011.5.25.31.6.7": (
        "OctetString",
        "255t",
    ),  # HUAWEI-ENTITY-EXTENT-MIB::hwEntitySystemMacAddress
    "1.3.6.1.4.1.2011.5.25.31.8.1.1": (
        "OctetString",
        "255t",
    ),  # HUAWEI-ENTITY-EXTENT-MIB::hwPreDisposeSequenceNo
    "1.3.6.1.4.1.2011.5.25.31.8.4.1.2": (
        "OctetString",
        "255t",
    ),  # HUAWEI-ENTITY-EXTENT-MIB::hwDisposeEntPhysicalDescr
    "1.3.6.1.4.1.2011.5.25.31.8.4.1.7": (
        "OctetString",
        "255t",
    ),  # HUAWEI-ENTITY-EXTENT-MIB::hwDisposeEntPhysicalName
}
