# -*- coding: utf-8 -*-
# ---------------------------------------------------------------------
# Brocade.ADX.get_interface_status
# ---------------------------------------------------------------------
# Copyright (C) 2007-2017 The NOC Project
# See LICENSE for details
# ---------------------------------------------------------------------

# Python modules
import re
# NOC modules
from noc.core.script.base import BaseScript
from noc.sa.interfaces.igetinterfacestatus import IGetInterfaceStatus


class Script(BaseScript):
    name = 'Brocade.ADX.get_interface_status'
    interface = IGetInterfaceStatus

    rx_interface_status = re.compile(
        r"^(?P<interface>\S+)\s+(?P<status>\S+).+$")

    def execute(self, interface=None):
        if self.snmp and self.access_profile.snmp_ro:
            try:
                r = []
                for n, s in self.snmp.join_tables(
                    '1.3.6.1.2.1.31.1.1.1.1',
                    '1.3.6.1.2.1.2.2.1.8'
                ):
                    r += [{'interface': n, 'status': int(s) == 1}]

                return r
            except self.snmp.TimeOutError:
                pass

        r = []
        if interface:
            cmd = 'show interface brief | include ^%s' % interface
        else:
            cmd = 'show interface brief | excl Port'
        for l in self.cli(cmd).splitlines():
            # I do not, what do these lines :(
            # Need more examples
            l = l.replace('Disabled', ' Disabled ')
            l = l.replace('Up', ' Up ')
            l = l.replace('DisabN', ' Disabled N')
            match = self.rx_interface_status.match(l)
            if match:
                r += [{
                    'interface': match.group('interface'),
                    'status': match.group('status').lower() == 'up'
                }]

        return r
