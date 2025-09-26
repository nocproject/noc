# ----------------------------------------------------------------------
# Migrate Object.connections
# ----------------------------------------------------------------------
# Copyright (C) 2007-2023 The NOC Project
# See LICENSE for details
# ----------------------------------------------------------------------

# Third-party modules
from pymongo import UpdateOne

# NOC modules
from noc.core.migration.base import BaseMigration

PROTOCOL_DIRECTION_CODES = {">", "<", "*"}


class Migration(BaseMigration):
    MAX_BULK_SIZE = 500

    protocol_code_map = {}

    @staticmethod
    def fix_code(code: str):
        code = code.strip()
        if code == "100BASET":
            return "100BASETX"
        if code == "10GBASE-LR":
            return "10GBASELR"
        if code in ("1000BASELH", "1000BASELHT"):
            return "1000BASELX10"
        if code == "1000BASE-LX":
            return "1000BASELX"
        if code == "100BASELX":
            return "100BASELX10"
        if code == "V34bis":
            return "V34"
        if code == "USB2.0":
            return "USB20"
        if code == "100VAC":
            return "110VAC"
        if code == "240VAC":
            return "220VAC"
        if code in ("USB1", "<USB10"):
            return "USB10"
        if code == "USB1.1":
            return "USB11"
        if code.endswith("IC") or code.endswith("IC3") or code.endswith("IC2"):
            return f"CISCO{code}"
        if code == "G.703":
            return "G703"
        if code == "EIA530A":
            return "EIA530"
        if code == "X21":
            return None
        if code in {"48VDC", "48V DC", "48DC", "-36VDC"}:
            return "-48VDC"
        if code in ("RS323", "RS-232"):
            return "RS232"
        if code == "EM":
            return "E&M"
        if code == "TransE1h100M":
            return "TransEth100M"
        if code == "POTS":
            return "PSTN"
        if code == "TransEth10GTransEth10G":
            return "TransEth10G"
        if code in ("-57VDC", "-72VDC", "-60VDC", "-56VDC"):
            return None
        if code == "RS-485":
            return "RS485"
        if code == "ADSL+":
            return "ADSL2+"
        if code == "802.11abgn":
            return "802.11a"
        return code

    def parse_variant(self, code: str):
        d_code, vd_code = "*", None
        if code[0] in PROTOCOL_DIRECTION_CODES:
            # Old format
            d_code, p_code = code[0], code[1:]
            if (
                "-" in p_code
                and p_code[0] != "-"
                and p_code[-2:] != "LR"
                and not p_code.startswith("RS-232")
            ):
                p_code, vd_code = p_code.rsplit("-", 1)
        else:
            p_code = code
        p_code = self.fix_code(p_code)
        if not p_code:
            return None
        if p_code not in self.protocol_code_map:
            # print("Unknown protocol: %s/%s" % (code, p_code))
            return None
        protocol = self.protocol_code_map[p_code]
        return {"protocol": protocol, "direction": d_code, "discriminator": vd_code}

    def load_protocols(self):
        coll = self.mongo_db["protocols"]
        for p in coll.find():
            self.protocol_code_map[p["code"]] = p["_id"]

    def migrate(self):
        self.load_protocols()
        coll = self.mongo_db["noc.objectmodels"]
        bulk = []
        for doc in coll.find({"connections.protocols": {"$exists": True}}, no_cursor_timeout=True):
            connections = doc.get("connections") or []
            new_connections = []
            for c in connections:
                new_proto = []
                for v_code in c.get("protocols") or []:
                    if isinstance(v_code, dict):
                        new_proto += [v_code]
                        continue
                    v_code = self.parse_variant(v_code)
                    if v_code:
                        new_proto += [v_code]
                c["protocols"] = new_proto
                new_connections += [c]
            bulk += [UpdateOne({"_id": doc["_id"]}, {"$set": {"connections": new_connections}})]
            if len(bulk) >= self.MAX_BULK_SIZE:
                coll.bulk_write(bulk)
                # print(bulk[:3])
                bulk = []
        # Write rest of data
        if bulk:
            coll.bulk_write(bulk)
