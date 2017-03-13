# -*- coding: utf-8 -*-
##----------------------------------------------------------------------
## DCN.DCWS.get_interfaces
##----------------------------------------------------------------------
## Copyright (C) 2007-2017 The NOC Project
## See LICENSE for details
##----------------------------------------------------------------------
## Python modules
import re
## NOC modules
from noc.core.script.base import BaseScript
from noc.sa.interfaces.igetinterfaces import IGetInterfaces


class Script(BaseScript):
    name = "DCN.DCWS.get_interfaces"
    cache = True
    interface = IGetInterfaces

    rx_sh_int = re.compile(
        r"\s+(?P<interface>\S+)\s+is\s+(?P<admin_status>up|down),\s+line\s+protocol\s+is\s+(?P<oper_status>up|down)"
        r"\s+(?P<ifname>[^\n]+)"
        r"\s+Hardware is (?P<hardw>[^\n]+)",
    re.MULTILINE | re.IGNORECASE)
    rx_mac = re.compile(
        r"\s+address\s+is\s+(?P<mac>\S+)",
    re.MULTILINE | re.IGNORECASE)
    rx_alias = re.compile(
        r"\s+alias\s+name is (?P<alias>\S+)\s",
    re.MULTILINE | re.IGNORECASE)
    rx_index = re.compile(
        r"\s*index is (?P<ifindex>\S+)",
    re.MULTILINE | re.IGNORECASE)

    def execute(self):
        ver = """Interface brief:
            Ethernet1/0/1 is down, line protocol is down
            Ethernet1/0/1 is layer 2 port, alias name is (null), index is 1
            Hardware is Gigabit-TX, address is 00-03-0f-61-e0-21
            PVID is 1
            MTU 1500 bytes, BW 10000 Kbit
            Time since last status change:31w-2d-6h-59m-2s  (18946742 seconds)
            Encapsulation ARPA, Loopback not set
            Auto-duplex, Auto-speed
            FlowControl is off, MDI type is auto
          Transceiver info:
          Statistics:
            5 minute input rate 0 bits/sec, 0 packets/sec
            5 minute output rate 0 bits/sec, 0 packets/sec
            The last 5 second input rate 0 bits/sec, 0 packets/sec
            The last 5 second output rate 0 bits/sec, 0 packets/sec
            Input packets statistics:
              0 input packets, 0 bytes, 0 no buffer
              0 unicast packets, 0 multicast packets, 0 broadcast packets
              0 input errors, 0 CRC, 0 frame alignment, 0 overrun, 0 ignored,
              0 abort, 0 length error, 0 pause frame
            Output packets statistics:
              0 output packets, 0 bytes, 0 underruns
              0 unicast packets, 0 multicast packets, 0 broadcast packets
              0 output errors, 0 collisions, 0 late collisions, 0 pause frame
            Input and output packets by length:
              (64)        bytes:         0, (65~127)    bytes:         0,
              (128~255)   bytes:         0, (256~511)   bytes:         0,
              (512~1023)  bytes:         0, (1024~1518) bytes:         0
            Output packets dropped because of no buffer: 0
            Input IPv4 L3 packets:
              0 unicast packets, 0 multicast packets,
              0 IP header error packets, 0 discard packets
            Output IPv4 L3 packets:
              0 unicast packets, 0 multicast packets, 0 aged and dropped packets
            Input IPv6 L3 packets:
              0 unicast packets, 0 multicast packets,
              0 IP header error packets, 0 discard packets
            Output IPv6 L3 packets:
              0 unicast packets, 0 multicast packets,
              0 aged and dropped packets
          Interface brief:
            Ethernet1/0/2 is down, line protocol is down
            Ethernet1/0/2 is layer 2 port, alias name is (null), index is 2
            Hardware is Gigabit-TX, address is 00-03-0f-61-e0-21
            PVID is 1
            MTU 1500 bytes, BW 10000 Kbit
            Time since last status change:31w-2d-6h-59m-2s  (18946742 seconds)
            Encapsulation ARPA, Loopback not set
            Auto-duplex, Auto-speed
            FlowControl is off, MDI type is auto
          Transceiver info:
          Statistics:
            5 minute input rate 0 bits/sec, 0 packets/sec
            5 minute output rate 0 bits/sec, 0 packets/sec
            The last 5 second input rate 0 bits/sec, 0 packets/sec
            The last 5 second output rate 0 bits/sec, 0 packets/sec
            Input packets statistics:
              0 input packets, 0 bytes, 0 no buffer
              0 unicast packets, 0 multicast packets, 0 broadcast packets
              0 input errors, 0 CRC, 0 frame alignment, 0 overrun, 0 ignored,
              0 abort, 0 length error, 0 pause frame
            Output packets statistics:
              0 output packets, 0 bytes, 0 underruns
              0 unicast packets, 0 multicast packets, 0 broadcast packets
              0 output errors, 0 collisions, 0 late collisions, 0 pause frame
            Input and output packets by length:
              (64)        bytes:         0, (65~127)    bytes:         0,
              (128~255)   bytes:         0, (256~511)   bytes:         0,
              (512~1023)  bytes:         0, (1024~1518) bytes:         0
            Output packets dropped because of no buffer: 0
            Input IPv4 L3 packets:
              0 unicast packets, 0 multicast packets,
              0 IP header error packets, 0 discard packets
            Output IPv4 L3 packets:
              0 unicast packets, 0 multicast packets, 0 aged and dropped packets
            Input IPv6 L3 packets:
              0 unicast packets, 0 multicast packets,
              0 IP header error packets, 0 discard packets
            Output IPv6 L3 packets:
              0 unicast packets, 0 multicast packets,
              0 aged and dropped packets
          Interface brief:
            Ethernet1/0/3 is down, line protocol is down
            Ethernet1/0/3 is layer 2 port, alias name is (null), index is 3
    
          TVE-UCN-WC1#show interface
          Interface brief:
            Ethernet1/0/1 is down, line protocol is down
            Ethernet1/0/1 is layer 2 port, alias name is (null), index is 1
            Hardware is Gigabit-TX, address is 00-03-0f-61-e0-21
            PVID is 1
            MTU 1500 bytes, BW 10000 Kbit
            Time since last status change:31w-2d-6h-59m-14s  (18946754 seconds)
            Encapsulation ARPA, Loopback not set
            Auto-duplex, Auto-speed
            FlowControl is off, MDI type is auto
          Transceiver info:
          Statistics:
            5 minute input rate 0 bits/sec, 0 packets/sec
            5 minute output rate 0 bits/sec, 0 packets/sec
            The last 5 second input rate 0 bits/sec, 0 packets/sec
            The last 5 second output rate 0 bits/sec, 0 packets/sec
            Input packets statistics:
              0 input packets, 0 bytes, 0 no buffer
              0 unicast packets, 0 multicast packets, 0 broadcast packets
              0 input errors, 0 CRC, 0 frame alignment, 0 overrun, 0 ignored,
              0 abort, 0 length error, 0 pause frame
            Output packets statistics:
              0 output packets, 0 bytes, 0 underruns
              0 unicast packets, 0 multicast packets, 0 broadcast packets
              0 output errors, 0 collisions, 0 late collisions, 0 pause frame
          Interface brief:
            Ethernet1/0/2 is down, line protocol is down
            Ethernet1/0/2 is layer 2 port, alias name is (null), index is 2
            Hardware is Gigabit-TX, address is 00-03-0f-61-e0-21
            PVID is 1
            MTU 1500 bytes, BW 10000 Kbit
            Time since last status change:31w-2d-6h-59m-14s  (18946754 seconds)
            Encapsulation ARPA, Loopback not set
            Auto-duplex, Auto-speed
            FlowControl is off, MDI type is auto
          Transceiver info:
          Statistics:
            5 minute input rate 0 bits/sec, 0 packets/sec
            5 minute output rate 0 bits/sec, 0 packets/sec
            The last 5 second input rate 0 bits/sec, 0 packets/sec
            The last 5 second output rate 0 bits/sec, 0 packets/sec
            Input packets statistics:
              0 input packets, 0 bytes, 0 no buffer
              0 unicast packets, 0 multicast packets, 0 broadcast packets
              0 input errors, 0 CRC, 0 frame alignment, 0 overrun, 0 ignored,
              0 abort, 0 length error, 0 pause frame
            Output packets statistics:
              0 output packets, 0 bytes, 0 underruns
              0 unicast packets, 0 multicast packets, 0 broadcast packets
              0 output errors, 0 collisions, 0 late collisions, 0 pause frame
          Interface brief:
            Ethernet1/0/3 is down, line protocol is down
            Ethernet1/0/3 is layer 2 port, alias name is (null), index is 3
            Hardware is Gigabit-TX, address is 00-03-0f-61-e0-21
            PVID is 1
            MTU 1500 bytes, BW 10000 Kbit
            Time since last status change:31w-2d-6h-59m-14s  (18946754 seconds)
            Encapsulation ARPA, Loopback not set
            Auto-duplex, Auto-speed
            FlowControl is off, MDI type is auto
          Transceiver info:
          Statistics:
            5 minute input rate 0 bits/sec, 0 packets/sec
            5 minute output rate 0 bits/sec, 0 packets/sec
            The last 5 second input rate 0 bits/sec, 0 packets/sec
            The last 5 second output rate 0 bits/sec, 0 packets/sec
            Input packets statistics:
              0 input packets, 0 bytes, 0 no buffer
              0 unicast packets, 0 multicast packets, 0 broadcast packets
              0 input errors, 0 CRC, 0 frame alignment, 0 overrun, 0 ignored,
              0 abort, 0 length error, 0 pause frame
            Output packets statistics:
              0 output packets, 0 bytes, 0 underruns
              0 unicast packets, 0 multicast packets, 0 broadcast packets
              0 output errors, 0 collisions, 0 late collisions, 0 pause frame
          Interface brief:
            Ethernet1/0/4 is down, line protocol is down
            Ethernet1/0/4 is layer 2 port, alias name is (null), index is 4
            Hardware is Gigabit-TX, address is 00-03-0f-61-e0-21
            PVID is 1
            MTU 1500 bytes, BW 10000 Kbit
            Time since last status change:31w-2d-6h-59m-14s  (18946754 seconds)
            Encapsulation ARPA, Loopback not set
            Auto-duplex, Auto-speed
            FlowControl is off, MDI type is auto
          Transceiver info:
          Statistics:
            5 minute input rate 0 bits/sec, 0 packets/sec
            5 minute output rate 0 bits/sec, 0 packets/sec
            The last 5 second input rate 0 bits/sec, 0 packets/sec
            The last 5 second output rate 0 bits/sec, 0 packets/sec
            Input packets statistics:
              0 input packets, 0 bytes, 0 no buffer
              0 unicast packets, 0 multicast packets, 0 broadcast packets
              0 input errors, 0 CRC, 0 frame alignment, 0 overrun, 0 ignored,
              0 abort, 0 length error, 0 pause frame
            Output packets statistics:
              0 output packets, 0 bytes, 0 underruns
              0 unicast packets, 0 multicast packets, 0 broadcast packets
              0 output errors, 0 collisions, 0 late collisions, 0 pause frame
          Interface brief:
            Ethernet1/0/5 is down, line protocol is down
            Ethernet1/0/5 is layer 2 port, alias name is (null), index is 5
            Hardware is Gigabit-TX, address is 00-03-0f-61-e0-21
            PVID is 1
            MTU 1500 bytes, BW 10000 Kbit
            Time since last status change:31w-2d-6h-59m-14s  (18946754 seconds)
            Encapsulation ARPA, Loopback not set
            Auto-duplex, Auto-speed
            FlowControl is off, MDI type is auto
          Transceiver info:
          Statistics:
            5 minute input rate 0 bits/sec, 0 packets/sec
            5 minute output rate 0 bits/sec, 0 packets/sec
            The last 5 second input rate 0 bits/sec, 0 packets/sec
            The last 5 second output rate 0 bits/sec, 0 packets/sec
            Input packets statistics:
              0 input packets, 0 bytes, 0 no buffer
              0 unicast packets, 0 multicast packets, 0 broadcast packets
              0 input errors, 0 CRC, 0 frame alignment, 0 overrun, 0 ignored,
              0 abort, 0 length error, 0 pause frame
            Output packets statistics:
              0 output packets, 0 bytes, 0 underruns
              0 unicast packets, 0 multicast packets, 0 broadcast packets
              0 output errors, 0 collisions, 0 late collisions, 0 pause frame
          Interface brief:
            Ethernet1/0/6 is down, line protocol is down
            Ethernet1/0/6 is layer 2 port, alias name is (null), index is 6
            Hardware is Gigabit-TX, address is 00-03-0f-61-e0-21
            PVID is 1
            MTU 1500 bytes, BW 10000 Kbit
            Time since last status change:31w-2d-6h-59m-14s  (18946754 seconds)
            Encapsulation ARPA, Loopback not set
            Auto-duplex, Auto-speed
            FlowControl is off, MDI type is auto
          Transceiver info:
          Statistics:
            5 minute input rate 0 bits/sec, 0 packets/sec
            5 minute output rate 0 bits/sec, 0 packets/sec
            The last 5 second input rate 0 bits/sec, 0 packets/sec
            The last 5 second output rate 0 bits/sec, 0 packets/sec
            Input packets statistics:
              0 input packets, 0 bytes, 0 no buffer
              0 unicast packets, 0 multicast packets, 0 broadcast packets
              0 input errors, 0 CRC, 0 frame alignment, 0 overrun, 0 ignored,
              0 abort, 0 length error, 0 pause frame
            Output packets statistics:
              0 output packets, 0 bytes, 0 underruns
              0 unicast packets, 0 multicast packets, 0 broadcast packets
              0 output errors, 0 collisions, 0 late collisions, 0 pause frame
          Interface brief:
            Ethernet1/0/7 is down, line protocol is down
            Ethernet1/0/7 is layer 2 port, alias name is (null), index is 7
            Hardware is Gigabit-TX, address is 00-03-0f-61-e0-21
            PVID is 1
            MTU 1500 bytes, BW 10000 Kbit
            Time since last status change:31w-2d-6h-59m-14s  (18946754 seconds)
            Encapsulation ARPA, Loopback not set
            Auto-duplex, Auto-speed
            FlowControl is off, MDI type is auto
          Transceiver info:
          Statistics:
            5 minute input rate 0 bits/sec, 0 packets/sec
            5 minute output rate 0 bits/sec, 0 packets/sec
            The last 5 second input rate 0 bits/sec, 0 packets/sec
            The last 5 second output rate 0 bits/sec, 0 packets/sec
            Input packets statistics:
              0 input packets, 0 bytes, 0 no buffer
              0 unicast packets, 0 multicast packets, 0 broadcast packets
              0 input errors, 0 CRC, 0 frame alignment, 0 overrun, 0 ignored,
              0 abort, 0 length error, 0 pause frame
            Output packets statistics:
              0 output packets, 0 bytes, 0 underruns
              0 unicast packets, 0 multicast packets, 0 broadcast packets
              0 output errors, 0 collisions, 0 late collisions, 0 pause frame
          Interface brief:
            Ethernet1/0/8 is down, line protocol is down
            Ethernet1/0/8 is layer 2 port, alias name is (null), index is 8
            Hardware is Gigabit-TX, address is 00-03-0f-61-e0-21
            PVID is 1
            MTU 1500 bytes, BW 10000 Kbit
            Time since last status change:31w-2d-6h-59m-14s  (18946754 seconds)
            Encapsulation ARPA, Loopback not set
            Auto-duplex, Auto-speed
            FlowControl is off, MDI type is auto
          Transceiver info:
          Statistics:
            5 minute input rate 0 bits/sec, 0 packets/sec
            5 minute output rate 0 bits/sec, 0 packets/sec
            The last 5 second input rate 0 bits/sec, 0 packets/sec
            The last 5 second output rate 0 bits/sec, 0 packets/sec
            Input packets statistics:
              0 input packets, 0 bytes, 0 no buffer
              0 unicast packets, 0 multicast packets, 0 broadcast packets
              0 input errors, 0 CRC, 0 frame alignment, 0 overrun, 0 ignored,
              0 abort, 0 length error, 0 pause frame
            Output packets statistics:
              0 output packets, 0 bytes, 0 underruns
              0 unicast packets, 0 multicast packets, 0 broadcast packets
              0 output errors, 0 collisions, 0 late collisions, 0 pause frame
          Interface brief:
            Ethernet1/0/9 is down, line protocol is down
            Ethernet1/0/9 is layer 2 port, alias name is (null), index is 9
            Hardware is Gigabit-TX, address is 00-03-0f-61-e0-21
            PVID is 1
            MTU 1500 bytes, BW 10000 Kbit
            Time since last status change:31w-2d-6h-59m-14s  (18946754 seconds)
            Encapsulation ARPA, Loopback not set
            Auto-duplex, Auto-speed
            FlowControl is off, MDI type is auto
          Transceiver info:
          Statistics:
            5 minute input rate 0 bits/sec, 0 packets/sec
            5 minute output rate 0 bits/sec, 0 packets/sec
            The last 5 second input rate 0 bits/sec, 0 packets/sec
            The last 5 second output rate 0 bits/sec, 0 packets/sec
            Input packets statistics:
              0 input packets, 0 bytes, 0 no buffer
              0 unicast packets, 0 multicast packets, 0 broadcast packets
              0 input errors, 0 CRC, 0 frame alignment, 0 overrun, 0 ignored,
              0 abort, 0 length error, 0 pause frame
            Output packets statistics:
              0 output packets, 0 bytes, 0 underruns
              0 unicast packets, 0 multicast packets, 0 broadcast packets
              0 output errors, 0 collisions, 0 late collisions, 0 pause frame
          Interface brief:
            Ethernet1/0/10 is down, line protocol is down
            Ethernet1/0/10 is layer 2 port, alias name is (null), index is 10
            Hardware is Gigabit-TX, address is 00-03-0f-61-e0-21
            PVID is 1
            MTU 1500 bytes, BW 10000 Kbit
            Time since last status change:31w-2d-6h-59m-14s  (18946754 seconds)
            Encapsulation ARPA, Loopback not set
            Auto-duplex, Auto-speed
            FlowControl is off, MDI type is auto
          Transceiver info:
          Statistics:
            5 minute input rate 0 bits/sec, 0 packets/sec
            5 minute output rate 0 bits/sec, 0 packets/sec
            The last 5 second input rate 0 bits/sec, 0 packets/sec
            The last 5 second output rate 0 bits/sec, 0 packets/sec
            Input packets statistics:
              0 input packets, 0 bytes, 0 no buffer
              0 unicast packets, 0 multicast packets, 0 broadcast packets
              0 input errors, 0 CRC, 0 frame alignment, 0 overrun, 0 ignored,
              0 abort, 0 length error, 0 pause frame
            Output packets statistics:
              0 output packets, 0 bytes, 0 underruns
              0 unicast packets, 0 multicast packets, 0 broadcast packets
              0 output errors, 0 collisions, 0 late collisions, 0 pause frame
          Interface brief:
            Ethernet1/0/11 is down, line protocol is down
            Ethernet1/0/11 is layer 2 port, alias name is (null), index is 11
            Hardware is Gigabit-TX, address is 00-03-0f-61-e0-21
            PVID is 1
            MTU 1500 bytes, BW 10000 Kbit
            Time since last status change:31w-2d-6h-59m-14s  (18946754 seconds)
            Encapsulation ARPA, Loopback not set
            Auto-duplex, Auto-speed
            FlowControl is off, MDI type is auto
          Transceiver info:
          Statistics:
            5 minute input rate 0 bits/sec, 0 packets/sec
            5 minute output rate 0 bits/sec, 0 packets/sec
            The last 5 second input rate 0 bits/sec, 0 packets/sec
            The last 5 second output rate 0 bits/sec, 0 packets/sec
            Input packets statistics:
              0 input packets, 0 bytes, 0 no buffer
              0 unicast packets, 0 multicast packets, 0 broadcast packets
              0 input errors, 0 CRC, 0 frame alignment, 0 overrun, 0 ignored,
              0 abort, 0 length error, 0 pause frame
            Output packets statistics:
              0 output packets, 0 bytes, 0 underruns
              0 unicast packets, 0 multicast packets, 0 broadcast packets
              0 output errors, 0 collisions, 0 late collisions, 0 pause frame
          Interface brief:
            Ethernet1/0/12 is down, line protocol is down
            Ethernet1/0/12 is layer 2 port, alias name is (null), index is 12
            Hardware is Gigabit-TX, address is 00-03-0f-61-e0-21
            PVID is 1
            MTU 1500 bytes, BW 10000 Kbit
            Time since last status change:31w-2d-6h-59m-14s  (18946754 seconds)
            Encapsulation ARPA, Loopback not set
            Auto-duplex, Auto-speed
            FlowControl is off, MDI type is auto
          Transceiver info:
          Statistics:
            5 minute input rate 0 bits/sec, 0 packets/sec
            5 minute output rate 0 bits/sec, 0 packets/sec
            The last 5 second input rate 0 bits/sec, 0 packets/sec
            The last 5 second output rate 0 bits/sec, 0 packets/sec
            Input packets statistics:
              0 input packets, 0 bytes, 0 no buffer
              0 unicast packets, 0 multicast packets, 0 broadcast packets
              0 input errors, 0 CRC, 0 frame alignment, 0 overrun, 0 ignored,
              0 abort, 0 length error, 0 pause frame
            Output packets statistics:
              0 output packets, 0 bytes, 0 underruns
              0 unicast packets, 0 multicast packets, 0 broadcast packets
              0 output errors, 0 collisions, 0 late collisions, 0 pause frame
          Interface brief:
            Ethernet1/0/13 is down, line protocol is down
            Ethernet1/0/13 is layer 2 port, alias name is (null), index is 13
            Hardware is Gigabit-TX, address is 00-03-0f-61-e0-21
            PVID is 1
            MTU 1500 bytes, BW 10000 Kbit
            Time since last status change:31w-2d-6h-59m-14s  (18946754 seconds)
            Encapsulation ARPA, Loopback not set
            Auto-duplex, Auto-speed
            FlowControl is off, MDI type is auto
          Transceiver info:
          Statistics:
            5 minute input rate 0 bits/sec, 0 packets/sec
            5 minute output rate 0 bits/sec, 0 packets/sec
            The last 5 second input rate 0 bits/sec, 0 packets/sec
            The last 5 second output rate 0 bits/sec, 0 packets/sec
            Input packets statistics:
              0 input packets, 0 bytes, 0 no buffer
              0 unicast packets, 0 multicast packets, 0 broadcast packets
              0 input errors, 0 CRC, 0 frame alignment, 0 overrun, 0 ignored,
              0 abort, 0 length error, 0 pause frame
            Output packets statistics:
              0 output packets, 0 bytes, 0 underruns
              0 unicast packets, 0 multicast packets, 0 broadcast packets
              0 output errors, 0 collisions, 0 late collisions, 0 pause frame
          Interface brief:
            Ethernet1/0/14 is down, line protocol is down
            Ethernet1/0/14 is layer 2 port, alias name is (null), index is 14
            Hardware is Gigabit-TX, address is 00-03-0f-61-e0-21
            PVID is 1
            MTU 1500 bytes, BW 10000 Kbit
            Time since last status change:31w-2d-6h-59m-14s  (18946754 seconds)
            Encapsulation ARPA, Loopback not set
            Auto-duplex, Auto-speed
            FlowControl is off, MDI type is auto
          Transceiver info:
          Statistics:
            5 minute input rate 0 bits/sec, 0 packets/sec
            5 minute output rate 0 bits/sec, 0 packets/sec
            The last 5 second input rate 0 bits/sec, 0 packets/sec
            The last 5 second output rate 0 bits/sec, 0 packets/sec
            Input packets statistics:
              0 input packets, 0 bytes, 0 no buffer
              0 unicast packets, 0 multicast packets, 0 broadcast packets
              0 input errors, 0 CRC, 0 frame alignment, 0 overrun, 0 ignored,
              0 abort, 0 length error, 0 pause frame
            Output packets statistics:
              0 output packets, 0 bytes, 0 underruns
              0 unicast packets, 0 multicast packets, 0 broadcast packets
              0 output errors, 0 collisions, 0 late collisions, 0 pause frame
          Interface brief:
            Ethernet1/0/15 is down, line protocol is down
            Ethernet1/0/15 is layer 2 port, alias name is (null), index is 15
            Hardware is Gigabit-TX, address is 00-03-0f-61-e0-21
            PVID is 1
            MTU 1500 bytes, BW 10000 Kbit
            Time since last status change:31w-2d-6h-59m-14s  (18946754 seconds)
            Encapsulation ARPA, Loopback not set
            Auto-duplex, Auto-speed
            FlowControl is off, MDI type is auto
          Transceiver info:
          Statistics:
            5 minute input rate 0 bits/sec, 0 packets/sec
            5 minute output rate 0 bits/sec, 0 packets/sec
            The last 5 second input rate 0 bits/sec, 0 packets/sec
            The last 5 second output rate 0 bits/sec, 0 packets/sec
            Input packets statistics:
              0 input packets, 0 bytes, 0 no buffer
              0 unicast packets, 0 multicast packets, 0 broadcast packets
              0 input errors, 0 CRC, 0 frame alignment, 0 overrun, 0 ignored,
              0 abort, 0 length error, 0 pause frame
            Output packets statistics:
              0 output packets, 0 bytes, 0 underruns
              0 unicast packets, 0 multicast packets, 0 broadcast packets
              0 output errors, 0 collisions, 0 late collisions, 0 pause frame
          Interface brief:
            Ethernet1/0/16 is down, line protocol is down
            Ethernet1/0/16 is layer 2 port, alias name is (null), index is 16
            Hardware is Gigabit-TX, address is 00-03-0f-61-e0-21
            PVID is 1
            MTU 1500 bytes, BW 10000 Kbit
            Time since last status change:31w-2d-6h-59m-14s  (18946754 seconds)
            Encapsulation ARPA, Loopback not set
            Auto-duplex, Auto-speed
            FlowControl is off, MDI type is auto
          Transceiver info:
          Statistics:
            5 minute input rate 0 bits/sec, 0 packets/sec
            5 minute output rate 0 bits/sec, 0 packets/sec
            The last 5 second input rate 0 bits/sec, 0 packets/sec
            The last 5 second output rate 0 bits/sec, 0 packets/sec
            Input packets statistics:
              0 input packets, 0 bytes, 0 no buffer
              0 unicast packets, 0 multicast packets, 0 broadcast packets
              0 input errors, 0 CRC, 0 frame alignment, 0 overrun, 0 ignored,
              0 abort, 0 length error, 0 pause frame
            Output packets statistics:
              0 output packets, 0 bytes, 0 underruns
              0 unicast packets, 0 multicast packets, 0 broadcast packets
              0 output errors, 0 collisions, 0 late collisions, 0 pause frame
          Interface brief:
            Ethernet1/0/17 is down, line protocol is down
            Ethernet1/0/17 is layer 2 port, alias name is (null), index is 17
            Hardware is Gigabit-TX, address is 00-03-0f-61-e0-21
            PVID is 1
            MTU 1500 bytes, BW 10000 Kbit
            Time since last status change:31w-2d-6h-59m-14s  (18946754 seconds)
            Encapsulation ARPA, Loopback not set
            Auto-duplex, Auto-speed
            FlowControl is off, MDI type is auto
          Transceiver info:
          Statistics:
            5 minute input rate 0 bits/sec, 0 packets/sec
            5 minute output rate 0 bits/sec, 0 packets/sec
            The last 5 second input rate 0 bits/sec, 0 packets/sec
            The last 5 second output rate 0 bits/sec, 0 packets/sec
            Input packets statistics:
              0 input packets, 0 bytes, 0 no buffer
              0 unicast packets, 0 multicast packets, 0 broadcast packets
              0 input errors, 0 CRC, 0 frame alignment, 0 overrun, 0 ignored,
              0 abort, 0 length error, 0 pause frame
            Output packets statistics:
              0 output packets, 0 bytes, 0 underruns
              0 unicast packets, 0 multicast packets, 0 broadcast packets
              0 output errors, 0 collisions, 0 late collisions, 0 pause frame
          Interface brief:
            Ethernet1/0/18 is down, line protocol is down
            Ethernet1/0/18 is layer 2 port, alias name is (null), index is 18
            Hardware is Gigabit-TX, address is 00-03-0f-61-e0-21
            PVID is 1
            MTU 1500 bytes, BW 10000 Kbit
            Time since last status change:31w-2d-6h-59m-14s  (18946754 seconds)
            Encapsulation ARPA, Loopback not set
            Auto-duplex, Auto-speed
            FlowControl is off, MDI type is auto
          Transceiver info:
          Statistics:
            5 minute input rate 0 bits/sec, 0 packets/sec
            5 minute output rate 0 bits/sec, 0 packets/sec
            The last 5 second input rate 0 bits/sec, 0 packets/sec
            The last 5 second output rate 0 bits/sec, 0 packets/sec
            Input packets statistics:
              0 input packets, 0 bytes, 0 no buffer
              0 unicast packets, 0 multicast packets, 0 broadcast packets
              0 input errors, 0 CRC, 0 frame alignment, 0 overrun, 0 ignored,
              0 abort, 0 length error, 0 pause frame
            Output packets statistics:
              0 output packets, 0 bytes, 0 underruns
              0 unicast packets, 0 multicast packets, 0 broadcast packets
              0 output errors, 0 collisions, 0 late collisions, 0 pause frame
          Interface brief:
            Ethernet1/0/19 is down, line protocol is down
            Ethernet1/0/19 is layer 2 port, alias name is (null), index is 19
            Hardware is Gigabit-TX, address is 00-03-0f-61-e0-21
            PVID is 1
            MTU 1500 bytes, BW 10000 Kbit
            Time since last status change:31w-2d-6h-59m-14s  (18946754 seconds)
            Encapsulation ARPA, Loopback not set
            Auto-duplex, Auto-speed
            FlowControl is off, MDI type is auto
          Transceiver info:
          Statistics:
            5 minute input rate 0 bits/sec, 0 packets/sec
            5 minute output rate 0 bits/sec, 0 packets/sec
            The last 5 second input rate 0 bits/sec, 0 packets/sec
            The last 5 second output rate 0 bits/sec, 0 packets/sec
            Input packets statistics:
              0 input packets, 0 bytes, 0 no buffer
              0 unicast packets, 0 multicast packets, 0 broadcast packets
              0 input errors, 0 CRC, 0 frame alignment, 0 overrun, 0 ignored,
              0 abort, 0 length error, 0 pause frame
            Output packets statistics:
              0 output packets, 0 bytes, 0 underruns
              0 unicast packets, 0 multicast packets, 0 broadcast packets
              0 output errors, 0 collisions, 0 late collisions, 0 pause frame
          Interface brief:
            Ethernet1/0/20 is down, line protocol is down
            Ethernet1/0/20 is layer 2 port, alias name is (null), index is 20
            Hardware is Gigabit-TX, address is 00-03-0f-61-e0-21
            PVID is 1
            MTU 1500 bytes, BW 10000 Kbit
            Time since last status change:31w-2d-6h-59m-14s  (18946754 seconds)
            Encapsulation ARPA, Loopback not set
            Auto-duplex, Auto-speed
            FlowControl is off, MDI type is auto
          Transceiver info:
          Statistics:
            5 minute input rate 0 bits/sec, 0 packets/sec
            5 minute output rate 0 bits/sec, 0 packets/sec
            The last 5 second input rate 0 bits/sec, 0 packets/sec
            The last 5 second output rate 0 bits/sec, 0 packets/sec
            Input packets statistics:
              0 input packets, 0 bytes, 0 no buffer
              0 unicast packets, 0 multicast packets, 0 broadcast packets
              0 input errors, 0 CRC, 0 frame alignment, 0 overrun, 0 ignored,
              0 abort, 0 length error, 0 pause frame
            Output packets statistics:
              0 output packets, 0 bytes, 0 underruns
              0 unicast packets, 0 multicast packets, 0 broadcast packets
              0 output errors, 0 collisions, 0 late collisions, 0 pause frame
          Interface brief:
            Ethernet1/0/21 is up, line protocol is up
            Ethernet1/0/21 is layer 2 port, alias name is Uplink_MGMT, index is 21
            Hardware is Gigabit-Combo, active is Fiber, address is 00-03-0f-61-e0-21
            PVID is 1
            MTU 1500 bytes, BW 1000000 Kbit
            Time since last status change:17w-3d-17h-17m-46s  (10603066 seconds)
            Encapsulation ARPA, Loopback not set
            Auto-duplex: Negotiation full-duplex, Auto-speed: Negotiation 1G bits
            FlowControl is off, MDI type is auto
          Transceiver info:
            SFP found in this port, manufactured by OEM, on Jan 28 2010.
            Type is 1000BASE-LX.  Serial number is SA1M167126.
            Link length is 10000 m for Single Mode Fiber.
            Nominal bit rate is 1200 Mb/s.
            Laser wavelength is 1310 nm.
          Statistics:
            5 minute input rate 44197 bits/sec, 10 packets/sec
            5 minute output rate 9896 bits/sec, 10 packets/sec
            The last 5 second input rate 53611 bits/sec, 12 packets/sec
            The last 5 second output rate 12917 bits/sec, 12 packets/sec
            Input packets statistics:
              157849706 input packets, 98327188779 bytes, 0 no buffer
              157842751 unicast packets, 0 multicast packets, 6955 broadcast packets
              0 input errors, 0 CRC, 0 frame alignment, 0 overrun, 0 ignored,
              0 abort, 0 length error, 0 pause frame
            Output packets statistics:
              147308018 output packets, 14750008061 bytes, 0 underruns
              146683157 unicast packets, 4 multicast packets, 624857 broadcast packets
              0 output errors, 0 collisions, 0 late collisions, 0 pause frame
          Interface brief:
            Ethernet1/0/22 is down, line protocol is down
            Ethernet1/0/22 is layer 2 port, alias name is (null), index is 22
            Hardware is Gigabit-Combo, active is Fiber, address is 00-03-0f-61-e0-21
            PVID is 1
            MTU 1500 bytes, BW 10000 Kbit
            Time since last status change:31w-2d-6h-59m-14s  (18946754 seconds)
            Encapsulation ARPA, Loopback not set
            Auto-duplex, Auto-speed
            FlowControl is off, MDI type is auto
          Transceiver info:
          Statistics:
            5 minute input rate 0 bits/sec, 0 packets/sec
            5 minute output rate 0 bits/sec, 0 packets/sec
            The last 5 second input rate 0 bits/sec, 0 packets/sec
            The last 5 second output rate 0 bits/sec, 0 packets/sec
            Input packets statistics:
              0 input packets, 0 bytes, 0 no buffer
              0 unicast packets, 0 multicast packets, 0 broadcast packets
              0 input errors, 0 CRC, 0 frame alignment, 0 overrun, 0 ignored,
              0 abort, 0 length error, 0 pause frame
            Output packets statistics:
              0 output packets, 0 bytes, 0 underruns
              0 unicast packets, 0 multicast packets, 0 broadcast packets
              0 output errors, 0 collisions, 0 late collisions, 0 pause frame
          Interface brief:
            Ethernet1/0/23 is down, line protocol is down
            Ethernet1/0/23 is layer 2 port, alias name is (null), index is 23
            Hardware is Gigabit-Combo, active is Fiber, address is 00-03-0f-61-e0-21
            PVID is 1
            MTU 1500 bytes, BW 10000 Kbit
            Time since last status change:31w-2d-6h-59m-14s  (18946754 seconds)
            Encapsulation ARPA, Loopback not set
            Auto-duplex, Auto-speed
            FlowControl is off, MDI type is auto
          Transceiver info:
          Statistics:
            5 minute input rate 0 bits/sec, 0 packets/sec
            5 minute output rate 0 bits/sec, 0 packets/sec
            The last 5 second input rate 0 bits/sec, 0 packets/sec
            The last 5 second output rate 0 bits/sec, 0 packets/sec
            Input packets statistics:
              0 input packets, 0 bytes, 0 no buffer
              0 unicast packets, 0 multicast packets, 0 broadcast packets
              0 input errors, 0 CRC, 0 frame alignment, 0 overrun, 0 ignored,
              0 abort, 0 length error, 0 pause frame
            Output packets statistics:
              0 output packets, 0 bytes, 0 underruns
              0 unicast packets, 0 multicast packets, 0 broadcast packets
              0 output errors, 0 collisions, 0 late collisions, 0 pause frame
          Interface brief:
            Ethernet1/0/24 is down, line protocol is down
            Ethernet1/0/24 is layer 2 port, alias name is (null), index is 24
            Hardware is Gigabit-Combo, active is Fiber, address is 00-03-0f-61-e0-21
            PVID is 1
            MTU 1500 bytes, BW 10000 Kbit
            Time since last status change:31w-2d-6h-59m-14s  (18946754 seconds)
            Encapsulation ARPA, Loopback not set
            Auto-duplex, Auto-speed
            FlowControl is off, MDI type is auto
          Transceiver info:
          Statistics:
            5 minute input rate 0 bits/sec, 0 packets/sec
            5 minute output rate 0 bits/sec, 0 packets/sec
            The last 5 second input rate 0 bits/sec, 0 packets/sec
            The last 5 second output rate 0 bits/sec, 0 packets/sec
            Input packets statistics:
              0 input packets, 0 bytes, 0 no buffer
              0 unicast packets, 0 multicast packets, 0 broadcast packets
              0 input errors, 0 CRC, 0 frame alignment, 0 overrun, 0 ignored,
              0 abort, 0 length error, 0 pause frame
            Output packets statistics:
              0 output packets, 0 bytes, 0 underruns
              0 unicast packets, 0 multicast packets, 0 broadcast packets
              0 output errors, 0 collisions, 0 late collisions, 0 pause frame
          Interface brief:
            Ethernet1/0/25 is down, line protocol is down
            Ethernet1/0/25 is layer 2 port, alias name is (null), index is 25
            Hardware is XFP,  address is 00-03-0f-61-e0-21
            PVID is 1
            MTU 1500 bytes, BW 10000 Kbit
            Time since last status change:31w-2d-6h-59m-14s  (18946754 seconds)
            Encapsulation ARPA, Loopback not set
            Auto-duplex, Auto-speed
            FlowControl is off, MDI type is auto
          Transceiver info:
          Statistics:
            5 minute input rate 0 bits/sec, 0 packets/sec
            5 minute output rate 0 bits/sec, 0 packets/sec
            The last 5 second input rate 0 bits/sec, 0 packets/sec
            The last 5 second output rate 0 bits/sec, 0 packets/sec
            Input packets statistics:
              0 input packets, 0 bytes, 0 no buffer
              0 unicast packets, 0 multicast packets, 0 broadcast packets
              0 input errors, 0 CRC, 0 frame alignment, 0 overrun, 0 ignored,
              0 abort, 0 length error, 0 pause frame
            Output packets statistics:
              0 output packets, 0 bytes, 0 underruns
              0 unicast packets, 0 multicast packets, 0 broadcast packets
              0 output errors, 0 collisions, 0 late collisions, 0 pause frame
          Interface brief:
            Ethernet1/0/26 is down, line protocol is down
            Ethernet1/0/26 is layer 2 port, alias name is (null), index is 26
            Hardware is XFP,  address is 00-03-0f-61-e0-21
            PVID is 1
            MTU 1500 bytes, BW 10000 Kbit
            Time since last status change:31w-2d-6h-59m-14s  (18946754 seconds)
            Encapsulation ARPA, Loopback not set
            Auto-duplex, Auto-speed
            FlowControl is off, MDI type is auto
          Transceiver info:
          Statistics:
            5 minute input rate 0 bits/sec, 0 packets/sec
            5 minute output rate 0 bits/sec, 0 packets/sec
            The last 5 second input rate 0 bits/sec, 0 packets/sec
            The last 5 second output rate 0 bits/sec, 0 packets/sec
            Input packets statistics:
              0 input packets, 0 bytes, 0 no buffer
              0 unicast packets, 0 multicast packets, 0 broadcast packets
              0 input errors, 0 CRC, 0 frame alignment, 0 overrun, 0 ignored,
              0 abort, 0 length error, 0 pause frame
            Output packets statistics:
              0 output packets, 0 bytes, 0 underruns
              0 unicast packets, 0 multicast packets, 0 broadcast packets
              0 output errors, 0 collisions, 0 late collisions, 0 pause frame
          Interface brief:
            Ethernet1/0/27 is down, line protocol is down
            Ethernet1/0/27 is layer 2 port, alias name is (null), index is 27
            Hardware is XFP,  address is 00-03-0f-61-e0-21
            PVID is 1
            MTU 1500 bytes, BW 10000 Kbit
            Time since last status change:31w-2d-6h-59m-14s  (18946754 seconds)
            Encapsulation ARPA, Loopback not set
            Auto-duplex, Auto-speed
            FlowControl is off, MDI type is auto
          Transceiver info:
          Statistics:
            5 minute input rate 0 bits/sec, 0 packets/sec
            5 minute output rate 0 bits/sec, 0 packets/sec
            The last 5 second input rate 0 bits/sec, 0 packets/sec
            The last 5 second output rate 0 bits/sec, 0 packets/sec
            Input packets statistics:
              0 input packets, 0 bytes, 0 no buffer
              0 unicast packets, 0 multicast packets, 0 broadcast packets
              0 input errors, 0 CRC, 0 frame alignment, 0 overrun, 0 ignored,
              0 abort, 0 length error, 0 pause frame
            Output packets statistics:
              0 output packets, 0 bytes, 0 underruns
              0 unicast packets, 0 multicast packets, 0 broadcast packets
              0 output errors, 0 collisions, 0 late collisions, 0 pause frame
          Interface brief:
            Ethernet1/0/28 is down, line protocol is down
            Ethernet1/0/28 is layer 2 port, alias name is (null), index is 28
            Hardware is XFP,  address is 00-03-0f-61-e0-21
            PVID is 1
            MTU 1500 bytes, BW 10000 Kbit
            Time since last status change:31w-2d-6h-59m-14s  (18946754 seconds)
            Encapsulation ARPA, Loopback not set
            Auto-duplex, Auto-speed
            FlowControl is off, MDI type is auto
          Transceiver info:
          Statistics:
            5 minute input rate 0 bits/sec, 0 packets/sec
            5 minute output rate 0 bits/sec, 0 packets/sec
            The last 5 second input rate 0 bits/sec, 0 packets/sec
            The last 5 second output rate 0 bits/sec, 0 packets/sec
            Input packets statistics:
              0 input packets, 0 bytes, 0 no buffer
              0 unicast packets, 0 multicast packets, 0 broadcast packets
              0 input errors, 0 CRC, 0 frame alignment, 0 overrun, 0 ignored,
              0 abort, 0 length error, 0 pause frame
            Output packets statistics:
              0 output packets, 0 bytes, 0 underruns
              0 unicast packets, 0 multicast packets, 0 broadcast packets
              0 output errors, 0 collisions, 0 late collisions, 0 pause frame
          Vlan105 is up(0), line protocol is up, dev index is 11105
            Device flag 0x1003(UP BROADCAST MULTICAST)
            Time since last status change:17w-3d-17h-17m-45s  (10603065 seconds)
            IPv4 address is:
              10.217.160.6     255.255.255.252   (Primary)
            VRF Bind: Not Bind
            Hardware is EtherSVI, address is 00-03-0f-61-e0-20
            MTU is 1500 bytes , BW is 0 Kbit
            Encapsulation ARPA, loopback not set
            5 minute input rate 44197 bits/sec, 10 packets/sec
            5 minute output rate 9896 bits/sec, 10 packets/sec
            The last 5 second input rate 53611 bits/sec, 12 packets/sec
            The last 5 second output rate 12917 bits/sec, 12 packets/sec
            Input packets statistics:
              Input queue 0/1200, 0 drops
              157849706 packets input, 3837908267 bytes, 0 no buffer
              0 input errors, 0 CRC, 0 oversize, 0 undersize
               0 jabber, 0 fragments
            Output packets statistics:
              147308018 packets output, 1865106173 bytes, 0 underruns
              0 output errors, 0 collisions"""
        interfaces = []
        v = self.cli("show interface", cached=True)
        for match in self.rx_sh_int.finditer(v):
            name = match.group("interface")
            ifname = match.group("ifname")
            hw = match.group("hardw")
            matchmac = self.rx_mac.search(hw)
            if matchmac:
                mac = matchmac.group("mac")
            matchalias = self.rx_alias.search(ifname)
            if matchalias:
                alias = matchalias.group("alias")
            matchindex = self.rx_index.search(ifname)
            if matchindex:
                ifindex = matchindex.group("ifindex")
            a_stat = match.group("admin_status").lower() == "up"
            o_stat = match.group("oper_status").lower() == "up"
            #print name, mac, index, alias, a_stat, o_stat

            interfaces += [{
                "type": "physical",
                "name": name,
                "mac": mac,
                "admin_status": a_stat,
                "oper_status": o_stat,
                "description": alias,
                "snmp_ifindex": ifindex,
                "subinterfaces": [{
                    "name": name,
                    "mac": mac,
                    "admin_status": a_stat,
                    "oper_status": o_stat,
                    "description": alias,
                    "snmp_ifindex": ifindex,
                    "enabled_afi": ["BRIDGE"],
                }]
            }]
        return [{"interfaces": interfaces}]

