# ----------------------------------------------------------------------
# FIAS Extractor
# ----------------------------------------------------------------------
# Copyright (C) 2021 The NOC Project
# See LICENSE for details
# ----------------------------------------------------------------------

# python modules
import dbf
import csv
import logging
import requests
import os
import re
from datetime import datetime
from pathlib import Path
from zipfile import ZipFile, is_zipfile

# NOC modules
from .base import BaseExtractor
from ..models.street import Street
from ..models.address import Address
from ..models.building import Building
from ..models.admdiv import AdmDiv
from noc.core.etl.remotesystem.base import BaseRemoteSystem

logger = logging.getLogger(__name__)


class FiasRemoteSystem(BaseRemoteSystem):
    """
    base class

    Configuration variables
    *FIAS_URL* - url of source FIAS data
    *OKTMO_URL* - url of source OKTMO data
    *CACHE_PATH* - dir target download files
    *OKTMO_REGION* - region code OKTMO
    *FIAS_REGION* - region code FIAS
    """

    def extract(self, extractors=None, incremental: bool = False):
        extractors = extractors or []
        for en in self.extractors_order:
            if extractors and en not in extractors:
                self.logger.info("Skipping extractor %s", en)
                continue
            if en not in self.extractors:
                self.logger.info("Extractor %s is not implemented. Skipping", en)
                continue
            xc = self.extractors[en](self)
            xc.extract()


@FiasRemoteSystem.extractor
class AdmDivExtractor(BaseExtractor):
    """
    Oktmo extractor.
    """

    name = "admdiv"
    model = AdmDiv
    twice_code = []

    area_type = (
        "г",
        "гп",
        "д",
        "дп",
        "ж/д",
        "им",
        "кп",
        "м",
        "маяк",
        "мыс",
        "нп",
        "п",
        "п.ст",
        "пгт",
        "рзд",
        "рп",
        "с",
        "сл",
        "ст",
        "у",
        "х",
    )

    def __init__(self, system, *args, **kwargs):
        super(AdmDivExtractor, self).__init__(system)
        self.oktmo_url = str(self.config.get("OKTMO_URL"))
        self.cache_path = str(self.config.get("CACHE_PATH"))
        self.region = str(self.config.get("OKTMO_REGION"))
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

    def extract(self, incremental: bool = False, **kwargs) -> None:
        super().extract(incremental=incremental)

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
        if kod1[1:3] != "00" and kod2 == "000" and kod3 == "000":
            return f"{ter}{kod1[0]}00000000"
        if kod2 != "000" and kod3 == "000":
            return f"{ter}{kod1}000000"
        if kod2 == "000" and kod3 != "000":
            return f"{ter}{kod1}000000"
        if kod2 != "000" and kod3 != "000":
            return f"{ter}{kod1}{kod2}000"
        return ""

    def iter_data(self, checkpoint=None, **kwargs):
        self.download()
        with open(self.csv_path, encoding="cp1251") as f:
            reader = csv.reader(f, delimiter=";", quotechar='"')
            for row in reader:
                ter = row[0]
                kod1 = row[1]
                kod2 = row[2]
                kod3 = row[3]
                if row[6].split()[0] in self.area_type:
                    short_name = " ".join(row[6].split()[1:])
                    name = row[6]
                else:
                    name = short_name = row[6]
                oktmo = f"{ter}{kod1}{kod2}{kod3}"
                if ter == self.region and self.check_twice_code(ter, kod1, kod2, kod3):
                    parent = self.parent_level(ter, kod1, kod2, kod3)
                    parent = "" if parent == oktmo else parent
                    yield f"{oktmo}", parent, name, short_name
                else:
                    continue


@FiasRemoteSystem.extractor
class StreetExtractor(BaseExtractor):
    """
    Street extractor.
    """

    name = "street"
    model = Street

    def __init__(self, system, *args, **kwargs):
        super(StreetExtractor, self).__init__(system)
        self.fias_url = str(self.config.get("FIAS_URL"))
        self.cache_path = str(self.config.get("CACHE_PATH"))
        self.region = str(self.config.get("FIAS_REGION"))
        self.check_path(self.cache_path)
        self.zip_path = os.path.join(self.cache_path, "fias_dbf.zip")
        self.dbf_file = f"ADDROB{self.region}.DBF"
        self.dbf_path = os.path.join(self.cache_path, self.dbf_file)

        self.parent_admdiv_data = self.parent_admdiv_data()

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
                f.extract(self.dbf_file, self.cache_path)
        else:
            raise Exception("zipfile not found!")

    def extract(self, incremental: bool = False, **kwargs) -> None:
        super().extract(incremental=incremental)

    def parent_admdiv_data(self):
        parent = set()
        l_chain = self.system.get_loader_chain()
        line = l_chain.get_loader("admdiv")
        ls = line.get_new_state()
        if not ls:
            ls = line.get_current_state()
        for o in line.iter_jsonl(ls):
            id = getattr(o, "id")
            parent.add(id)
        return parent

    def get_tables(self):
        field_specs = (
            "OKTMO C(11); AOLEVEL N(3,0); SHORTNAME C(10); FORMALNAME C(120);"
            "AOGUID C(36); PARENTGUID C(36); STARTDATE D; ENDDATE D"
        )

        tmp = dbf.Table(filename="tmp", codepage="cp866", field_specs=field_specs, on_disk=False)
        cities = dbf.Table(filename="tmp", codepage="cp866", field_specs=field_specs, on_disk=False)
        streets = dbf.Table(
            filename="tmp", codepage="cp866", field_specs=field_specs, on_disk=False
        )

        with dbf.Table(filename=self.dbf_path, codepage="cp866") as table:
            with tmp:
                for row in table:
                    if (
                        row.AOLEVEL in [7, 4, 35]
                        and row.NEXTID == " " * 36
                        and row.OKTMO != " " * 11
                    ):
                        OKTMO = row.OKTMO.rstrip().zfill(11)
                        tmp.append(
                            (
                                OKTMO,
                                row.AOLEVEL,
                                row.SHORTNAME,
                                row.FORMALNAME,
                                row.AOGUID,
                                row.PARENTGUID,
                                row.STARTDATE,
                                row.ENDDATE,
                            )
                        )

        cities.open(dbf.READ_WRITE)
        streets.open(dbf.READ_WRITE)
        with tmp:
            for record in tmp:
                if record.AOLEVEL in [7]:
                    streets.append(record)
                else:
                    cities.append(record)

        return cities, streets

    def get_parent(self, table, id):
        table.top()
        for r in table:
            if id == r.AOGUID:
                return r
        return None

    def iter_data(self, checkpoint=None, **kwargs):
        self.download()
        cities, streets = self.get_tables()
        for r in streets:
            parent = self.get_parent(cities, r.PARENTGUID)
            if parent and parent.OKTMO in self.parent_admdiv_data:
                yield (
                    r.AOGUID,
                    parent.OKTMO,
                    r.FORMALNAME.rstrip(),
                    r.SHORTNAME.rstrip(),
                    r.STARTDATE,
                    r.ENDDATE,
                )
        cities.close()
        streets.close()


@FiasRemoteSystem.extractor
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
        self.region = str(self.config.get("FIAS_REGION"))
        self.check_path(self.cache_path)
        self.zip_path = os.path.join(self.cache_path, "fias_dbf.zip")
        self.dbf_file = f"HOUSE{self.region}.DBF"
        self.dbf_path = os.path.join(self.cache_path, self.dbf_file)
        self.now = datetime.now().date()

        self.street = self.street_data()
        self.building = self.building_data()

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
                f.extract(self.dbf_file, self.cache_path)
        else:
            raise Exception("zipfile not found!")

    def extract(self, incremental: bool = False, **kwargs) -> None:
        super().extract(incremental=incremental)

    def street_data(self):
        street = set()
        l_chain = self.system.get_loader_chain()
        line = l_chain.get_loader("street")
        ls = line.get_new_state()
        if not ls:
            ls = line.get_current_state()
        for o in line.iter_jsonl(ls):
            id = getattr(o, "id")
            street.add(id)
        return street

    def building_data(self):
        building = set()
        l_chain = self.system.get_loader_chain()
        line = l_chain.get_loader("building")
        ls = line.get_new_state()
        if not ls:
            ls = line.get_current_state()
        for o in line.iter_jsonl(ls):
            id = getattr(o, "id")
            building.add(id)
        return building

    def num_letter(self, num_letter):
        found = re.search(r"^\d+", num_letter.rstrip())
        if found:
            num = found.group()
            letter = num_letter.rstrip()[len(num) :]
            return num, letter
        return None, None

    def iter_data(self, checkpoint=None, **kwargs):
        self.download()
        with dbf.Table(filename=self.dbf_path, codepage="cp866") as table:
            for r in table:
                num, letter = self.num_letter(r.HOUSENUM)
                if (
                    r.ENDDATE >= self.now
                    and num
                    and r.HOUSEGUID in self.building
                    and r.AOGUID in self.street
                ):
                    yield r.HOUSEID, r.HOUSEGUID, r.AOGUID, num, letter


@FiasRemoteSystem.extractor
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
        self.region = str(self.config.get("FIAS_REGION"))
        self.check_path(self.cache_path)
        self.zip_path = os.path.join(self.cache_path, "fias_dbf.zip")
        self.dbf_file_house = f"HOUSE{self.region}.DBF"
        self.dbf_file_address = f"ADDROB{self.region}.DBF"
        self.dbf_path_house = os.path.join(self.cache_path, self.dbf_file_house)
        self.dbf_path_address = os.path.join(self.cache_path, self.dbf_file_address)
        self.now = datetime.now().date()

        self.adm_div = self.adm_div_data()

    def check_path(self, path):
        # check exists cache_path
        dirpath = Path(path)
        if not dirpath.exists() or not dirpath.is_dir():
            os.makedirs(path)

    def adm_div_data(self):
        div_data = set()
        l_chain = self.system.get_loader_chain()
        line = l_chain.get_loader("admdiv")
        ls = line.get_new_state()
        if not ls:
            ls = line.get_current_state()
        for o in line.iter_jsonl(ls):
            id = getattr(o, "id")
            div_data.add(id)
        return div_data

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

    def extract(self, incremental: bool = False, **kwargs) -> None:
        super().extract(incremental=incremental)

    def get_oktmo_data(self):
        oktmo_data = {}
        with dbf.Table(filename=self.dbf_path_address, codepage="cp866") as table:
            for r in table:
                if r.AOLEVEL in [7, 4, 35] and r.NEXTID == " " * 36 and r.OKTMO != " " * 11:
                    oktmo = r.OKTMO.rstrip().zfill(11)
                    oktmo_data[r.AOGUID] = oktmo

        return oktmo_data

    def iter_data(self, checkpoint=None, **kwargs):
        self.download()
        oktmo_data = self.get_oktmo_data()
        with dbf.Table(filename=self.dbf_path_house, codepage="cp866") as table:
            for r in table:
                oktmo = oktmo_data.get(r.AOGUID)
                if r.ENDDATE >= self.now and oktmo and oktmo in self.adm_div:
                    yield r.HOUSEGUID, oktmo, r.POSTALCODE, r.STARTDATE, r.ENDDATE
