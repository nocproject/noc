# -*- coding: utf-8 -*-
##----------------------------------------------------------------------
## Cisco.IOS.get_version test
## Auto-generated by ./noc debug-script at 2011-12-22 16:13:01
##----------------------------------------------------------------------
## Copyright (C) 2007-2011 The NOC Project
## See LICENSE for details
##----------------------------------------------------------------------

## NOC modules
from noc.lib.test import ScriptTestCase


class Cisco_IOS_get_version_Test(ScriptTestCase):
    script = "Cisco.IOS.get_version"
    vendor = "Cisco"
    platform = 'IOS-XE'
    version = '15.0(1)S4'
    input = {}
    result = {'attributes': {'image': 'PPC_LINUX_IOSD-ADVIPSERVICES-M'},
 'platform': 'ASR1004',
 'vendor': 'Cisco',
 'version': '15.0(1)S4'}
    motd = ''
    cli = {
## 'show version'
'show version': """show version
Cisco IOS Software, IOS-XE Software (PPC_LINUX_IOSD-ADVIPSERVICES-M), Version 15.0(1)S4, RELEASE SOFTWARE (fc2)
Technical Support: http://www.cisco.com/techsupport
Copyright (c) 1986-2011 by Cisco Systems, Inc.
Compiled Mon 11-Jul-11 02:29 by mcpre


Cisco IOS-XE software, Copyright (c) 2005-2011 by cisco Systems, Inc.
All rights reserved.  Certain components of Cisco IOS-XE software are
licensed under the GNU General Public License ("GPL") Version 2.0.  The
software code licensed under GPL Version 2.0 is free software that comes
with ABSOLUTELY NO WARRANTY.  You can redistribute and/or modify such
GPL code under the terms of GPL Version 2.0.  For more details, see the
documentation or "License Notice" file accompanying the IOS-XE software,
or the applicable URL provided on the flyer accompanying the IOS-XE
software.


ROM: IOS-XE ROMMON

zoo-asr1004-1 uptime is 15 weeks, 2 days, 11 hours, 5 minutes
Uptime for this control processor is 15 weeks, 2 days, 11 hours, 7 minutes
System returned to ROM by reload at 05:03:00 MSD Tue Sep 6 2011
System restarted at 05:07:04 MSK Tue Sep 6 2011
System image file is "harddisk:asr1000rp1-advipservices.03.01.04.S.150-1.S4.bin"
Last reload reason: Reload Command


cisco ASR1004 (RP1) processor with 1727026K/6147K bytes of memory.
2 Ten Gigabit Ethernet interfaces
32768K bytes of non-volatile configuration memory.
4194304K bytes of physical memory.
937983K bytes of eUSB flash at bootflash:.
39004543K bytes of SATA hard disk at harddisk:.

Configuration register is 0x2102
""", 
'terminal length 0':  'terminal length 0\n', 
}
    snmp_get = {}
    snmp_getnext = {}
    http_get = {}
