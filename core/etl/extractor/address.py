# ----------------------------------------------------------------------
# FIAS Address Extractor
# ----------------------------------------------------------------------
# Copyright (C) 2021 The NOC Project
# See LICENSE for details
# ----------------------------------------------------------------------

# python modules
import dbf
import requests
import os
import re
from datetime import datetime
from pathlib import Path
from zipfile import ZipFile, is_zipfile

# NOC modules
from .base import BaseExtractor
from ..models.address import Address
from noc.core.etl.remotesystem.base import BaseRemoteSystem


class AddressRemoteSystem(BaseRemoteSystem):
    """
    base class

    Configuration variables
    *FIAS_URL* - url of source FIAS data
    *CACHE_PATH* - dir target download files
    *REGION* - region code
    """


@AddressRemoteSystem.extractor
class AddressExtractor(BaseExtractor):
    """
    Address extractor.
    """

    name = "address"
    model = Address

    def __init__(self, system, *args, **kwargs):
        super(AddressExtractor, self).__init__(system)
        self.fias_url = str(self.config.get("FIAS_URL"))
        self.cache_path = str(self.config.get("CACHE_PATH"))
        self.region = str(self.config.get("REGION"))
        self.check_path(self.cache_path)
        self.zip_path = os.path.join(self.cache_path, "fias_dbf.zip")
        self.dbf_file = f"HOUSE{self.region}.DBF"
        self.dbf_path = os.path.join(self.cache_path, self.dbf_file)
        self.now = datetime.now().date()

    def check_path(self, path):
        # check exists cache_path
        dirpath = Path(path)
        if not dirpath.exists() or not dirpath.is_dir():
            os.makedirs(path)

    def download(self):
        if (
            not os.path.isfile(self.zip_path)
            or datetime.fromtimestamp(os.path.getctime(self.zip_path)).date()
            != datetime.now().date()
        ):
            r = requests.get(self.fias_url, stream=True)
            if r.status_code == 200:
                with open(self.zip_path, "wb") as f:
                    for chunk in r.iter_content(1024):
                        f.write(chunk)
            if is_zipfile(self.zip_path):
                with ZipFile(self.zip_path, "r") as f:
                    f.extract(self.dbf_file_house, self.cache_path)
                    f.extract(self.dbf_file_address, self.cache_path)
            else:
                raise Exception("zipfile not found!")

    def extract(self):
        super().extract()
        return

    def num_letter(self, num_letter):
        found = re.search(r"^\d+", num_letter.rstrip())
        if found:
            num = found.group()
            letter = num_letter.rstrip()[len(num) :]
            return num, letter
        else:
            return None, None

    def iter_data(self):
        self.download()
        with dbf.Table(filename=self.dbf_path, codepage="cp866") as table:
            for r in table:
                num, letter = self.num_letter(r.HOUSENUM)
                if r.ENDDATE >= self.now and num:
                    yield r.HOUSEID, r.HOUSEGUID, r.AOGUID, num, letter
