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
        elif code == "10GBASE-LR":
            return "10GBASELR"
        elif code == "1000BASELH" or code == "1000BASELHT":
            return "1000BASELX10"
        elif code == "1000BASE-LX":
            return "1000BASELX"
        elif code == "100BASELX":
            return "100BASELX10"
        elif code == "V34bis":
            return "V34"
        elif code == "USB2.0":
            return "USB20"
        elif code == "100VAC":
            return "110VAC"
        elif code == "240VAC":
            return "220VAC"
        elif code == "USB1" or code == "<USB10":
            return "USB10"
        elif code == "USB1.1":
            return "USB11"
        elif code.endswith("IC") or code.endswith("IC3") or code.endswith("IC2"):
            return f"CISCO{code}"
        elif code == "G.703":
            return "G703"
        elif code == "EIA530A":
            return "EIA530"
        elif code == "X21":
            return None
        elif code in {"48VDC", "48V DC", "48DC", "-36VDC"}:
            return "-48VDC"
        elif code == "RS323" or code == "RS-232":
            return "RS232"
        elif code == "EM":
            return "E&M"
        elif code == "TransE1h100M":
            return "TransEth100M"
        elif code == "POTS":
            return "PSTN"
        elif code == "TransEth10GTransEth10G":
            return "TransEth10G"
        elif code == "-57VDC" or code == "-72VDC" or code == "-60VDC" or code == "-56VDC":
            return
        elif code == "RS-485":
            return "RS485"
        elif code == "ADSL+":
            return "ADSL2+"
        elif code == "802.11abgn":
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
            return
        elif p_code not in self.protocol_code_map:
            # print("Unknown protocol: %s/%s" % (code, p_code))
            return
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
