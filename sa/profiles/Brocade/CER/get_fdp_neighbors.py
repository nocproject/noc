# -*- coding: utf-8 -*-
<<<<<<< HEAD
# ---------------------------------------------------------------------
# Brocade.CER.get_fdp_neighbors
# ---------------------------------------------------------------------
# Copyright (C) 2007-2013 The NOC Project
# See LICENSE for details
# ---------------------------------------------------------------------

# Python modules
import re
# NOC modules
from noc.core.script.base import BaseScript
from noc.sa.interfaces.igetfdpneighbors import IGetFDPNeighbors


class Script(BaseScript):
=======
##----------------------------------------------------------------------
## Brocade.CER.get_fdp_neighbors
##----------------------------------------------------------------------
## Copyright (C) 2007-2013 The NOC Project
## See LICENSE for details
##----------------------------------------------------------------------

## Python modules
import re
## NOC modules
from noc.sa.script import Script as NOCScript
from noc.sa.interfaces import IGetFDPNeighbors


class Script(NOCScript):
>>>>>>> 2ab0ab7718bb7116da2c3953efd466757e11d9ce
    """
    Brocade.CER.get_fdp_neighbors
    """
    name = 'Brocade.CER.get_fdp_neighbors'
<<<<<<< HEAD
    interface = IGetFDPNeighbors
    rx_entry = re.compile(r'Device ID: (?P<device_id>\\S+).+?'
                          'Interface:\\s(?P<local_interface>\\S+)\\s+'
                          'Port ID \\(outgoing port\\): (?P<remote_interface>\\S+)',
                          re.MULTILINE | re.DOTALL | re.IGNORECASE)
=======
    implements = [IGetFDPNeighbors]
    rx_entry = re.compile('Device ID: (?P<device_id>\\S+).+?Interface:\\s(?P<local_interface>\\S+)\\s+Port ID \\(outgoing port\\): (?P<remote_interface>\\S+)', re.MULTILINE | re.DOTALL | re.IGNORECASE)
>>>>>>> 2ab0ab7718bb7116da2c3953efd466757e11d9ce

    def execute(self):
        device_id = self.scripts.get_fqdn()
        neighbors = []
        for match in self.rx_entry.finditer(self.cli('show fdp neighbors detail')):
            neighbors += [{'device_id': match.group('device_id'),
<<<<<<< HEAD
                           'local_interface': match.group('local_interface'),
                           'remote_interface': match.group('remote_interface')}]
=======
              'local_interface': match.group('local_interface'),
              'remote_interface': match.group('remote_interface')}]
>>>>>>> 2ab0ab7718bb7116da2c3953efd466757e11d9ce

        return {'device_id': device_id, 'neighbors': neighbors}
