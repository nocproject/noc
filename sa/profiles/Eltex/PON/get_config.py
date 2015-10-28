# -*- coding: utf-8 -*-
##----------------------------------------------------------------------
## Eltex.PON.get_config
##----------------------------------------------------------------------
## Copyright (C) 2007-2014 The NOC Project
## See LICENSE for details
##----------------------------------------------------------------------

## Python modules
from __future__ import with_statement
## NOC modules
from noc.core.script.base import BaseScript
from noc.sa.interfaces.igetconfig import IGetConfig


class Script(BaseScript):
    name = "Eltex.PON.get_config"
    interface = IGetConfig

    def execute(self):
        """
        # Try snmp first
        #
        #
        # See bug NOC-291: http://bt.nocproject.org/browse/NOC-291
        #
        #
        if self.snmp and self.access_profile.snmp_rw
            and TFTP_IP and file_name:
            try:
                # The ConfigCopyProtocol is set to TFTP
                self.snmp.set('1.3.6.1.4.1.9.9.96.1.1.1.1.2.111', 1)
                # Set the SourceFileType to running-config
                self.snmp.set('1.3.6.1.4.1.9.9.96.1.1.1.1.3.111', 4)
                # Set the DestinationFileType to networkfile
                self.snmp.set('1.3.6.1.4.1.9.9.96.1.1.1.1.4.111', 1)
                # Sets the ServerAddress to the IP address of the TFTP server
                self.snmp.set('1.3.6.1.4.1.9.9.96.1.1.1.1.5.111', TFTP_IP)
                # Sets the CopyFilename to your desired file name.
                self.snmp.set('1.3.6.1.4.1.9.9.96.1.1.1.1.6.111', file_name)
                # Sets the CopyStatus to active which starts the copy process.
                self.snmp.set('1.3.6.1.4.1.9.9.96.1.1.1.1.14.111', 1)
                conf_file = open(TFTP_root + '/' + file_name, 'r')
                config = conf_file.read()
                conf_file.close()
                config = self.strip_first_lines(config, 0)
                return self.cleaned_config(config)
            except self.snmp.TimeOutError:
                pass
        """

        # Fallback to CLI
        with self.profile.switch(self):
            conf = self.cli("show running-config\r")

        for i in ['0', '1', '2', '3']:
            conf = conf + self.cli("olt " + i)
            for j in [
                'ipmc', 'layer3', 'network', 'ports', 'pppoe', 'traffic'
            ]:
                conf = conf + "\n" + self.cli("show config " + j)
            self.cli("exit")

        return self.cleaned_config(conf)
