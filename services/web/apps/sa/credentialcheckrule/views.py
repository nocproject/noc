# ---------------------------------------------------------------------
# sa.credentialcheckrule application
# ---------------------------------------------------------------------
# Copyright (C) 2007-2023 The NOC Project
# See LICENSE for details
# ---------------------------------------------------------------------

# Python modules
from typing import Tuple, List

# NOC modules
from noc.services.web.base.extdocapplication import ExtDocApplication
from noc.sa.models.credentialcheckrule import CredentialCheckRule
from noc.main.models.label import MATCH_OPS, MATCH_BADGES
from noc.core.translation import ugettext as _


def clean_label(label: str) -> Tuple[str, str, List[str]]:
    r = label.split("::")
    badges = []
    if len(r) == 1:
        return "", label, badges
    if r[0] == "noc":
        r.pop(0)
    if r[-1] in MATCH_OPS:
        badges += [MATCH_BADGES[r[-1]]]
        r.pop(-1)
    return "::".join(r[:-1]), r[-1], badges


class CredentialCheckRuleApplication(ExtDocApplication):
    """
    CredentialCheckRule application
    """

    title = _("Credential Check Rule")
    menu = [_("Setup"), _("Credential Check Rules")]
    model = CredentialCheckRule
    query_fields = ["name__icontains", "description__icontains"]
    default_ordering = ["preference", "_id"]

    @staticmethod
    def field_match_expression(o: "CredentialCheckRule"):
        r = []
        for num, ml in enumerate(o.match):
            if num:
                r += [
                    {
                        "id": "&&",
                        "is_protected": False,
                        "scope": "",
                        "name": "&&",
                        # "name": ll.name,
                        "value": "&&",
                        "badges": [],
                        "bg_color1": 0,
                        "fg_color1": 16777215,
                        "bg_color2": 0,
                        "fg_color2": 16777215,
                    }
                ]
            for ll in ml.get_labels():
                scope, value, badges = clean_label(ll.name)
                r += [
                    {
                        "id": ll.name,
                        "is_protected": ll.is_protected,
                        "scope": scope,
                        "name": f" {scope}::{value}" if scope else value,
                        "value": value,
                        "badges": ll.badges + badges,
                        # "bg_color1": f"#{ll.bg_color1:06x}",
                        # "fg_color1": f"#{ll.fg_color1:06x}",
                        # "bg_color2": f"#{ll.bg_color2:06x}",
                        # "fg_color2": f"#{ll.fg_color2:06x}",
                        "bg_color1": ll.bg_color1,
                        "fg_color1": ll.fg_color1,
                        "bg_color2": ll.bg_color2,
                        "fg_color2": ll.fg_color2,
                    }
                ]

        return r

    @staticmethod
    def get_affected_rules(el: List[str]):
        return [
            ccr["_id"]
            for ccr in CredentialCheckRule._get_collection().aggregate(
                [
                    {"$unwind": {"path": "$match", "preserveNullAndEmptyArrays": True}},
                    {
                        "$match": {
                            "$or": [
                                {"match.labels": {"$exists": False}},
                                {"$expr": {"$setIsSubset": ["$match.labels", el]}},
                            ]
                        }
                    },
                    {"$project": {"_id": 1}},
                ]
            )
        ]

    def cleaned_query(self, q):
        from noc.sa.models.managedobject import ManagedObject

        mo = q.pop("managed_object", None)
        q = super().cleaned_query(q)
        if not mo:
            return q
        mo = ManagedObject.objects.filter(id=int(mo)).values("effective_labels").first()
        if not mo:
            return
        q["id__in"] = self.get_affected_rules(mo["effective_labels"])
        return q

    def instance_to_dict(self, o, fields=None, nocustom=False):
        r = super().instance_to_dict(o, fields=fields, nocustom=nocustom)
        r["suggest_protocols"] = [
            {"protocol": p, "protocol__label": p} for p in r.get("suggest_protocols", [])
        ]
        r["suggest_snmp_oids"] = [
            {"oid": p, "oid__label": p} for p in r.get("suggest_snmp_oids", [])
        ]
        return r

    def clean(self, data):
        suggest_snmp_oids, suggest_protocols = [], []
        for f in data.get("suggest_snmp_oids", []):
            suggest_snmp_oids += [f["oid"]]
        for f in data.get("suggest_protocols", []):
            suggest_protocols += [f["protocol"]]
        data["suggest_snmp_oids"] = suggest_snmp_oids
        data["suggest_protocols"] = suggest_protocols
        return super().clean(data)
