# ----------------------------------------------------------------------
# FIAS Building Extractor
# ----------------------------------------------------------------------
# Copyright (C) 2021 The NOC Project
# See LICENSE for details
# ----------------------------------------------------------------------

# python modules
import dbf
import requests
import os
from datetime import datetime
from pathlib import Path
from zipfile import ZipFile, is_zipfile

# NOC modules
from .base import BaseExtractor
from ..models.building import Building
from noc.core.etl.remotesystem.base import BaseRemoteSystem


class BuildingRemoteSystem(BaseRemoteSystem):
    """
    base class

    Configuration variables
    *FIAS_URL* - url of source FIAS data
    *CACHE_PATH* - dir target download files
    *REGION* - region code
    """


@BuildingRemoteSystem.extractor
class BuildingExtractor(BaseExtractor):
    """
    Building extractor.
    """

    name = "building"
    model = Building

    def __init__(self, system, *args, **kwargs):
        super(BuildingExtractor, self).__init__(system)
        self.fias_url = str(self.config.get("FIAS_URL"))
        self.cache_path = str(self.config.get("CACHE_PATH"))
        self.region = str(self.config.get("REGION"))
        self.check_path(self.cache_path)
        self.zip_path = os.path.join(self.cache_path, "fias_dbf.zip")
        self.dbf_file_house = f"HOUSE{self.region}.DBF"
        self.dbf_file_address = f"ADDROB{self.region}.DBF"
        self.dbf_path_house = os.path.join(self.cache_path, self.dbf_file_house)
        self.dbf_path_address = os.path.join(self.cache_path, self.dbf_file_address)
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

    def get_oktmo_data(self):
        oktmo_data = {}
        with dbf.Table(filename=self.dbf_path_address, codepage="cp866") as table:
            for r in table:
                if r.AOLEVEL in [7, 4, 35] and r.NEXTID == " " * 36 and r.OKTMO != " " * 11:
                    oktmo = r.OKTMO.rstrip().zfill(11)
                    oktmo_data[r.AOGUID] = oktmo

        return oktmo_data

    def iter_data(self):
        self.download()
        oktmo_data = self.get_oktmo_data()
        with dbf.Table(filename=self.dbf_path_house, codepage="cp866") as table:
            for r in table:
                oktmo = oktmo_data.get(r.AOGUID)
                if r.ENDDATE >= self.now and oktmo:
                    yield r.HOUSEGUID, oktmo, r.POSTALCODE, r.STARTDATE, r.ENDDATE
