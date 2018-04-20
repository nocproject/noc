# -*- coding: utf-8 -*-
<<<<<<< HEAD
# ---------------------------------------------------------------------
# Brocade.CER-ADV.get_interface_status
# ---------------------------------------------------------------------
# Copyright (C) 2007-2013 The NOC Project
# See LICENSE for details
# ---------------------------------------------------------------------

# Python modules
import re
import string
# NOC modules
from noc.core.script.base import BaseScript
from noc.sa.interfaces.igetinterfacestatus import IGetInterfaceStatus
rx_interface_status = re.compile('^(?P<interface>\\S+)\\s+(?P<status>\\S+).+$', re.IGNORECASE)


class Script(BaseScript):
    name = 'Brocade.CER-ADV.get_interface_status'
    interface = IGetInterfaceStatus

    def execute(self, interface = None):
        if self.has_snmp():
            try:
                r = []
                for i, n, s in self.snmp.join([
                    '1.3.6.1.2.1.31.1.1.1.1',
                    '1.3.6.1.2.1.2.2.1.8'
                ]):
=======
##----------------------------------------------------------------------
## Brocade.CER-ADV.get_interface_status
##----------------------------------------------------------------------
## Copyright (C) 2007-2013 The NOC Project
## See LICENSE for details
##----------------------------------------------------------------------

## Python modules
import re
import string
## NOC modules
from noc.sa.script import Script as NOCScript
from noc.sa.interfaces import IGetInterfaceStatus
rx_interface_status = re.compile('^(?P<interface>\\S+)\\s+(?P<status>\\S+).+$', re.IGNORECASE)


class Script(NOCScript):
    name = 'Brocade.CER-ADV.get_interface_status'
    implements = [IGetInterfaceStatus]

    def execute(self, interface = None):
        if self.snmp and self.access_profile.snmp_ro:
            try:
                r = []
                for n, s in self.snmp.join_tables('1.3.6.1.2.1.31.1.1.1.1', '1.3.6.1.2.1.2.2.1.8', bulk=True):
>>>>>>> 2ab0ab7718bb7116da2c3953efd466757e11d9ce
                    r += [{'interface': n,
                      'status': int(s) == 1}]

                return r
            except self.snmp.TimeOutError:
                pass

        r = []
        if interface:
            cmd = 'show interface brief | include ^%s' % interface
        else:
            cmd = 'show interface brief | excl Port'
        for l in self.cli(cmd).splitlines():
            l = l.replace('Disabled', ' Disabled ')
            l = l.replace('Up', ' Up ')
            l = l.replace('DisabN', ' Disabled N')
            match = rx_interface_status.match(l)
            if match:
                r += [{'interface': match.group('interface'),
                  'status': match.group('status').lower() == 'up'}]

        return r
