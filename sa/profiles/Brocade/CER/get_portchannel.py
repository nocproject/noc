# -*- coding: utf-8 -*-
##----------------------------------------------------------------------
## Brocade.CER.get_portchannel
##----------------------------------------------------------------------
## Copyright (C) 2007-2013 The NOC Project
## See LICENSE for details
##----------------------------------------------------------------------

## Python modules
import re
## NOC modules
from noc.sa.script import Script as NOCScript
from noc.sa.interfaces import IGetPortchannel


class Script(NOCScript):
    """
    Brocade.CER.get_portchannel
    """
    name = 'Brocade.CER.get_portchannel'
    implements = [IGetPortchannel]
    rx_trunk = re.compile('^(?P<name>\\S+)\\s+(?P<type>\\S+)\\s+(?P<deploy>\\S+)\\s+(?P<id>\\d+)\\s+(?P<pri>\\d+\\/\\d+)\\s+(?P<ports>.*)$', re.MULTILINE)

    def execute(self):
        r = []
        rawportlist = []
        st = self.cli('show lag brief')
        for trunk in self.rx_trunk.findall(st):
            self.debug('\nRAWPORTLIST:' + trunk[5] + '<--')
            rawportlist = trunk[5].split('e ')
            self.debug('\nPORTLIST:'.join(map(str, rawportlist)) + '<--')
            portlist = []
            for port in rawportlist:
                if port:
                    port = port.strip()
                    self.debug('\n   PORT:' + port)
                    if port.find(' to ') > 0:
                        first = port.split()[0].split('/')[1]
                        last = port.split()[2].split('/')[1]
                        for n in range(int(first), int(last) + 1):
                            self.debug('\n   ADDING PORT:' + port.split()[0].split('/')[0] + '/' + repr(n))
                            portlist += [port.split()[0].split('/')[0] + '/' + repr(n)]

                    else:
                        self.debug('\n   ADDING PORT:' + port)
                        portlist += [port]

            r += [{'interface': trunk[0],
              'members': portlist,
              'type': trunk[1]}]

        return r
