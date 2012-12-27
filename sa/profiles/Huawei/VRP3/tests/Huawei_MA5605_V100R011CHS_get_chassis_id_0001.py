# -*- coding: utf-8 -*-
##----------------------------------------------------------------------
## Huawei.VRP3.get_chassis_id test
## Auto-generated by ./noc debug-script at 27.12.2012 10:01:58
##----------------------------------------------------------------------
## Copyright (C) 2007-2012 The NOC Project
## See LICENSE for details
##----------------------------------------------------------------------

## NOC modules
from noc.lib.test import ScriptTestCase


class Huawei_VRP3_get_chassis_id_Test(ScriptTestCase):
    script = "Huawei.VRP3.get_chassis_id"
    vendor = "Huawei"
    platform = "MA5605"
    version = "V100R011CHS"
    input = {}
    result = {'first_chassis_mac': '00:18:82:6D:93:C2',
 'last_chassis_mac': '00:18:82:6D:93:C2'}
    motd = ''
    cli = {
'show atmlan mac-address':  'show atmlan mac-address\n  MAC address: 00-18-82-6d-93-c2\n \n', 
}
    snmp_get = {}
    snmp_getnext = {}
    http_get = {}
