# ----------------------------------------------------------------------
# Migrate ManagedObject Diagnostics labels
# ----------------------------------------------------------------------
# Copyright (C) 2007-2022 The NOC Project
# See LICENSE for details
# ----------------------------------------------------------------------

# Python modules
from itertools import product

# Third-party modules
from pymongo import InsertOne, UpdateOne

# NOC modules
from noc.core.migration.base import BaseMigration
from noc.core.diagnostic.types import DiagnosticState
from noc.core.diagnostic.hub import (
    PROFILE_DIAG,
    SNMP_DIAG,
    CLI_DIAG,
    SNMPTRAP_DIAG,
    SYSLOG_DIAG,
    HTTP_DIAG,
    DIAGNOCSTIC_LABEL_SCOPE,
)

DIAGNOSTICS = ["Access", PROFILE_DIAG, SNMP_DIAG, CLI_DIAG, SNMPTRAP_DIAG, SYSLOG_DIAG, HTTP_DIAG]


class Migration(BaseMigration):
    depends_on = [("sa", "0233_managedobject_diagnostics")]

    def migrate(self):
        labels, remove_labels = [], []
        states = [s.value for s in DiagnosticState]
        # Reset unknown state
        # Cleanup diagnostics label
        for d, s in product(DIAGNOSTICS, states):
            remove_labels += [f"funcs::{d}::{s}"]
            labels += [f"{DIAGNOCSTIC_LABEL_SCOPE}::{d}::{s}"]
        self.db.execute(
            """
                UPDATE sa_managedobject
                SET effective_labels = ARRAY (SELECT unnest(effective_labels) EXCEPT SELECT unnest(%s::varchar[]))
                WHERE diagnostics != '{}'::jsonb
            """,
            [remove_labels],
        )
        # Update Diagnostic labels
        for d, s in product(DIAGNOSTICS, states):
            if s == "unknown":
                continue
            self.db.execute(
                """
                    UPDATE sa_managedobject
                    SET effective_labels = ARRAY (SELECT DISTINCT e FROM unnest(effective_labels || %s::varchar[]) AS a(e))
                    WHERE diagnostics -> %s -> 'state' ? %s
                """,
                [[f"{DIAGNOCSTIC_LABEL_SCOPE}::{d}::{s}"], d, s],
            )
        # Update labels
        self.sync_labels(labels)
        # Rest SNMP and SYSLOG Diagnostics
        self.db.execute(
            """
                 UPDATE sa_managedobject
                 SET diagnostics = diagnostics  #- %s  #- %s
                 """,
            ["{%s}" % SNMPTRAP_DIAG, "{%s}" % SYSLOG_DIAG],
        )

    def sync_labels(self, labels):
        # Create labels
        bulk = []
        l_coll = self.mongo_db["labels"]
        current_labels = {ll["name"]: ll["_id"] for ll in l_coll.find()}
        # Scope labels
        if f"{DIAGNOCSTIC_LABEL_SCOPE}::*" not in current_labels:
            bulk += [
                InsertOne(
                    {
                        "name": f"{DIAGNOCSTIC_LABEL_SCOPE}::*",
                        "description": "",
                        "bg_color1": 8359053,
                        "fg_color1": 16777215,
                        "bg_color2": 8359053,
                        "fg_color2": 16777215,
                        "is_protected": True,
                        "propagate": True,
                        # Label scope
                        "enable_agent": False,
                        "enable_service": False,
                        "enable_serviceprofile": False,
                        "enable_managedobject": True,
                        "enable_managedobjectprofile": False,
                        "enable_administrativedomain": False,
                        "enable_authprofile": False,
                        "enable_commandsnippet": False,
                        # Exposition scope
                        "expose_metric": False,
                        "expose_datastream": False,
                    }
                )
            ]
        for label in labels:
            if label in current_labels:
                bulk += [
                    UpdateOne(
                        {"_id": current_labels[label]},
                        {
                            "$set": {
                                "bg_color1": 8359053,
                                "fg_color1": 16777215,
                                "bg_color2": 8359053,
                                "fg_color2": 16777215,
                                "is_protected": True,
                                "enable_managedobject": True,
                            }
                        },
                    )
                ]
            else:
                doc = {
                    # "_id": bson.ObjectId(),
                    "name": label,
                    "description": "",
                    "bg_color1": 8359053,
                    "fg_color1": 16777215,
                    "bg_color2": 8359053,
                    "fg_color2": 16777215,
                    "is_protected": True,
                    # Label scope
                    "enable_agent": False,
                    "enable_service": False,
                    "enable_serviceprofile": False,
                    "enable_managedobject": True,
                    "enable_managedobjectprofile": False,
                    "enable_administrativedomain": False,
                    "enable_authprofile": False,
                    "enable_commandsnippet": False,
                    # Exposition scope
                    "expose_metric": False,
                    "expose_datastream": False,
                }
                bulk += [InsertOne(doc)]
        if bulk:
            l_coll.bulk_write(bulk, ordered=True)
