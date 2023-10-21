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
        if code == "100BASET":
            return "100BASETX"
        elif code == "USB2.0":
            return "USB20"
        elif code == "USB1":
            return "USB10"
        return code

    def parse_variant(self, code: str):
        d_code, vd_code = "*", None
        if code[0] in PROTOCOL_DIRECTION_CODES:
            # Old format
            d_code, p_code = code[0], code[1:]
            if "-" in p_code and p_code[0] != "-":
                p_code, vd_code = p_code.rsplit("-", 1)
        else:
            p_code = code
        p_code = self.fix_code(p_code)
        if p_code not in self.protocol_code_map:
            print("Unknown protocol: %s" % code)
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
                # coll.bulk_write(bulk)
                print(bulk[:3])
                bulk = []
        # Write rest of data
        # if bulk:
        #    coll.bulk_write(bulk)
