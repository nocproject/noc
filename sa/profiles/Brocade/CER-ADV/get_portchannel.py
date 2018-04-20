# -*- coding: utf-8 -*-
<<<<<<< HEAD
# ---------------------------------------------------------------------
# Brocade.CER-ADV.get_portchannel
# ---------------------------------------------------------------------
# Copyright (C) 2007-2013 The NOC Project
# See LICENSE for details
# ---------------------------------------------------------------------

# Python modules
import re
# NOC modules
from noc.core.script.base import BaseScript
from noc.sa.interfaces.igetportchannel import IGetPortchannel


class Script(BaseScript):
=======
##----------------------------------------------------------------------
## Brocade.CER-ADV.get_portchannel
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
>>>>>>> 2ab0ab7718bb7116da2c3953efd466757e11d9ce
    """
    Brocade.CER-ADV.get_portchannel
    """
    name = 'Brocade.CER-ADV.get_portchannel'
<<<<<<< HEAD
    interface = IGetPortchannel
=======
    implements = [IGetPortchannel]
>>>>>>> 2ab0ab7718bb7116da2c3953efd466757e11d9ce
    rx_trunk = re.compile('^(?P<name>\\S+)\\s+(?P<type>\\S+)\\s+(?P<deploy>\\S+)\\s+(?P<id>\\d+)\\s+(?P<pri>\\d+\\/\\d+)\\s+(?P<ports>.*)$', re.MULTILINE)

    def execute(self):
        r = []
        rawportlist = []
        st = self.cli('show lag brief')
        for trunk in self.rx_trunk.findall(st):
<<<<<<< HEAD
            self.logger.debug('\nRAWPORTLIST:' + trunk[5] + '<--')
            rawportlist = trunk[5].split('e ')
            self.logger.debug('\nPORTLIST:'.join(map(str, rawportlist)) + '<--')
=======
            self.debug('\nRAWPORTLIST:' + trunk[5] + '<--')
            rawportlist = trunk[5].split('e ')
            self.debug('\nPORTLIST:'.join(map(str, rawportlist)) + '<--')
>>>>>>> 2ab0ab7718bb7116da2c3953efd466757e11d9ce
            portlist = []
            for port in rawportlist:
                if port:
                    port = port.strip()
<<<<<<< HEAD
                    self.logger.debug('\n   PORT:' + port)
=======
                    self.debug('\n   PORT:' + port)
>>>>>>> 2ab0ab7718bb7116da2c3953efd466757e11d9ce
                    if port.find(' to ') > 0:
                        first = port.split()[0].split('/')[1]
                        last = port.split()[2].split('/')[1]
                        for n in range(int(first), int(last) + 1):
<<<<<<< HEAD
                            self.logger.debug('\n   ADDING PORT:' + port.split()[0].split('/')[0] + '/' + repr(n))
                            portlist += [port.split()[0].split('/')[0] + '/' + repr(n)]

                    else:
                        self.logger.debug('\n   ADDING PORT:' + port)
=======
                            self.debug('\n   ADDING PORT:' + port.split()[0].split('/')[0] + '/' + repr(n))
                            portlist += [port.split()[0].split('/')[0] + '/' + repr(n)]

                    else:
                        self.debug('\n   ADDING PORT:' + port)
>>>>>>> 2ab0ab7718bb7116da2c3953efd466757e11d9ce
                        portlist += [port]

            r += [{'interface': trunk[0],
              'members': portlist,
              'type': trunk[1]}]

        return r
