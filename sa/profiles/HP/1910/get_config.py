# -*- coding: utf-8 -*-
<<<<<<< HEAD
# ---------------------------------------------------------------------
# HP.1910.get_config
# ---------------------------------------------------------------------
# Copyright (C) 2007-2013 The NOC Project
# See LICENSE for details
# ---------------------------------------------------------------------

# NOC modules
from noc.core.script.base import BaseScript
from noc.sa.interfaces.igetconfig import IGetConfig


class Script(BaseScript):
    name = "HP.1910.get_config"
    interface = IGetConfig
=======
##----------------------------------------------------------------------
## HP.1910.get_config
##----------------------------------------------------------------------
## Copyright (C) 2007-2013 The NOC Project
## See LICENSE for details
##----------------------------------------------------------------------

## NOC modules
import noc.sa.script
from noc.sa.interfaces import IGetConfig


class Script(noc.sa.script.Script):
    name = "HP.1910.get_config"
    implements = [IGetConfig]
>>>>>>> 2ab0ab7718bb7116da2c3953efd466757e11d9ce

    def execute(self):
        # Try snmp first
        """
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
        config = self.cli("display current-configuration")
        config = config.replace('                ', '')
        return self.cleaned_config(config)
