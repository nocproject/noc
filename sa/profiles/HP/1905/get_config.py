# -*- coding: utf-8 -*-
##----------------------------------------------------------------------
## HP.1905.get_config
##----------------------------------------------------------------------
## Copyright (C) 2007-2013 The NOC Project
## See LICENSE for details
##----------------------------------------------------------------------

## NOC modules
from noc.sa.script import Script as NOCScript
from noc.sa.interfaces import IGetConfig


class Script(NOCScript):
    name = "HP.1905.get_config"
    implements = [IGetConfig]

    def execute(self, TFTP_root='', TFTP_IP='', file_name=''):
        # Try snmp first
        #
        #
        # See bug NOC-291: http://bt.nocproject.org/browse/NOC-291
        raise Exception("Not implemented")
        #
        #
        if self.snmp and self.access_profile.snmp_rw and TFTP_IP and file_name:
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
#                config = self.strip_first_lines(config, 0)
                return self.cleaned_config(config)
            except self.snmp.TimeOutError:
                pass

        # Fallback to CLI
        raise Exception("Not implemented")
