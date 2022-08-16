# ----------------------------------------------------------------------
# Migrate AuthProfile Suggests to Credential Rule
# ----------------------------------------------------------------------
# Copyright (C) 2007-2021 The NOC Project
# See LICENSE for details
# ----------------------------------------------------------------------

# Third-party modules
from pymongo import InsertOne
import bson

# NOC modules
from noc.core.migration.base import BaseMigration


class Migration(BaseMigration):
    def migrate(self):
        coll = self.mongo_db["noc.credentialcheckrules"]

        credentials = {}
        for ap_id, au_name, au_descr in self.db.execute(
            """
                SELECT id, name, description FROM sa_authprofile WHERE type = 'S'
                """
        ):
            credentials[ap_id] = {
                "_id": bson.ObjectId(),
                "name": au_name,
                "description": au_descr or f"Migrate from Suggests AuthProfile {au_name}",
                "is_active": True,
                "match": [],
                "preference": 100,
                "suggest_snmp": [],
                "suggest_credential": [],
                "suggest_auth_profile": [],
                "suggest_protocols": [],
            }
        # SNMP
        for ap_id, snmp_ro, snmp_rw in self.db.execute(
            """
                SELECT auth_profile_id, snmp_ro, snmp_rw
                FROM sa_authprofilesuggestsnmp WHERE snmp_ro <> ''
                """
        ):
            if ap_id not in credentials:
                continue
            credentials[ap_id]["suggest_snmp"] += [{"snmp_ro": snmp_ro, "snmp_rw": snmp_rw}]
        # CLI
        for ap_id, user, password, super_password in self.db.execute(
            """
                SELECT auth_profile_id, user, password, super_password
                FROM sa_authprofilesuggestcli
                """
        ):
            if ap_id not in credentials:
                continue
            credentials[ap_id]["suggest_credential"] += [{"user": user, "password": password}]
            if super_password:
                credentials[ap_id]["suggest_credential"][-1]["super_password"] = super_password
        bulk = []
        for doc in credentials.values():
            if not doc["suggest_snmp"] and not doc["suggest_credential"]:
                continue
            bulk += [InsertOne(doc)]
        if bulk:
            coll.bulk_write(bulk)
