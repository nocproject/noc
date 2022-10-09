# ---------------------------------------------------------------------
# CredentialCheckRule
# ---------------------------------------------------------------------
# Copyright (C) 2007-2022 The NOC Project
# See LICENSE for details
# ---------------------------------------------------------------------

# Python modules
from typing import List

# Third-party modules
from mongoengine.document import Document, EmbeddedDocument
from mongoengine.fields import (
    StringField,
    IntField,
    EmbeddedDocumentListField,
    ListField,
    BooleanField,
)

# NOC modules
from noc.core.mongo.fields import ForeignKeyField
from noc.core.script.scheme import Protocol
from noc.main.models.label import Label
from noc.sa.models.authprofile import AuthProfile


class Match(EmbeddedDocument):
    labels = ListField(StringField())
    exclude_labels = ListField(StringField())

    def __str__(self):
        return ", ".join(self.labels)

    def get_labels(self):
        return list(Label.objects.filter(name__in=self.labels))


class SuggestSNMP(EmbeddedDocument):
    snmp_ro = StringField(blank=True, null=True, max_length=64)
    snmp_rw = StringField(blank=True, null=True, max_length=64)


class SuggestCLI(EmbeddedDocument):
    user = StringField(max_length=32, blank=True, null=True)
    password = StringField(max_length=32, blank=True, null=True)
    super_password = StringField(max_length=32, blank=True, null=True)


class SuggestAuthProfile(EmbeddedDocument):
    auth_profile: "AuthProfile" = ForeignKeyField(AuthProfile)


class CredentialCheckRule(Document):
    meta = {
        "collection": "noc.credentialcheckrules",
        "strict": False,
        "auto_create_index": False,
    }

    name = StringField(required=True, unique=True)
    is_active = BooleanField(default=True)
    match = EmbeddedDocumentListField(Match)
    description = StringField()
    # Rule preference, processed from lesser to greater
    preference = IntField(required=True, default=100)
    suggest_snmp = EmbeddedDocumentListField(SuggestSNMP)
    suggest_credential = EmbeddedDocumentListField(SuggestCLI)
    suggest_auth_profile = EmbeddedDocumentListField(SuggestAuthProfile)
    # TELNET/SSH/SNMP/HTTP
    suggest_protocols = ListField(
        StringField(choices=[p.name for p in Protocol if p.config.enable_suggest])
    )
    # SNMP OID's for check
    suggest_snmp_oids = ListField(StringField())

    def __str__(self):
        return self.name

    def get_suggest_proto(self) -> List[Protocol]:
        return [Protocol[sp] for sp in self.suggest_protocols]

    # def clean(self):
    #     super().clean()
    #     # if "snmp" in self.method and self.param.startswith("."):
    #         raise ValidationError("SNMP Param must not be started with dot")
