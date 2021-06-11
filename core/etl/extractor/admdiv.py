# ----------------------------------------------------------------------
# OKTMO Data Extractor
# ----------------------------------------------------------------------
# Copyright (C) 2021 The NOC Project
# See LICENSE for details
# ----------------------------------------------------------------------

# python modules
import requests
import os
import csv
from pathlib import Path

# NOC modules
from .base import BaseExtractor
from ..models.admdiv import AdmDiv
from noc.core.etl.remotesystem.base import BaseRemoteSystem


class AdmDivRemoteSystem(BaseRemoteSystem):
    """
    base class

    Configuration variables
    *OKTMO_URL* - url of source oktmo data
    *CACHE_PATH* - dir target download files
    *REGION* - region code
    """


@AdmDivRemoteSystem.extractor
class AdmDivExtractor(BaseExtractor):
    """
    Oktmo extractor.
    """

    name = "admdiv"
    model = AdmDiv
    twice_code = []

    def __init__(self, system, *args, **kwargs):
        super(AdmDivExtractor, self).__init__(system)
        self.oktmo_url = str(self.config.get("OKTMO_URL"))
        self.cache_path = str(self.config.get("CACHE_PATH"))
        self.region = str(self.config.get("REGION"))
        self.check_path(self.cache_path)
        self.csv_path = None

    def check_path(self, path):
        # check exists cache_path
        dirpath = Path(path)
        if not dirpath.exists() or not dirpath.is_dir():
            os.makedirs(path)

    def download(self):
        r = requests.get(self.oktmo_url, stream=True)
        self.csv_path = os.path.join(self.cache_path, "oktmo.csv")
        if r.status_code == 200:
            with open(self.csv_path, "wb") as f:
                for chunk in r.iter_content(1024):
                    f.write(chunk)

    def extract(self):
        super(AdmDivExtractor, self).extract()
        return

    def check_twice_code(self, ter, kod1, kod2, kod3):
        """
        Checking duble oktmo code

        :param ter:
        :param kod1:
        :param kod2:
        :param kod3:
        :return:
        """
        if kod3 == "000":
            oktmo = f"{ter}{kod1}{kod2}{kod3}"
            if oktmo in self.twice_code:
                return False
            else:
                self.twice_code.append(oktmo)
        return True

    def parent_level(self, ter, kod1, kod2, kod3):
        """
        Creating parent code

        :param ter:
        :param kod1:
        :param kod2:
        :param kod3:
        :return:
        """
        if self.region != "0" and kod1[1:3] == "00" and kod2 == "000" and kod3 == "000":
            return f"{ter}000000000"
        elif kod1[1:3] != "00" and kod2 == "000" and kod3 == "000":
            return f"{ter}{kod1[0]}00000000"
        elif kod2 != "000" and kod3 == "000":
            return f"{ter}{kod1}000000"
        elif kod2 == "000" and kod3 != "000":
            return f"{ter}{kod1}000000"
        elif kod2 != "000" and kod3 != "000":
            return f"{ter}{kod1}{kod2}000"
        else:
            return ""

    def iter_data(self):
        self.download()
        with open(self.csv_path, encoding="cp1251") as f:
            reader = csv.reader(f, delimiter=";", quotechar='"')
            for row in reader:
                ter = row[0]
                kod1 = row[1]
                kod2 = row[2]
                kod3 = row[3]
                name = " ".join(row[6].split()[1:])
                short_name = row[6].split()[0]
                name = " ".join(row[6].split()[1:])
                short_name = row[6].split()[0]
                oktmo = f"{ter}{kod1}{kod2}{kod3}"
                if ter == "04" and self.check_twice_code(ter, kod1, kod2, kod3):
                    parent = self.parent_level(ter, kod1, kod2, kod3)
                    parent = "" if parent == oktmo else parent
                    yield f"{ter}{kod1}{kod2}{kod3}", parent, name, short_name
                else:
                    continue
