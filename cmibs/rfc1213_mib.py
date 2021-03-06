# ----------------------------------------------------------------------
# RFC1213-MIB
# Compiled MIB
# Do not modify this file directly
# Run ./noc mib make-cmib instead
# ----------------------------------------------------------------------
# Copyright (C) 2007-2020 The NOC Project
# See LICENSE for details
# ----------------------------------------------------------------------

# MIB Name
NAME = "RFC1213-MIB"

# Metadata
LAST_UPDATED = "1970-01-01"
COMPILED = "2020-01-19"

# MIB Data: name -> oid
MIB = {
    "RFC1213-MIB::at": "1.3.6.1.2.1.3",
    "RFC1213-MIB::atTable": "1.3.6.1.2.1.3.1",
    "RFC1213-MIB::atEntry": "1.3.6.1.2.1.3.1.1",
    "RFC1213-MIB::atIfIndex": "1.3.6.1.2.1.3.1.1.1",
    "RFC1213-MIB::atPhysAddress": "1.3.6.1.2.1.3.1.1.2",
    "RFC1213-MIB::atNetAddress": "1.3.6.1.2.1.3.1.1.3",
    "RFC1213-MIB::ip": "1.3.6.1.2.1.4",
    "RFC1213-MIB::ipForwarding": "1.3.6.1.2.1.4.1",
    "RFC1213-MIB::ipDefaultTTL": "1.3.6.1.2.1.4.2",
    "RFC1213-MIB::ipInReceives": "1.3.6.1.2.1.4.3",
    "RFC1213-MIB::ipInHdrErrors": "1.3.6.1.2.1.4.4",
    "RFC1213-MIB::ipInAddrErrors": "1.3.6.1.2.1.4.5",
    "RFC1213-MIB::ipForwDatagrams": "1.3.6.1.2.1.4.6",
    "RFC1213-MIB::ipInUnknownProtos": "1.3.6.1.2.1.4.7",
    "RFC1213-MIB::ipInDiscards": "1.3.6.1.2.1.4.8",
    "RFC1213-MIB::ipInDelivers": "1.3.6.1.2.1.4.9",
    "RFC1213-MIB::ipOutRequests": "1.3.6.1.2.1.4.10",
    "RFC1213-MIB::ipOutDiscards": "1.3.6.1.2.1.4.11",
    "RFC1213-MIB::ipOutNoRoutes": "1.3.6.1.2.1.4.12",
    "RFC1213-MIB::ipReasmTimeout": "1.3.6.1.2.1.4.13",
    "RFC1213-MIB::ipReasmReqds": "1.3.6.1.2.1.4.14",
    "RFC1213-MIB::ipReasmOKs": "1.3.6.1.2.1.4.15",
    "RFC1213-MIB::ipReasmFails": "1.3.6.1.2.1.4.16",
    "RFC1213-MIB::ipFragOKs": "1.3.6.1.2.1.4.17",
    "RFC1213-MIB::ipFragFails": "1.3.6.1.2.1.4.18",
    "RFC1213-MIB::ipFragCreates": "1.3.6.1.2.1.4.19",
    "RFC1213-MIB::ipAddrTable": "1.3.6.1.2.1.4.20",
    "RFC1213-MIB::ipAddrEntry": "1.3.6.1.2.1.4.20.1",
    "RFC1213-MIB::ipAdEntAddr": "1.3.6.1.2.1.4.20.1.1",
    "RFC1213-MIB::ipAdEntIfIndex": "1.3.6.1.2.1.4.20.1.2",
    "RFC1213-MIB::ipAdEntNetMask": "1.3.6.1.2.1.4.20.1.3",
    "RFC1213-MIB::ipAdEntBcastAddr": "1.3.6.1.2.1.4.20.1.4",
    "RFC1213-MIB::ipAdEntReasmMaxSize": "1.3.6.1.2.1.4.20.1.5",
    "RFC1213-MIB::ipRouteTable": "1.3.6.1.2.1.4.21",
    "RFC1213-MIB::ipRouteEntry": "1.3.6.1.2.1.4.21.1",
    "RFC1213-MIB::ipRouteDest": "1.3.6.1.2.1.4.21.1.1",
    "RFC1213-MIB::ipRouteIfIndex": "1.3.6.1.2.1.4.21.1.2",
    "RFC1213-MIB::ipRouteMetric1": "1.3.6.1.2.1.4.21.1.3",
    "RFC1213-MIB::ipRouteMetric2": "1.3.6.1.2.1.4.21.1.4",
    "RFC1213-MIB::ipRouteMetric3": "1.3.6.1.2.1.4.21.1.5",
    "RFC1213-MIB::ipRouteMetric4": "1.3.6.1.2.1.4.21.1.6",
    "RFC1213-MIB::ipRouteNextHop": "1.3.6.1.2.1.4.21.1.7",
    "RFC1213-MIB::ipRouteType": "1.3.6.1.2.1.4.21.1.8",
    "RFC1213-MIB::ipRouteProto": "1.3.6.1.2.1.4.21.1.9",
    "RFC1213-MIB::ipRouteAge": "1.3.6.1.2.1.4.21.1.10",
    "RFC1213-MIB::ipRouteMask": "1.3.6.1.2.1.4.21.1.11",
    "RFC1213-MIB::ipRouteMetric5": "1.3.6.1.2.1.4.21.1.12",
    "RFC1213-MIB::ipRouteInfo": "1.3.6.1.2.1.4.21.1.13",
    "RFC1213-MIB::ipNetToMediaTable": "1.3.6.1.2.1.4.22",
    "RFC1213-MIB::ipNetToMediaEntry": "1.3.6.1.2.1.4.22.1",
    "RFC1213-MIB::ipNetToMediaIfIndex": "1.3.6.1.2.1.4.22.1.1",
    "RFC1213-MIB::ipNetToMediaPhysAddress": "1.3.6.1.2.1.4.22.1.2",
    "RFC1213-MIB::ipNetToMediaNetAddress": "1.3.6.1.2.1.4.22.1.3",
    "RFC1213-MIB::ipNetToMediaType": "1.3.6.1.2.1.4.22.1.4",
    "RFC1213-MIB::ipRoutingDiscards": "1.3.6.1.2.1.4.23",
    "RFC1213-MIB::icmp": "1.3.6.1.2.1.5",
    "RFC1213-MIB::icmpInMsgs": "1.3.6.1.2.1.5.1",
    "RFC1213-MIB::icmpInErrors": "1.3.6.1.2.1.5.2",
    "RFC1213-MIB::icmpInDestUnreachs": "1.3.6.1.2.1.5.3",
    "RFC1213-MIB::icmpInTimeExcds": "1.3.6.1.2.1.5.4",
    "RFC1213-MIB::icmpInParmProbs": "1.3.6.1.2.1.5.5",
    "RFC1213-MIB::icmpInSrcQuenchs": "1.3.6.1.2.1.5.6",
    "RFC1213-MIB::icmpInRedirects": "1.3.6.1.2.1.5.7",
    "RFC1213-MIB::icmpInEchos": "1.3.6.1.2.1.5.8",
    "RFC1213-MIB::icmpInEchoReps": "1.3.6.1.2.1.5.9",
    "RFC1213-MIB::icmpInTimestamps": "1.3.6.1.2.1.5.10",
    "RFC1213-MIB::icmpInTimestampReps": "1.3.6.1.2.1.5.11",
    "RFC1213-MIB::icmpInAddrMasks": "1.3.6.1.2.1.5.12",
    "RFC1213-MIB::icmpInAddrMaskReps": "1.3.6.1.2.1.5.13",
    "RFC1213-MIB::icmpOutMsgs": "1.3.6.1.2.1.5.14",
    "RFC1213-MIB::icmpOutErrors": "1.3.6.1.2.1.5.15",
    "RFC1213-MIB::icmpOutDestUnreachs": "1.3.6.1.2.1.5.16",
    "RFC1213-MIB::icmpOutTimeExcds": "1.3.6.1.2.1.5.17",
    "RFC1213-MIB::icmpOutParmProbs": "1.3.6.1.2.1.5.18",
    "RFC1213-MIB::icmpOutSrcQuenchs": "1.3.6.1.2.1.5.19",
    "RFC1213-MIB::icmpOutRedirects": "1.3.6.1.2.1.5.20",
    "RFC1213-MIB::icmpOutEchos": "1.3.6.1.2.1.5.21",
    "RFC1213-MIB::icmpOutEchoReps": "1.3.6.1.2.1.5.22",
    "RFC1213-MIB::icmpOutTimestamps": "1.3.6.1.2.1.5.23",
    "RFC1213-MIB::icmpOutTimestampReps": "1.3.6.1.2.1.5.24",
    "RFC1213-MIB::icmpOutAddrMasks": "1.3.6.1.2.1.5.25",
    "RFC1213-MIB::icmpOutAddrMaskReps": "1.3.6.1.2.1.5.26",
    "RFC1213-MIB::tcp": "1.3.6.1.2.1.6",
    "RFC1213-MIB::tcpRtoAlgorithm": "1.3.6.1.2.1.6.1",
    "RFC1213-MIB::tcpRtoMin": "1.3.6.1.2.1.6.2",
    "RFC1213-MIB::tcpRtoMax": "1.3.6.1.2.1.6.3",
    "RFC1213-MIB::tcpMaxConn": "1.3.6.1.2.1.6.4",
    "RFC1213-MIB::tcpActiveOpens": "1.3.6.1.2.1.6.5",
    "RFC1213-MIB::tcpPassiveOpens": "1.3.6.1.2.1.6.6",
    "RFC1213-MIB::tcpAttemptFails": "1.3.6.1.2.1.6.7",
    "RFC1213-MIB::tcpEstabResets": "1.3.6.1.2.1.6.8",
    "RFC1213-MIB::tcpCurrEstab": "1.3.6.1.2.1.6.9",
    "RFC1213-MIB::tcpInSegs": "1.3.6.1.2.1.6.10",
    "RFC1213-MIB::tcpOutSegs": "1.3.6.1.2.1.6.11",
    "RFC1213-MIB::tcpRetransSegs": "1.3.6.1.2.1.6.12",
    "RFC1213-MIB::tcpConnTable": "1.3.6.1.2.1.6.13",
    "RFC1213-MIB::tcpConnEntry": "1.3.6.1.2.1.6.13.1",
    "RFC1213-MIB::tcpConnState": "1.3.6.1.2.1.6.13.1.1",
    "RFC1213-MIB::tcpConnLocalAddress": "1.3.6.1.2.1.6.13.1.2",
    "RFC1213-MIB::tcpConnLocalPort": "1.3.6.1.2.1.6.13.1.3",
    "RFC1213-MIB::tcpConnRemAddress": "1.3.6.1.2.1.6.13.1.4",
    "RFC1213-MIB::tcpConnRemPort": "1.3.6.1.2.1.6.13.1.5",
    "RFC1213-MIB::tcpInErrs": "1.3.6.1.2.1.6.14",
    "RFC1213-MIB::tcpOutRsts": "1.3.6.1.2.1.6.15",
    "RFC1213-MIB::udp": "1.3.6.1.2.1.7",
    "RFC1213-MIB::udpInDatagrams": "1.3.6.1.2.1.7.1",
    "RFC1213-MIB::udpNoPorts": "1.3.6.1.2.1.7.2",
    "RFC1213-MIB::udpInErrors": "1.3.6.1.2.1.7.3",
    "RFC1213-MIB::udpOutDatagrams": "1.3.6.1.2.1.7.4",
    "RFC1213-MIB::udpTable": "1.3.6.1.2.1.7.5",
    "RFC1213-MIB::udpEntry": "1.3.6.1.2.1.7.5.1",
    "RFC1213-MIB::udpLocalAddress": "1.3.6.1.2.1.7.5.1.1",
    "RFC1213-MIB::udpLocalPort": "1.3.6.1.2.1.7.5.1.2",
    "RFC1213-MIB::egp": "1.3.6.1.2.1.8",
    "RFC1213-MIB::egpInMsgs": "1.3.6.1.2.1.8.1",
    "RFC1213-MIB::egpInErrors": "1.3.6.1.2.1.8.2",
    "RFC1213-MIB::egpOutMsgs": "1.3.6.1.2.1.8.3",
    "RFC1213-MIB::egpOutErrors": "1.3.6.1.2.1.8.4",
    "RFC1213-MIB::egpNeighTable": "1.3.6.1.2.1.8.5",
    "RFC1213-MIB::egpNeighEntry": "1.3.6.1.2.1.8.5.1",
    "RFC1213-MIB::egpNeighState": "1.3.6.1.2.1.8.5.1.1",
    "RFC1213-MIB::egpNeighAddr": "1.3.6.1.2.1.8.5.1.2",
    "RFC1213-MIB::egpNeighAs": "1.3.6.1.2.1.8.5.1.3",
    "RFC1213-MIB::egpNeighInMsgs": "1.3.6.1.2.1.8.5.1.4",
    "RFC1213-MIB::egpNeighInErrs": "1.3.6.1.2.1.8.5.1.5",
    "RFC1213-MIB::egpNeighOutMsgs": "1.3.6.1.2.1.8.5.1.6",
    "RFC1213-MIB::egpNeighOutErrs": "1.3.6.1.2.1.8.5.1.7",
    "RFC1213-MIB::egpNeighInErrMsgs": "1.3.6.1.2.1.8.5.1.8",
    "RFC1213-MIB::egpNeighOutErrMsgs": "1.3.6.1.2.1.8.5.1.9",
    "RFC1213-MIB::egpNeighStateUps": "1.3.6.1.2.1.8.5.1.10",
    "RFC1213-MIB::egpNeighStateDowns": "1.3.6.1.2.1.8.5.1.11",
    "RFC1213-MIB::egpNeighIntervalHello": "1.3.6.1.2.1.8.5.1.12",
    "RFC1213-MIB::egpNeighIntervalPoll": "1.3.6.1.2.1.8.5.1.13",
    "RFC1213-MIB::egpNeighMode": "1.3.6.1.2.1.8.5.1.14",
    "RFC1213-MIB::egpNeighEventTrigger": "1.3.6.1.2.1.8.5.1.15",
    "RFC1213-MIB::egpAs": "1.3.6.1.2.1.8.6",
}

DISPLAY_HINTS = {}
