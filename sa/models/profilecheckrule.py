# ---------------------------------------------------------------------
# ProfileCheckRule
# ---------------------------------------------------------------------
# Copyright (C) 2007-2024 The NOC Project
# See LICENSE for details
# ---------------------------------------------------------------------

# Python modules
import os
import operator
from threading import Lock
from typing import Any, Dict

# Third-party modules
import cachetools
from pymongo import ReadPreference
from mongoengine.document import Document
from mongoengine.fields import StringField, UUIDField, ObjectIdField, IntField
from mongoengine.errors import ValidationError

# NOC modules
from noc.core.mongo.fields import PlainReferenceField
from noc.sa.models.profile import Profile
from noc.main.models.doccategory import category
from noc.core.prettyjson import to_json
from noc.core.text import quote_safe_path
from noc.core.checkers.profile import SuggestProfile

rules_lock = Lock()


@category
class ProfileCheckRule(Document):
    meta = {
        "collection": "noc.profilecheckrules",
        "strict": False,
        "auto_create_index": False,
        "json_collection": "sa.profilecheckrules",
        "json_depends_on": ["sa.profile"],
        "json_unique_fields": ["uuid", "name"],
    }

    name = StringField(required=True, unique=True)
    uuid = UUIDField(required=True, unique=True)
    description = StringField()
    # Rule preference, processed from lesser to greater
    preference = IntField(required=True, default=1000)
    # Check method
    method = StringField(
        required=True, choices=["snmp_v2c_get", "http_get", "https_get"], default="snmp_v2c_get"
    )
    # Method input parameters, defined by method
    param = StringField()
    #
    match_method = StringField(
        required=True,
        choices=["eq", "contains", "re"],  # Full match  # Contains  # regular expression
        default="eq",
    )
    #
    value = StringField(required=True)
    #
    action = StringField(required=True, choices=["match", "maybe"], default="match")
    # Resulting profile name
    profile = PlainReferenceField(Profile, required=True)
    #
    category = ObjectIdField()

    _rules_cache = cachetools.TTLCache(10, ttl=60)

    def __str__(self):
        return self.name

    def clean(self):
        super().clean()
        if "snmp" in self.method and self.param.startswith("."):
            raise ValidationError("SNMP Param must not be started with dot")

    @property
    def json_data(self) -> Dict[str, Any]:
        return {
            "name": self.name,
            "$collection": self._meta["json_collection"],
            "uuid": self.uuid,
            "description": self.description,
            "preference": self.preference,
            "method": self.method,
            "param": self.param,
            "match_method": self.match_method,
            "value": self.value,
            "action": self.action,
            "profile__name": self.profile.name,
        }

    def to_json(self) -> str:
        return to_json(
            self.json_data,
            order=[
                "name",
                "$collection",
                "uuid",
                "description",
                "preference",
                "method",
                "param",
                "match_method",
                "value",
                "action",
                "profile__name",
            ],
        )

    def get_json_path(self) -> str:
        p = [quote_safe_path(n.strip()) for n in self.name.split("|")]
        return os.path.join(*p) + ".json"

    @classmethod
    @cachetools.cachedmethod(operator.attrgetter("_rules_cache"), lock=lambda _: rules_lock)
    def get_profile_check_rules(cls):
        r = []
        for rule in (
            ProfileCheckRule.objects.all()
            .read_preference(ReadPreference.SECONDARY_PREFERRED)
            .order_by("preference")
        ):
            r.append(
                SuggestProfile(
                    method=rule.method,
                    param=rule.param,
                    match=rule.match_method,
                    value=rule.value,
                    profile=rule.profile.name,
                    preference=rule.preference,
                    name=rule.name,
                )
            )
        return r
