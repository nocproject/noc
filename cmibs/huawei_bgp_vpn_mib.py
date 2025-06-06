# ----------------------------------------------------------------------
# HUAWEI-BGP-VPN-MIB
# Compiled MIB
# Do not modify this file directly
# Run ./noc mib make-cmib instead
# ----------------------------------------------------------------------
# Copyright (C) 2007-2025 The NOC Project
# See LICENSE for details
# ----------------------------------------------------------------------

# MIB Name
NAME = "HUAWEI-BGP-VPN-MIB"

# Metadata
LAST_UPDATED = "2022-10-25"
COMPILED = "2025-02-21"

# MIB Data: name -> oid
MIB = {
    "HUAWEI-BGP-VPN-MIB::hwBgpMIB": "1.3.6.1.4.1.2011.5.25.177",
    "HUAWEI-BGP-VPN-MIB::hwBgpObjects": "1.3.6.1.4.1.2011.5.25.177.1",
    "HUAWEI-BGP-VPN-MIB::hwBgpPeers": "1.3.6.1.4.1.2011.5.25.177.1.1",
    "HUAWEI-BGP-VPN-MIB::hwBgpPeerAddrFamilyTable": "1.3.6.1.4.1.2011.5.25.177.1.1.1",
    "HUAWEI-BGP-VPN-MIB::hwBgpPeerAddrFamilyEntry": "1.3.6.1.4.1.2011.5.25.177.1.1.1.1",
    "HUAWEI-BGP-VPN-MIB::hwBgpPeerInstanceId": "1.3.6.1.4.1.2011.5.25.177.1.1.1.1.1",
    "HUAWEI-BGP-VPN-MIB::hwBgpPeerAddrFamilyAfi": "1.3.6.1.4.1.2011.5.25.177.1.1.1.1.2",
    "HUAWEI-BGP-VPN-MIB::hwBgpPeerAddrFamilySafi": "1.3.6.1.4.1.2011.5.25.177.1.1.1.1.3",
    "HUAWEI-BGP-VPN-MIB::hwBgpPeerType": "1.3.6.1.4.1.2011.5.25.177.1.1.1.1.4",
    "HUAWEI-BGP-VPN-MIB::hwBgpPeerIPAddr": "1.3.6.1.4.1.2011.5.25.177.1.1.1.1.5",
    "HUAWEI-BGP-VPN-MIB::hwBgpPeerVrfName": "1.3.6.1.4.1.2011.5.25.177.1.1.1.1.6",
    "HUAWEI-BGP-VPN-MIB::hwBgpPeerTable": "1.3.6.1.4.1.2011.5.25.177.1.1.2",
    "HUAWEI-BGP-VPN-MIB::hwBgpPeerEntry": "1.3.6.1.4.1.2011.5.25.177.1.1.2.1",
    "HUAWEI-BGP-VPN-MIB::hwBgpPeerNegotiatedVersion": "1.3.6.1.4.1.2011.5.25.177.1.1.2.1.1",
    "HUAWEI-BGP-VPN-MIB::hwBgpPeerRemoteAs": "1.3.6.1.4.1.2011.5.25.177.1.1.2.1.2",
    "HUAWEI-BGP-VPN-MIB::hwBgpPeerRemoteAddr": "1.3.6.1.4.1.2011.5.25.177.1.1.2.1.4",
    "HUAWEI-BGP-VPN-MIB::hwBgpPeerState": "1.3.6.1.4.1.2011.5.25.177.1.1.2.1.5",
    "HUAWEI-BGP-VPN-MIB::hwBgpPeerFsmEstablishedCounter": "1.3.6.1.4.1.2011.5.25.177.1.1.2.1.6",
    "HUAWEI-BGP-VPN-MIB::hwBgpPeerFsmEstablishedTime": "1.3.6.1.4.1.2011.5.25.177.1.1.2.1.7",
    "HUAWEI-BGP-VPN-MIB::hwBgpPeerGRStatus": "1.3.6.1.4.1.2011.5.25.177.1.1.2.1.8",
    "HUAWEI-BGP-VPN-MIB::hwBgpPeerLastError": "1.3.6.1.4.1.2011.5.25.177.1.1.2.1.9",
    "HUAWEI-BGP-VPN-MIB::hwBgpPeerUnAvaiReason": "1.3.6.1.4.1.2011.5.25.177.1.1.2.1.10",
    "HUAWEI-BGP-VPN-MIB::hwBgpPeerAdminStatus": "1.3.6.1.4.1.2011.5.25.177.1.1.2.1.11",
    "HUAWEI-BGP-VPN-MIB::hwBgpPeerDescription": "1.3.6.1.4.1.2011.5.25.177.1.1.2.1.12",
    "HUAWEI-BGP-VPN-MIB::hwBgpPeerRouteTable": "1.3.6.1.4.1.2011.5.25.177.1.1.3",
    "HUAWEI-BGP-VPN-MIB::hwBgpPeerRouteEntry": "1.3.6.1.4.1.2011.5.25.177.1.1.3.1",
    "HUAWEI-BGP-VPN-MIB::hwBgpPeerPrefixRcvCounter": "1.3.6.1.4.1.2011.5.25.177.1.1.3.1.1",
    "HUAWEI-BGP-VPN-MIB::hwBgpPeerPrefixActiveCounter": "1.3.6.1.4.1.2011.5.25.177.1.1.3.1.2",
    "HUAWEI-BGP-VPN-MIB::hwBgpPeerPrefixAdvCounter": "1.3.6.1.4.1.2011.5.25.177.1.1.3.1.3",
    "HUAWEI-BGP-VPN-MIB::hwBgpPeerMessageTable": "1.3.6.1.4.1.2011.5.25.177.1.1.4",
    "HUAWEI-BGP-VPN-MIB::hwBgpPeerMessageEntry": "1.3.6.1.4.1.2011.5.25.177.1.1.4.1",
    "HUAWEI-BGP-VPN-MIB::hwBgpPeerInTotalMsgCounter": "1.3.6.1.4.1.2011.5.25.177.1.1.4.1.1",
    "HUAWEI-BGP-VPN-MIB::hwBgpPeerOutTotalMsgCounter": "1.3.6.1.4.1.2011.5.25.177.1.1.4.1.2",
    "HUAWEI-BGP-VPN-MIB::hwBgpPeerInOpenMsgCounter": "1.3.6.1.4.1.2011.5.25.177.1.1.4.1.3",
    "HUAWEI-BGP-VPN-MIB::hwBgpPeerInUpdateMsgCounter": "1.3.6.1.4.1.2011.5.25.177.1.1.4.1.4",
    "HUAWEI-BGP-VPN-MIB::hwBgpPeerInNotificationMsgCounter": "1.3.6.1.4.1.2011.5.25.177.1.1.4.1.5",
    "HUAWEI-BGP-VPN-MIB::hwBgpPeerInKeepAliveMsgCounter": "1.3.6.1.4.1.2011.5.25.177.1.1.4.1.6",
    "HUAWEI-BGP-VPN-MIB::hwBgpPeerInRouteFreshMsgCounter": "1.3.6.1.4.1.2011.5.25.177.1.1.4.1.7",
    "HUAWEI-BGP-VPN-MIB::hwBgpPeerOutOpenMsgCounter": "1.3.6.1.4.1.2011.5.25.177.1.1.4.1.8",
    "HUAWEI-BGP-VPN-MIB::hwBgpPeerOutUpdateMsgCounter": "1.3.6.1.4.1.2011.5.25.177.1.1.4.1.9",
    "HUAWEI-BGP-VPN-MIB::hwBgpPeerOutNotificationMsgCounter": "1.3.6.1.4.1.2011.5.25.177.1.1.4.1.10",
    "HUAWEI-BGP-VPN-MIB::hwBgpPeerOutKeepAliveMsgCounter": "1.3.6.1.4.1.2011.5.25.177.1.1.4.1.11",
    "HUAWEI-BGP-VPN-MIB::hwBgpPeerOutRouteFreshMsgCounter": "1.3.6.1.4.1.2011.5.25.177.1.1.4.1.12",
    "HUAWEI-BGP-VPN-MIB::hwBgpPeerConfigTable": "1.3.6.1.4.1.2011.5.25.177.1.1.5",
    "HUAWEI-BGP-VPN-MIB::hwBgpPeerConfigEntry": "1.3.6.1.4.1.2011.5.25.177.1.1.5.1",
    "HUAWEI-BGP-VPN-MIB::hwBgpPeerConfigRouteLimitNum": "1.3.6.1.4.1.2011.5.25.177.1.1.5.1.1",
    "HUAWEI-BGP-VPN-MIB::hwBgpPeerConfigRouteLimitThreshold": "1.3.6.1.4.1.2011.5.25.177.1.1.5.1.2",
    "HUAWEI-BGP-VPN-MIB::hwBgpPeerSessionTable": "1.3.6.1.4.1.2011.5.25.177.1.1.6",
    "HUAWEI-BGP-VPN-MIB::hwBgpPeerSessionEntry": "1.3.6.1.4.1.2011.5.25.177.1.1.6.1",
    "HUAWEI-BGP-VPN-MIB::hwBgpPeerSessionVrfName": "1.3.6.1.4.1.2011.5.25.177.1.1.6.1.1",
    "HUAWEI-BGP-VPN-MIB::hwBgpPeerSessionRemoteAddrType": "1.3.6.1.4.1.2011.5.25.177.1.1.6.1.2",
    "HUAWEI-BGP-VPN-MIB::hwBgpPeerSessionRemoteAddr": "1.3.6.1.4.1.2011.5.25.177.1.1.6.1.3",
    "HUAWEI-BGP-VPN-MIB::hwBgpPeerSessionLocalAddrType": "1.3.6.1.4.1.2011.5.25.177.1.1.6.1.4",
    "HUAWEI-BGP-VPN-MIB::hwBgpPeerSessionLocalAddr": "1.3.6.1.4.1.2011.5.25.177.1.1.6.1.5",
    "HUAWEI-BGP-VPN-MIB::hwBgpPeerSessionUnavailableType": "1.3.6.1.4.1.2011.5.25.177.1.1.6.1.6",
    "HUAWEI-BGP-VPN-MIB::hwBgpPeerSessionLocalIfName": "1.3.6.1.4.1.2011.5.25.177.1.1.6.1.7",
    "HUAWEI-BGP-VPN-MIB::hwBgpPeerSessionReason": "1.3.6.1.4.1.2011.5.25.177.1.1.6.1.8",
    "HUAWEI-BGP-VPN-MIB::hwBgpPeerStatisticTable": "1.3.6.1.4.1.2011.5.25.177.1.1.7",
    "HUAWEI-BGP-VPN-MIB::hwBgpPeerStatisticEntry": "1.3.6.1.4.1.2011.5.25.177.1.1.7.1",
    "HUAWEI-BGP-VPN-MIB::hwBgpProcessId": "1.3.6.1.4.1.2011.5.25.177.1.1.7.1.1",
    "HUAWEI-BGP-VPN-MIB::hwBgpPeerVrfInstanceId": "1.3.6.1.4.1.2011.5.25.177.1.1.7.1.2",
    "HUAWEI-BGP-VPN-MIB::hwBgpPeerAddr": "1.3.6.1.4.1.2011.5.25.177.1.1.7.1.3",
    "HUAWEI-BGP-VPN-MIB::hwBgpPeerFsmEstablishedTransitions": "1.3.6.1.4.1.2011.5.25.177.1.1.7.1.4",
    "HUAWEI-BGP-VPN-MIB::hwBgpPeerDownCounts": "1.3.6.1.4.1.2011.5.25.177.1.1.7.1.5",
    "HUAWEI-BGP-VPN-MIB::hwBgpPeerInUpdateMsgs": "1.3.6.1.4.1.2011.5.25.177.1.1.7.1.6",
    "HUAWEI-BGP-VPN-MIB::hwBgpPeerOutUpdateMsgs": "1.3.6.1.4.1.2011.5.25.177.1.1.7.1.7",
    "HUAWEI-BGP-VPN-MIB::hwBgpPeerInTotalMsgs": "1.3.6.1.4.1.2011.5.25.177.1.1.7.1.8",
    "HUAWEI-BGP-VPN-MIB::hwBgpPeerOutTotalMsgs": "1.3.6.1.4.1.2011.5.25.177.1.1.7.1.9",
    "HUAWEI-BGP-VPN-MIB::hwBgpPeerSessionExtTable": "1.3.6.1.4.1.2011.5.25.177.1.1.8",
    "HUAWEI-BGP-VPN-MIB::hwBgpPeerSessionExtEntry": "1.3.6.1.4.1.2011.5.25.177.1.1.8.1",
    "HUAWEI-BGP-VPN-MIB::hwBgpPeerSessionExtVrfId": "1.3.6.1.4.1.2011.5.25.177.1.1.8.1.1",
    "HUAWEI-BGP-VPN-MIB::hwBgpPeerSessionExtRemoteAddrType": "1.3.6.1.4.1.2011.5.25.177.1.1.8.1.2",
    "HUAWEI-BGP-VPN-MIB::hwBgpPeerSessionExtRemoteAddr": "1.3.6.1.4.1.2011.5.25.177.1.1.8.1.3",
    "HUAWEI-BGP-VPN-MIB::hwBgpPeerSessionExtLocalAddrType": "1.3.6.1.4.1.2011.5.25.177.1.1.8.1.4",
    "HUAWEI-BGP-VPN-MIB::hwBgpPeerSessionExtLocalAddr": "1.3.6.1.4.1.2011.5.25.177.1.1.8.1.5",
    "HUAWEI-BGP-VPN-MIB::hwBgpPeerSessionExtUnavailableType": "1.3.6.1.4.1.2011.5.25.177.1.1.8.1.6",
    "HUAWEI-BGP-VPN-MIB::hwBgpPeerSessionExtLocalIfName": "1.3.6.1.4.1.2011.5.25.177.1.1.8.1.7",
    "HUAWEI-BGP-VPN-MIB::hwBgpPeerSessionExtReason": "1.3.6.1.4.1.2011.5.25.177.1.1.8.1.8",
    "HUAWEI-BGP-VPN-MIB::hwBgpPeerSessionExtVrfName": "1.3.6.1.4.1.2011.5.25.177.1.1.8.1.9",
    "HUAWEI-BGP-VPN-MIB::hwBgpPeerSessionExtRemoteAs": "1.3.6.1.4.1.2011.5.25.177.1.1.8.1.10",
    "HUAWEI-BGP-VPN-MIB::hwBgpPeerSessionExtDescription": "1.3.6.1.4.1.2011.5.25.177.1.1.8.1.11",
    "HUAWEI-BGP-VPN-MIB::hwBgpPeerSessionExtPswdType": "1.3.6.1.4.1.2011.5.25.177.1.1.8.1.12",
    "HUAWEI-BGP-VPN-MIB::hwBgpRoute": "1.3.6.1.4.1.2011.5.25.177.1.2",
    "HUAWEI-BGP-VPN-MIB::hwBgpRouteLimitTable": "1.3.6.1.4.1.2011.5.25.177.1.2.1",
    "HUAWEI-BGP-VPN-MIB::hwBgpRouteLimitindex": "1.3.6.1.4.1.2011.5.25.177.1.2.1.1",
    "HUAWEI-BGP-VPN-MIB::hwBgpRouteCurNum": "1.3.6.1.4.1.2011.5.25.177.1.2.1.2",
    "HUAWEI-BGP-VPN-MIB::hwBgpRouteMaxNum": "1.3.6.1.4.1.2011.5.25.177.1.2.1.3",
    "HUAWEI-BGP-VPN-MIB::hwBgpRouteThreshold": "1.3.6.1.4.1.2011.5.25.177.1.2.1.4",
    "HUAWEI-BGP-VPN-MIB::hwBgpRouteType": "1.3.6.1.4.1.2011.5.25.177.1.2.1.5",
    "HUAWEI-BGP-VPN-MIB::hwBgpVrfRouteTable": "1.3.6.1.4.1.2011.5.25.177.1.2.2",
    "HUAWEI-BGP-VPN-MIB::hwBgpVrfRouteEntry": "1.3.6.1.4.1.2011.5.25.177.1.2.2.1",
    "HUAWEI-BGP-VPN-MIB::hwBgpVrfCurrRouteNum": "1.3.6.1.4.1.2011.5.25.177.1.2.2.1.1",
    "HUAWEI-BGP-VPN-MIB::hwBgpVrfThresholdValue": "1.3.6.1.4.1.2011.5.25.177.1.2.2.1.2",
    "HUAWEI-BGP-VPN-MIB::hwBgpVrfRouteType": "1.3.6.1.4.1.2011.5.25.177.1.2.2.1.3",
    "HUAWEI-BGP-VPN-MIB::hwBgpVrfInstName": "1.3.6.1.4.1.2011.5.25.177.1.2.2.1.4",
    "HUAWEI-BGP-VPN-MIB::hwBgpVrfAddressFamily": "1.3.6.1.4.1.2011.5.25.177.1.2.2.1.5",
    "HUAWEI-BGP-VPN-MIB::hwEvpnRouteTable": "1.3.6.1.4.1.2011.5.25.177.1.2.3",
    "HUAWEI-BGP-VPN-MIB::hwEvpnRouteEntry": "1.3.6.1.4.1.2011.5.25.177.1.2.3.1",
    "HUAWEI-BGP-VPN-MIB::hwEvpnCurrRouteNum": "1.3.6.1.4.1.2011.5.25.177.1.2.3.1.1",
    "HUAWEI-BGP-VPN-MIB::hwEvpnThresholdValue": "1.3.6.1.4.1.2011.5.25.177.1.2.3.1.2",
    "HUAWEI-BGP-VPN-MIB::hwEvpnRouteType": "1.3.6.1.4.1.2011.5.25.177.1.2.3.1.3",
    "HUAWEI-BGP-VPN-MIB::hwEvpnAddressFamily": "1.3.6.1.4.1.2011.5.25.177.1.2.3.1.4",
    "HUAWEI-BGP-VPN-MIB::hwBgpLabelLimitTable": "1.3.6.1.4.1.2011.5.25.177.1.2.4",
    "HUAWEI-BGP-VPN-MIB::hwBgpAddrFamilyAfi": "1.3.6.1.4.1.2011.5.25.177.1.2.4.1",
    "HUAWEI-BGP-VPN-MIB::hwBgpAddrFamilySafi": "1.3.6.1.4.1.2011.5.25.177.1.2.4.2",
    "HUAWEI-BGP-VPN-MIB::hwBgpLabelMaxValue": "1.3.6.1.4.1.2011.5.25.177.1.2.4.3",
    "HUAWEI-BGP-VPN-MIB::hwBgpLabelLimitThreshold": "1.3.6.1.4.1.2011.5.25.177.1.2.4.4",
    "HUAWEI-BGP-VPN-MIB::hwBgpVpnTrapObject": "1.3.6.1.4.1.2011.5.25.177.1.2.5",
    "HUAWEI-BGP-VPN-MIB::hwBgpVrfName": "1.3.6.1.4.1.2011.5.25.177.1.2.5.1",
    "HUAWEI-BGP-VPN-MIB::hwBgpMemReason": "1.3.6.1.4.1.2011.5.25.177.1.2.5.2",
    "HUAWEI-BGP-VPN-MIB::hwBgpSidLabelTable": "1.3.6.1.4.1.2011.5.25.177.1.2.6",
    "HUAWEI-BGP-VPN-MIB::hwBgpPrefixSidLabel": "1.3.6.1.4.1.2011.5.25.177.1.2.6.1",
    "HUAWEI-BGP-VPN-MIB::hwBgpRoutePrefix": "1.3.6.1.4.1.2011.5.25.177.1.2.6.2",
    "HUAWEI-BGP-VPN-MIB::hwBgpTraps": "1.3.6.1.4.1.2011.5.25.177.1.3",
    "HUAWEI-BGP-VPN-MIB::hwBgpPeerRouteNumThresholdExceed": "1.3.6.1.4.1.2011.5.25.177.1.3.1",
    "HUAWEI-BGP-VPN-MIB::hwBgpPeerRouteNumThresholdClear": "1.3.6.1.4.1.2011.5.25.177.1.3.2",
    "HUAWEI-BGP-VPN-MIB::hwBgpPeerGRStatusChange": "1.3.6.1.4.1.2011.5.25.177.1.3.3",
    "HUAWEI-BGP-VPN-MIB::hwBgpPeerUnavailable": "1.3.6.1.4.1.2011.5.25.177.1.3.4",
    "HUAWEI-BGP-VPN-MIB::hwBgpPeerAvailable": "1.3.6.1.4.1.2011.5.25.177.1.3.5",
    "HUAWEI-BGP-VPN-MIB::hwBgpPeerRouteExceed": "1.3.6.1.4.1.2011.5.25.177.1.3.6",
    "HUAWEI-BGP-VPN-MIB::hwBgpPeerRouteExceedClear": "1.3.6.1.4.1.2011.5.25.177.1.3.7",
    "HUAWEI-BGP-VPN-MIB::hwL3vpnVrfRouteMidThreshCleared": "1.3.6.1.4.1.2011.5.25.177.1.3.8",
    "HUAWEI-BGP-VPN-MIB::hwBgpPeerEstablished": "1.3.6.1.4.1.2011.5.25.177.1.3.9",
    "HUAWEI-BGP-VPN-MIB::hwBgpPeerBackwardTransition": "1.3.6.1.4.1.2011.5.25.177.1.3.10",
    "HUAWEI-BGP-VPN-MIB::hwBgpRouteThresholdExceed": "1.3.6.1.4.1.2011.5.25.177.1.3.11",
    "HUAWEI-BGP-VPN-MIB::hwBgpRouteThresholdClear": "1.3.6.1.4.1.2011.5.25.177.1.3.12",
    "HUAWEI-BGP-VPN-MIB::hwBgpRouteMaxExceed": "1.3.6.1.4.1.2011.5.25.177.1.3.13",
    "HUAWEI-BGP-VPN-MIB::hwBgpRouteMaxClear": "1.3.6.1.4.1.2011.5.25.177.1.3.14",
    "HUAWEI-BGP-VPN-MIB::hwBgpPeerSessionExceed": "1.3.6.1.4.1.2011.5.25.177.1.3.15",
    "HUAWEI-BGP-VPN-MIB::hwBgpPeerSessionExceedClear": "1.3.6.1.4.1.2011.5.25.177.1.3.16",
    "HUAWEI-BGP-VPN-MIB::hwBgpDynamicPeerSessionExceed": "1.3.6.1.4.1.2011.5.25.177.1.3.17",
    "HUAWEI-BGP-VPN-MIB::hwBgpDynamicPeerSessionExceedClear": "1.3.6.1.4.1.2011.5.25.177.1.3.18",
    "HUAWEI-BGP-VPN-MIB::hwBgpPeerSessionThresholdExceed": "1.3.6.1.4.1.2011.5.25.177.1.3.19",
    "HUAWEI-BGP-VPN-MIB::hwBgpPeerSessionThresholdClear": "1.3.6.1.4.1.2011.5.25.177.1.3.20",
    "HUAWEI-BGP-VPN-MIB::hwBgpVrfRouteNumReachThreshold": "1.3.6.1.4.1.2011.5.25.177.1.3.21",
    "HUAWEI-BGP-VPN-MIB::hwBgpVrfRouteNumReachThresholdClear": "1.3.6.1.4.1.2011.5.25.177.1.3.22",
    "HUAWEI-BGP-VPN-MIB::hwEvpnRouteReachThreshold": "1.3.6.1.4.1.2011.5.25.177.1.3.23",
    "HUAWEI-BGP-VPN-MIB::hwEvpnRouteReachThresholdClear": "1.3.6.1.4.1.2011.5.25.177.1.3.24",
    "HUAWEI-BGP-VPN-MIB::hwVpnRouteLabelNumReachThresold": "1.3.6.1.4.1.2011.5.25.177.1.3.25",
    "HUAWEI-BGP-VPN-MIB::hwVpnRouteLabelNumReachThresoldClear": "1.3.6.1.4.1.2011.5.25.177.1.3.26",
    "HUAWEI-BGP-VPN-MIB::hwVpnRouteLabelNumReachMaximum": "1.3.6.1.4.1.2011.5.25.177.1.3.27",
    "HUAWEI-BGP-VPN-MIB::hwVpnRouteLabelNumReachMaximumClear": "1.3.6.1.4.1.2011.5.25.177.1.3.28",
    "HUAWEI-BGP-VPN-MIB::hwBgpPeerAddrFamilyRouteThresholdExceed": "1.3.6.1.4.1.2011.5.25.177.1.3.29",
    "HUAWEI-BGP-VPN-MIB::hwBgpPeerAddrFamilyRouteThresholdExceedClear": "1.3.6.1.4.1.2011.5.25.177.1.3.30",
    "HUAWEI-BGP-VPN-MIB::hwBgpPeerAddrFamilyRouteExceed": "1.3.6.1.4.1.2011.5.25.177.1.3.31",
    "HUAWEI-BGP-VPN-MIB::hwBgpPeerAddrFamilyRouteExceedClear": "1.3.6.1.4.1.2011.5.25.177.1.3.32",
    "HUAWEI-BGP-VPN-MIB::hwBgpPeerAddrFamilyPerRouteThresholdExceed": "1.3.6.1.4.1.2011.5.25.177.1.3.33",
    "HUAWEI-BGP-VPN-MIB::hwBgpPeerAddrFamilyPerRouteThresholdExceedClear": "1.3.6.1.4.1.2011.5.25.177.1.3.34",
    "HUAWEI-BGP-VPN-MIB::hwBgpPeerAddrFamilyPerRouteExceed": "1.3.6.1.4.1.2011.5.25.177.1.3.35",
    "HUAWEI-BGP-VPN-MIB::hwBgpPeerAddrFamilyPerRouteExceedClear": "1.3.6.1.4.1.2011.5.25.177.1.3.36",
    "HUAWEI-BGP-VPN-MIB::hwBgpRouteLoopDetected": "1.3.6.1.4.1.2011.5.25.177.1.3.37",
    "HUAWEI-BGP-VPN-MIB::hwBgpRouteLoopDetectedClear": "1.3.6.1.4.1.2011.5.25.177.1.3.38",
    "HUAWEI-BGP-VPN-MIB::hwBgpDiscardRecvRoute": "1.3.6.1.4.1.2011.5.25.177.1.3.39",
    "HUAWEI-BGP-VPN-MIB::hwBgpDiscardRecvRouteClear": "1.3.6.1.4.1.2011.5.25.177.1.3.40",
    "HUAWEI-BGP-VPN-MIB::hwBgpUnnumberedPeerBackwardTransition": "1.3.6.1.4.1.2011.5.25.177.1.3.41",
    "HUAWEI-BGP-VPN-MIB::hwBgpUnnumberedPeerEstablished": "1.3.6.1.4.1.2011.5.25.177.1.3.42",
    "HUAWEI-BGP-VPN-MIB::hwBgpUnnumberedPeerRouteExceed": "1.3.6.1.4.1.2011.5.25.177.1.3.43",
    "HUAWEI-BGP-VPN-MIB::hwBgpUnnumberedPeerRouteExceedClear": "1.3.6.1.4.1.2011.5.25.177.1.3.44",
    "HUAWEI-BGP-VPN-MIB::hwBgpUnnumberedPeerRouteNumThresholdExceed": "1.3.6.1.4.1.2011.5.25.177.1.3.45",
    "HUAWEI-BGP-VPN-MIB::hwBgpUnnumberedPeerRouteNumThresholdExceedClear": "1.3.6.1.4.1.2011.5.25.177.1.3.46",
    "HUAWEI-BGP-VPN-MIB::hwBgpRoaCheckFail": "1.3.6.1.4.1.2011.5.25.177.1.3.47",
    "HUAWEI-BGP-VPN-MIB::hwBgpSidLabelConflict": "1.3.6.1.4.1.2011.5.25.177.1.3.48",
    "HUAWEI-BGP-VPN-MIB::hwBgpSidLabelConflictClear": "1.3.6.1.4.1.2011.5.25.177.1.3.49",
    "HUAWEI-BGP-VPN-MIB::hwBgpPdPeerAddrFamilyRouteThresholdExceed": "1.3.6.1.4.1.2011.5.25.177.1.3.50",
    "HUAWEI-BGP-VPN-MIB::hwBgpPdPeerAddrFamilyRouteThresholdExceedClear": "1.3.6.1.4.1.2011.5.25.177.1.3.51",
    "HUAWEI-BGP-VPN-MIB::hwBgpPdPeerAddrFamilyRouteExceed": "1.3.6.1.4.1.2011.5.25.177.1.3.52",
    "HUAWEI-BGP-VPN-MIB::hwBgpPdPeerAddrFamilyRouteExceedClear": "1.3.6.1.4.1.2011.5.25.177.1.3.53",
    "HUAWEI-BGP-VPN-MIB::hwBgpMultiVpnRouteLabelNumReachMaximum": "1.3.6.1.4.1.2011.5.25.177.1.3.54",
    "HUAWEI-BGP-VPN-MIB::hwBgpMultiVpnRouteLabelNumReachMaximumClear": "1.3.6.1.4.1.2011.5.25.177.1.3.55",
    "HUAWEI-BGP-VPN-MIB::hwBgpMultiVpnRouteLabelNumReachThresold": "1.3.6.1.4.1.2011.5.25.177.1.3.56",
    "HUAWEI-BGP-VPN-MIB::hwBgpMultiVpnRouteLabelNumReachThresoldClear": "1.3.6.1.4.1.2011.5.25.177.1.3.57",
    "HUAWEI-BGP-VPN-MIB::hwBgpMultiDynamicPeerSessionExceed": "1.3.6.1.4.1.2011.5.25.177.1.3.58",
    "HUAWEI-BGP-VPN-MIB::hwBgpMultiDynamicPeerSessionExceedClear": "1.3.6.1.4.1.2011.5.25.177.1.3.59",
    "HUAWEI-BGP-VPN-MIB::hwBgpScalars": "1.3.6.1.4.1.2011.5.25.177.1.4",
    "HUAWEI-BGP-VPN-MIB::hwBgpPeerSessionNum": "1.3.6.1.4.1.2011.5.25.177.1.4.1",
    "HUAWEI-BGP-VPN-MIB::hwIBgpPeerSessionNum": "1.3.6.1.4.1.2011.5.25.177.1.4.2",
    "HUAWEI-BGP-VPN-MIB::hwEBgpPeerSessionNum": "1.3.6.1.4.1.2011.5.25.177.1.4.3",
    "HUAWEI-BGP-VPN-MIB::hwBgpPeerSessionMaxNum": "1.3.6.1.4.1.2011.5.25.177.1.4.4",
    "HUAWEI-BGP-VPN-MIB::hwBgpDynamicPeerSessionNum": "1.3.6.1.4.1.2011.5.25.177.1.4.5",
    "HUAWEI-BGP-VPN-MIB::hwBgpDynamicPeerSessionMaxNum": "1.3.6.1.4.1.2011.5.25.177.1.4.6",
    "HUAWEI-BGP-VPN-MIB::hwBgpPeerSessionThreshold": "1.3.6.1.4.1.2011.5.25.177.1.4.7",
    "HUAWEI-BGP-VPN-MIB::hwBgpPeerTotalInUpdateMsgs": "1.3.6.1.4.1.2011.5.25.177.1.4.8",
    "HUAWEI-BGP-VPN-MIB::hwBgpPeerTotalOutUpdateMsgs": "1.3.6.1.4.1.2011.5.25.177.1.4.9",
    "HUAWEI-BGP-VPN-MIB::hwBgpProcess": "1.3.6.1.4.1.2011.5.25.177.1.5",
    "HUAWEI-BGP-VPN-MIB::hwBgpProcessCommTable": "1.3.6.1.4.1.2011.5.25.177.1.5.1",
    "HUAWEI-BGP-VPN-MIB::hwBgpProcessCommEntry": "1.3.6.1.4.1.2011.5.25.177.1.5.1.1",
    "HUAWEI-BGP-VPN-MIB::hwBgpProcessName": "1.3.6.1.4.1.2011.5.25.177.1.5.1.1.1",
    "HUAWEI-BGP-VPN-MIB::hwBgpVpnObjects": "1.3.6.1.4.1.2011.5.25.177.2",
    "HUAWEI-BGP-VPN-MIB::hwBgpVpnTunnelTable": "1.3.6.1.4.1.2011.5.25.177.2.1",
    "HUAWEI-BGP-VPN-MIB::hwBgpVpnTunnelEntry": "1.3.6.1.4.1.2011.5.25.177.2.1.1",
    "HUAWEI-BGP-VPN-MIB::hwBgpVpnTunnelVrfName": "1.3.6.1.4.1.2011.5.25.177.2.1.1.1",
    "HUAWEI-BGP-VPN-MIB::hwBgpVpnTunnelPublicNetNextHop": "1.3.6.1.4.1.2011.5.25.177.2.1.1.2",
    "HUAWEI-BGP-VPN-MIB::hwBgpVpnTunnelId": "1.3.6.1.4.1.2011.5.25.177.2.1.1.3",
    "HUAWEI-BGP-VPN-MIB::hwBgpVpnTunnelDestAddr": "1.3.6.1.4.1.2011.5.25.177.2.1.1.4",
    "HUAWEI-BGP-VPN-MIB::hwBgpVpnTunnelType": "1.3.6.1.4.1.2011.5.25.177.2.1.1.5",
    "HUAWEI-BGP-VPN-MIB::hwBgpVpnTunnelSrcAddr": "1.3.6.1.4.1.2011.5.25.177.2.1.1.6",
    "HUAWEI-BGP-VPN-MIB::hwBgpVpnTunnelOutIfName": "1.3.6.1.4.1.2011.5.25.177.2.1.1.7",
    "HUAWEI-BGP-VPN-MIB::hwBgpVpnTunnelIsLoadBalance": "1.3.6.1.4.1.2011.5.25.177.2.1.1.8",
    "HUAWEI-BGP-VPN-MIB::hwBgpVpnTunnelLspIndex": "1.3.6.1.4.1.2011.5.25.177.2.1.1.9",
    "HUAWEI-BGP-VPN-MIB::hwBgpVpnTunnelLspOutIfName": "1.3.6.1.4.1.2011.5.25.177.2.1.1.10",
    "HUAWEI-BGP-VPN-MIB::hwBgpVpnTunnelLspOutLabel": "1.3.6.1.4.1.2011.5.25.177.2.1.1.11",
    "HUAWEI-BGP-VPN-MIB::hwBgpVpnTunnelLspNextHop": "1.3.6.1.4.1.2011.5.25.177.2.1.1.12",
    "HUAWEI-BGP-VPN-MIB::hwBgpVpnTunnelLspFec": "1.3.6.1.4.1.2011.5.25.177.2.1.1.13",
    "HUAWEI-BGP-VPN-MIB::hwBgpVpnTunnelLspFecPfxLen": "1.3.6.1.4.1.2011.5.25.177.2.1.1.14",
    "HUAWEI-BGP-VPN-MIB::hwBgpVpnTunnelLspIsBackup": "1.3.6.1.4.1.2011.5.25.177.2.1.1.15",
    "HUAWEI-BGP-VPN-MIB::hwBgpVpnTunnelSignalProtocol": "1.3.6.1.4.1.2011.5.25.177.2.1.1.16",
    "HUAWEI-BGP-VPN-MIB::hwBgpVpnTunnelSessionTunnelId": "1.3.6.1.4.1.2011.5.25.177.2.1.1.17",
    "HUAWEI-BGP-VPN-MIB::hwBgpVpnTunnelTunnelName": "1.3.6.1.4.1.2011.5.25.177.2.1.1.18",
    "HUAWEI-BGP-VPN-MIB::hwBgpVpnServiceIdTable": "1.3.6.1.4.1.2011.5.25.177.2.2",
    "HUAWEI-BGP-VPN-MIB::hwBgpVpnServiceIdEntry": "1.3.6.1.4.1.2011.5.25.177.2.2.1",
    "HUAWEI-BGP-VPN-MIB::hwBgpVpnServiceIdVrfName": "1.3.6.1.4.1.2011.5.25.177.2.2.1.1",
    "HUAWEI-BGP-VPN-MIB::hwBgpVpnServiceIdValue": "1.3.6.1.4.1.2011.5.25.177.2.2.1.2",
    "HUAWEI-BGP-VPN-MIB::hwBgpVpnScalars": "1.3.6.1.4.1.2011.5.25.177.2.3",
    "HUAWEI-BGP-VPN-MIB::hwConfiguredVrfs": "1.3.6.1.4.1.2011.5.25.177.2.3.1",
    "HUAWEI-BGP-VPN-MIB::hwConfiguredIpv4Vrfs": "1.3.6.1.4.1.2011.5.25.177.2.3.2",
    "HUAWEI-BGP-VPN-MIB::hwConfiguredIpv6Vrfs": "1.3.6.1.4.1.2011.5.25.177.2.3.3",
    "HUAWEI-BGP-VPN-MIB::hwBgpConformance": "1.3.6.1.4.1.2011.5.25.177.3",
    "HUAWEI-BGP-VPN-MIB::hwBgpCompliances": "1.3.6.1.4.1.2011.5.25.177.3.1",
    "HUAWEI-BGP-VPN-MIB::hwBgpGroups": "1.3.6.1.4.1.2011.5.25.177.3.2",
    "HUAWEI-BGP-VPN-MIB::hwBgpVpnConformance": "1.3.6.1.4.1.2011.5.25.177.5",
    "HUAWEI-BGP-VPN-MIB::hwBgpVpnCompliances": "1.3.6.1.4.1.2011.5.25.177.5.1",
    "HUAWEI-BGP-VPN-MIB::hwBgpVpnExtGroups": "1.3.6.1.4.1.2011.5.25.177.5.2",
    "HUAWEI-BGP-VPN-MIB::hwTnl2VpnTrapObjects": "1.3.6.1.4.1.2011.5.25.177.6",
    "HUAWEI-BGP-VPN-MIB::hwTnl2VpnTrapTable": "1.3.6.1.4.1.2011.5.25.177.6.1",
    "HUAWEI-BGP-VPN-MIB::hwTnl2VpnTrapEntry": "1.3.6.1.4.1.2011.5.25.177.6.1.1",
    "HUAWEI-BGP-VPN-MIB::hwVpnId": "1.3.6.1.4.1.2011.5.25.177.6.1.1.1",
    "HUAWEI-BGP-VPN-MIB::hwVpnPublicNextHop": "1.3.6.1.4.1.2011.5.25.177.6.1.1.2",
    "HUAWEI-BGP-VPN-MIB::hwTunnelReachablityEvent": "1.3.6.1.4.1.2011.5.25.177.6.1.1.3",
    "HUAWEI-BGP-VPN-MIB::hwVpnTrapCkeyValue": "1.3.6.1.4.1.2011.5.25.177.6.1.1.4",
    "HUAWEI-BGP-VPN-MIB::hwTnl2VpnTrapConformance": "1.3.6.1.4.1.2011.5.25.177.7",
    "HUAWEI-BGP-VPN-MIB::hwTnl2VpnTrapConformances": "1.3.6.1.4.1.2011.5.25.177.7.1",
    "HUAWEI-BGP-VPN-MIB::hwTnl2VpnTrapGroups": "1.3.6.1.4.1.2011.5.25.177.7.2",
    "HUAWEI-BGP-VPN-MIB::hwTnl2VpnTrapNotification": "1.3.6.1.4.1.2011.5.25.177.8",
    "HUAWEI-BGP-VPN-MIB::hwTnl2VpnTrapEvent": "1.3.6.1.4.1.2011.5.25.177.8.1",
    "HUAWEI-BGP-VPN-MIB::hwPeerDistributeObjects": "1.3.6.1.4.1.2011.5.25.177.9",
    "HUAWEI-BGP-VPN-MIB::hwBgpTotalRouteNumber": "1.3.6.1.4.1.2011.5.25.177.9.1",
    "HUAWEI-BGP-VPN-MIB::hwOsNodeTable": "1.3.6.1.4.1.2011.5.25.177.9.2",
    "HUAWEI-BGP-VPN-MIB::hwOsNodeEntry": "1.3.6.1.4.1.2011.5.25.177.9.2.1",
    "HUAWEI-BGP-VPN-MIB::hwCurrSlot": "1.3.6.1.4.1.2011.5.25.177.9.2.1.1",
    "HUAWEI-BGP-VPN-MIB::hwPeerNumber": "1.3.6.1.4.1.2011.5.25.177.9.2.1.4",
    "HUAWEI-BGP-VPN-MIB::hwRouteNumber": "1.3.6.1.4.1.2011.5.25.177.9.2.1.5",
    "HUAWEI-BGP-VPN-MIB::hwDistributeTable": "1.3.6.1.4.1.2011.5.25.177.9.3",
    "HUAWEI-BGP-VPN-MIB::hwDistributeEntry": "1.3.6.1.4.1.2011.5.25.177.9.3.1",
    "HUAWEI-BGP-VPN-MIB::hwDistributeLocId": "1.3.6.1.4.1.2011.5.25.177.9.3.1.1",
    "HUAWEI-BGP-VPN-MIB::hwDistributeName": "1.3.6.1.4.1.2011.5.25.177.9.3.1.2",
    "HUAWEI-BGP-VPN-MIB::hwMigrateSrcSlot": "1.3.6.1.4.1.2011.5.25.177.9.3.1.3",
    "HUAWEI-BGP-VPN-MIB::hwMigrateDestSlot": "1.3.6.1.4.1.2011.5.25.177.9.3.1.4",
    "HUAWEI-BGP-VPN-MIB::hwMigrateReason": "1.3.6.1.4.1.2011.5.25.177.9.3.1.5",
    "HUAWEI-BGP-VPN-MIB::hwPeerDistributeTraps": "1.3.6.1.4.1.2011.5.25.177.9.4",
    "HUAWEI-BGP-VPN-MIB::hwRpkiObjects": "1.3.6.1.4.1.2011.5.25.177.11",
    "HUAWEI-BGP-VPN-MIB::hwRpkiSessions": "1.3.6.1.4.1.2011.5.25.177.11.1",
    "HUAWEI-BGP-VPN-MIB::hwRpkiSessionTable": "1.3.6.1.4.1.2011.5.25.177.11.1.1",
    "HUAWEI-BGP-VPN-MIB::hwRpkiSessionEntry": "1.3.6.1.4.1.2011.5.25.177.11.1.1.1",
    "HUAWEI-BGP-VPN-MIB::hwRpkiSessionVrfName": "1.3.6.1.4.1.2011.5.25.177.11.1.1.1.1",
    "HUAWEI-BGP-VPN-MIB::hwRpkiSessionType": "1.3.6.1.4.1.2011.5.25.177.11.1.1.1.2",
    "HUAWEI-BGP-VPN-MIB::hwSessionIPAddr": "1.3.6.1.4.1.2011.5.25.177.11.1.1.1.3",
    "HUAWEI-BGP-VPN-MIB::hwRpkiSessionRoaLimitNum": "1.3.6.1.4.1.2011.5.25.177.11.1.1.1.4",
    "HUAWEI-BGP-VPN-MIB::hwRpkiTraps": "1.3.6.1.4.1.2011.5.25.177.11.2",
    "HUAWEI-BGP-VPN-MIB::hwRpkiSessionRoaExceed": "1.3.6.1.4.1.2011.5.25.177.11.2.1",
    "HUAWEI-BGP-VPN-MIB::hwRpkiSessionRoaExceedClear": "1.3.6.1.4.1.2011.5.25.177.11.2.2",
    "HUAWEI-BGP-VPN-MIB::hwRpkiConformance": "1.3.6.1.4.1.2011.5.25.177.11.3",
    "HUAWEI-BGP-VPN-MIB::hwRpkiCompliances": "1.3.6.1.4.1.2011.5.25.177.11.3.1",
    "HUAWEI-BGP-VPN-MIB::hwRpkiGroups": "1.3.6.1.4.1.2011.5.25.177.11.3.2",
}

DISPLAY_HINTS = {}
