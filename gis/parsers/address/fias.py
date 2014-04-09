# -*- coding: utf-8 -*-
##----------------------------------------------------------------------
## Parse and load FIAS data
##----------------------------------------------------------------------
## Copyright (C) 2007-2014 The NOC Project
## See LICENSE for details
##----------------------------------------------------------------------

## Python modules
import os
from collections import namedtuple
import re
import csv
## Third-party modules
import dbf
## NOC modules
from noc.gis.models.division import Division
from noc.gis.models.building import Building
from noc.gis.models.street import Street
from noc.gis.models.address import Address
from base import AddressParser
from noc.lib.nosql import get_db
from noc.gis.utils.addr.ru import normalize_division


class FIASParser(AddressParser):
    name = "FIAS"
    TOP_NAME = u"Российская Федерация"

    rx_letter = re.compile("^(\d*)([^\d]*)$")
    rx_letter2 = re.compile("^(\d*)([^\d]*)(/\d+)?([^\d]*)$")

    def __init__(self, config, opts):
        super(FIASParser, self).__init__(config, opts)
        self.prefix = self.config.get("fias", "cache")
        self.regions = set()
        for opt in config.options("fias"):
            if opt.startswith("include."):
                self.regions.add(config.get("fias", opt))
        self.oktmo_codes = set()
        for opt in config.options("fias"):
            if opt.startswith("include_oktmo."):
                self.oktmo_codes.add(config.get("fias", opt))
        self.oktmo = {}  # code -> OKTMO
        self.okato = {}  # okato -> OKTMO
        self.div_cache = {}  # okato -> division
        self.aoid_cache = {}  # AOID -> division
        self.street_cache = {}  # AOGUID -> Street

    def download(self):
        self.download_file(
            self.config.get("oktmo", "download_url"),
            os.path.join(self.prefix, "oktmo.csv.gz"),
            auto_deflate=True
        )
        # Check for FIAS files
        if not os.path.isfile(os.path.join(self.prefix, "ADDROBJ.DBF")):
            self.error("FIAS database not found")
            self.error("Please download full DBF version")
            self.error("from http://fias.nalog.ru/Public/DownloadPage.aspx")
            self.error("and unpack it to %s directory" % self.prefix)
            return False
        return True

    def load_oktmo(self):
        self.info("Load OKTMO structure")
        # Inject top level
        for t in self.addrobj.find({"code": {"$regex": "^\d+\d+ 0 000 000 000 000 0000 0000 000$"}}):
            oktmo = t["okato"][:2] + "000000"
            o = OKTMO(okato=t["okato"], oktmo=oktmo,
                      name=t["offname"], parent=None)
            self.oktmo[oktmo] = o
            self.okato[t["okato"]] = o
        # Load CSV
        path = os.path.join(self.prefix, "oktmo.csv")
        with open(path) as f:
            reader = csv.reader(f, delimiter=";")
            reader.next()
            for okato, oktmo, name, parent in reader:
                o = OKTMO(okato=okato, oktmo=oktmo,
                          name=name, parent=parent)
                self.oktmo[oktmo] = o
                self.okato[okato] = o

    def get_addrobj(self, oktmo=None, okato=None, aoguid=None, unique=True):
        q = {}
        if oktmo:
            q["oktmo"] = oktmo
        if okato:
            q["okato"] = okato
        if aoguid:
            q["aoguid"] = aoguid
        r = list(self.addrobj.find(q, limit=2))
        if len(r) == 1:
            return r[0]
        elif len(r) == 2 and not unique:
            return r[0]
        else:
            return None

    def create_division(self, okato):
        """
        Create division by OKATO object
        :returns: Division
        """
        if okato in self.div_cache:
            return self.div_cache[okato]
        o = self.okato[okato]
        d = Division.objects.filter(data__OKATO=okato).first()
        if not d:
            if o.parent:
                p = self.oktmo[o.parent].okato
                parent = self.create_division(p)
            else:
                parent = self.get_top()
            ao = self.get_addrobj(okato=okato)
            self.info("Creating %s" % o.name)
            data = {
                "OKATO": okato
            }
            if ao:
                name = ao["offname"]
                short_name = ao["shortname"]
                if ao.get("oktmo", "").strip():
                    data["OKTMO"] = ao["oktmo"]
                if ao.get("kladr", "").strip():
                    data["KLADR"] = ao["kladr"]
                data["FIAS_AOID"] = ao["aoid"]
                data["FIAS_AOGUID"] = ao["aoguid"]
                data["FIAS_CODE"] = ao["code"]
            else:
                name = o.name
                short_name = None
            if not short_name:
                short_name, name = normalize_division(name)
            d = Division(
                name=name,
                short_name=short_name,
                parent=parent,
                data=data
            )
            d.save()
        self.div_cache[okato] = d
        return d

    def create_division2(self, ao):
        """
        Create division by ADDROBJ, used when OKATO is empty
        :returns: Division
        """
        if ao["aoid"] in self.aoid_cache:
            return self.aoid_cache[ao["aoid"]]
        d = Division.objects.filter(data__FIAS_AOID=ao["aoid"]).first()
        if not d:
            if ao["parentguid"]:
                po = self.get_addrobj(aoguid=ao["parentguid"])
                if po["okato"]:
                    parent = self.create_division(po["okato"])
                else:
                    parent = self.create_division2(po)
            else:
                parent = self.get_top()
            self.info("Creating %s" % ao["offname"])
            data = {}
            name = ao["offname"]
            short_name = ao["shortname"]
            if ao.get("okato", "").strip():
                data["OKATO"] = ao["okato"]
            if ao.get("oktmo", "").strip():
                data["OKTMO"] = ao["oktmo"]
            if ao.get("kladr", "").strip():
                data["KLADR"] = ao["kladr"]
            data["FIAS_AOID"] = ao["aoid"]
            data["FIAS_AOGUID"] = ao["aoguid"]
            data["FIAS_CODE"] = ao["code"]
            if not short_name:
                short_name, name = normalize_division(name)
            d = Division(
                name=name,
                short_name=short_name,
                parent=parent,
                data=data
            )
            d.save()
        self.aoid_cache[ao["aoid"]] = d
        return d

    def create_street(self, aoguid):
        if aoguid in self.street_cache:
            return self.street_cache[aoguid]
        s = Street.objects.filter(data__FIAS_AOGUID=aoguid).first()
        if not s:
            # Create street
            a = self.get_addrobj(aoguid=aoguid, unique=False)
            if not a:
                raise ValueError("Invalid street: AOGUID=%s" % aoguid)
            self.info("Creating street %s %s" % (a["offname"], a["shortname"]))
            p = self.get_addrobj(aoguid=a["parentguid"])
            if not p:
                raise ValueError("Invalid street parent: AOGUID=%s" % a["parentguid"])
            if p["okato"] and p["okato"] in self.okato:
                parent = self.create_division(p["okato"])
            else:
                parent = self.create_division2(p)
            s = Street(
                parent=parent,
                name=a["offname"],
                short_name=a["shortname"],
                data={
                    "FIAS_AOGUID": aoguid
                }
            )
            s.save()
        self.street_cache[aoguid] = s
        return s

    def check_oktmo(self, oktmo):
        oktmo = oktmo.strip()
        for o in self.oktmo_codes:
            if oktmo.startswith(o):
                return True
        return False

    def sync_buildings(self):
        def nq(s):
            if not s:
                return None
            s = s.strip()
            if not s:
                return None
            s = s.replace(".", "/").replace("-", "/")
            return s

        def split_num(s):
            s = nq(s)
            if not s:
                return None, None
            match = self.rx_letter.match(s)
            if not match:
                print r
                raise ValueError("Invalid number: '%s'" % s)
            n, l = match.groups()
            if not n:
                n = None
            if not l:
                l = None
            return n, l

        def split_num2(s):
            s = nq(s)
            if not s:
                return None, None, None
            if "-" in s:
                s = s.replace("-", "/")
            match = self.rx_letter2.match(s)
            if not match:
                print r
                raise ValueError("Invalid number: '%s'" % s)
            n, l1, n2, l2 = match.groups()
            if not n:
                n = None
            if n2:
                n2 = n2[1:]  # strip /
            else:
                n2 = None
            l = l1 or l2
            if not l:
                l = None
            return n, n2, l

        houses = get_db()["noc.cache.fias.houses"]
        houses.drop()
        for reg in self.regions:
            with dbf.Table(os.path.join(self.prefix, "HOUSE%s.DBF" % reg)) as t:
                for r in t:
                    if self.oktmo_codes:
                        if not self.check_oktmo(r.oktmo):
                            continue
                    bd = dict((k, str(r[k]).strip()) for k in t._meta.fields)
                    houses.insert(bd)
                    # Get house from base
                    b = Building.objects.filter(data__FIAS_HOUSEGUID=r.houseguid).first()
                    if b:
                        # @todo: Update data
                        pass
                    else:
                        # Create building
                        d = self.create_division(r.okato)
                        bld = Building(
                            adm_division=d,
                            postal_code=r.postalcode,
                            # @todo: Status
                            # @todo: NORMDOC
                            data={
                                "FIAS_HOUSEGUID": r.houseguid,
                                "OKATO": r.okato,
                                "OKTMO": r.oktmo
                            },
                            start_date=r.startdate,
                            end_date=r.enddate
                        )
                        bld.save()
                        # Create address
                        street = self.create_street(r.aoguid)
                        num, num2, num_letter = split_num2(r.housenum)
                        build, build_letter = split_num(r.buildnum)
                        estate, estate2, estate_letter = None, None, None
                        struct, struct2, struct_letter = None, None, None
                        if r.strucnum.startswith("ВЛ."):
                            estate = r.strucnum[3:].strip()
                        elif r.eststatus in (1, 3):
                            estate, estate2, estate_letter = split_num2(r.strucnum)
                        else:
                            sn = r.strucnum
                            if sn.startswith("СТР"):
                                sn = sn[3:]
                            struct, struct2, struct_letter = split_num2(sn)
                            if r.eststatus == 2 and num == struct:
                                struct = None
                        a = Address(
                            building=bld,
                            street=street,
                            num=num,
                            num2=num2,
                            num_letter=num_letter,
                            build=build,
                            build_letter=build_letter,
                            struct=struct,
                            struct2=struct2,
                            struct_letter=struct_letter,
                            estate=estate,
                            estate2=estate2,
                            estate_letter=estate_letter,
                            data={
                                "FIAS_HOUSEGUID": r.houseguid
                            }
                        )
                        a.save()

    def get_fias_code(self, r):
        """
        Return FIAS code
        """
        r = [
            r.regioncode,
            r.autocode,
            r.areacode,
            r.citycode,
            r.ctarcode,
            r.placecode,
            r.streetcode,
            r.extrcode,
            r.sextcode
        ]
        return " ".join(r)

    def load_addrobj(self):
        self.addrobj = get_db()["noc.cache.fias.addrobj"]
        if not self.opts["reset_cache"]:
            self.info("Using cached ADDROBJ.dbf")
            return
        self.info("Loading ADDROBJ.dbf. Regions %s" % ", ".join(self.regions))
        self.addrobj.drop()
        with dbf.Table(os.path.join(self.prefix, "ADDROBJ.DBF")) as t_addrobj:
            N = 1000
            batch = []
            for r in t_addrobj:
                if r.regioncode not in self.regions:
                    continue
                if r.actstatus != 1:
                    continue  # Skip historical data
                batch += [{
                    "aoid": r.aoid.strip(),
                    "aoguid": r.aoguid.strip(),
                    "offname": r.offname.strip(),
                    "shortname": r.shortname.strip(),
                    "code": self.get_fias_code(r),
                    "postalcode": r.postalcode.strip(),
                    "okato": r.okato.strip(),
                    "oktmo": r.oktmo.strip(),
                    "kladr": r.code.strip(),
                    "parentguid": r.parentguid.strip(),
                    "centstatus": r.centstatus
                }]
                if len(batch) >= N:
                    self.info("   writing %d records" % N)
                    self.addrobj.insert(batch)
                    batch = []
            if batch:
                self.info("   writing %d records" % len(batch))
                self.addrobj.insert(batch)
        self.info("    Creating indexes")
        self.addrobj.ensure_index("okato")
        self.addrobj.ensure_index("aoguid")

    def update_levels(self):
        self.info("Updating levels")
        Division.update_levels()

    def sync(self):
        self.load_addrobj()
        self.load_oktmo()
        self.sync_buildings()
        self.update_levels()

##
OKTMO = namedtuple("OKTMO", ["okato", "oktmo", "name", "parent"])