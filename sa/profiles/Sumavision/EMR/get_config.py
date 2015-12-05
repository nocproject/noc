# -*- coding: utf-8 -*-
__author__ = 'FeNikS'

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
path_to_temp_files = '/tmp/noc'
path_to_files = 'for_sumavision'

def check_path_existence(path):
        folders = path.split("/")
        path = '/'
        for folder in folders:
            if folder:
                path += folder + "/"
                if not os.path.exists(path):
                    os.mkdir(path)

def clear_dir(path):
    if not os.path.exists(path):
        return
    for element in os.listdir(path):
        full_path = os.path.join(path, element)
        if (not os.path.islink(full_path)) and (os.path.isdir(full_path)):
            clear_dir(full_path)
        else:
            os.remove(full_path)
    os.rmdir(path)

class Script(NOCScript):
    name = "Sumavision.EMR.get_config"
    implements = [IGetConfig]

    def execute(self):
        try:
            host = self.access_profile.address
            login = self.access_profile.user
            password = self.access_profile.password
            temp_dir = '/'.join([path_to_temp_files, path_to_files, host, ""])
            clear_dir(temp_dir)
            check_path_existence(temp_dir)

            copy_files = []
            try:
                ftp = FTP(host, login, password)
                ftp.login()
                ftp.cwd(confdir)
                names = []

                ftp.retrlines('NLST', names.append)

                for name in names:
                    if name.endswith(".gz"):
                        copy_file_path = temp_dir + name
                        lf = open(copy_file_path, "wb")
                        ftp.retrbinary("RETR " + name, lf.write, 8*1024)
                        copy_files.append(copy_file_path)
            finally:
                ftp.quit()

            result = ''
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
        finally:
            if temp_dir:
                clear_dir(temp_dir)

        return ''.join(['<root>\n', result, '</root>'])
