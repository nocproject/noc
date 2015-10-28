# -*- coding: utf-8 -*-
__author__ = 'boris'

##----------------------------------------------------------------------
## SUMAVISION.EMR.get_config
##----------------------------------------------------------------------
## Copyright (C) 2007-2015 The NOC Project
## See LICENSE for details
##----------------------------------------------------------------------

#NOC modules
from noc.core.script.base import BaseScript
from noc.sa.interfaces.igetconfig import IGetConfig
#Python modules
import os
from ftplib import FTP
import gzip
from xml.dom.minidom import parseString

confdir = "para"
path_to_temp_files = "/tmp/noc"
path_to_files = "/tmp/noc/for_sumavision/"

class Script(BaseScript):
    name = "SUMAVISION.EMR.get_config"
    interface = IGetConfig

    def execute(self):
        host = self.access_profile.address
        login = self.access_profile.user
        password = self.access_profile.password        

        copy_files = []
        try:
            ftp = FTP(host, login, password)
            ftp.login()
            ftp.cwd(confdir)
            names = []
            if not os.path.exists(path_to_temp_files):
                os.mkdir(path_to_temp_files)
            if not os.path.exists(path_to_files):
                os.mkdir(path_to_files)
            ftp.retrlines('NLST', names.append)

            for name in names:
                if name.endswith(".gz"):
                    copy_file_path = path_to_files + name
                    lf = open(copy_file_path, "wb")
                    ftp.retrbinary("RETR " + name, lf.write, 8*1024)
                    copy_files.append(copy_file_path)
        finally:
            ftp.quit()

        result = '<root>\n'
        for path in copy_files:
            f = gzip.open(path)
            config = f.read()
            config = self.strip_first_lines(config, 1)
            try:
                tree = parseString(config)
                config = tree.toprettyxml()
                config = self.strip_first_lines(config, 1)
                result += config + "\n"
            except Exception:
                pass
            finally:
                f.close()
                os.remove(path)

        return result + "</root>"
