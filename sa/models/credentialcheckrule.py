# ---------------------------------------------------------------------
# CredentialCheckRule
# ---------------------------------------------------------------------
# Copyright (C) 2007-2024 The NOC Project
# See LICENSE for details
# ---------------------------------------------------------------------

# Python modules
import operator
from threading import Lock
from typing import List, Set, Union, FrozenSet
from dataclasses import dataclass

# Third-party modules
import cachetools
from mongoengine.document import Document, EmbeddedDocument
from mongoengine.fields import (
    StringField,
    IntField,
    EmbeddedDocumentListField,
    ListField,
    BooleanField,
)
from mongoengine.errors import ValidationError
from pymongo import ReadPreference

# NOC modules
from noc.core.mongo.fields import ForeignKeyField
from noc.core.script.scheme import Protocol, SNMPCredential, CLICredential
from noc.core.validators import is_oid
from noc.main.models.label import Label
from noc.sa.models.authprofile import AuthProfile

rules_lock = Lock()


def check_model(oid):
    if not is_oid(oid):
        raise ValidationError(f"Bad SNMP OID value: {oid}")


@dataclass(frozen=True)
class SuggestItem(object):
    credentials: List[Union[SNMPCredential, CLICredential]]
    labels: List[FrozenSet[str]]
    protocols: Set[Protocol]

    def is_match(self, labels: Set[str]) -> bool:
        if not self.labels:
            return True
        if any(not set(ll) - labels for ll in self.labels):
            return True
        return False


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
    match: List["Match"] = EmbeddedDocumentListField(Match)
    description = StringField()
    # Rule preference, processed from lesser to greater
    preference = IntField(required=True, default=100)
    suggest_snmp: List["SuggestSNMP"] = EmbeddedDocumentListField(SuggestSNMP)
    suggest_credential: List["SuggestCLI"] = EmbeddedDocumentListField(SuggestCLI)
    suggest_auth_profile: List["SuggestAuthProfile"] = EmbeddedDocumentListField(SuggestAuthProfile)
    # TELNET/SSH/SNMP/HTTP
    suggest_protocols = ListField(
        StringField(choices=[p.name for p in Protocol if p.config.enable_suggest])
    )
    # SNMP OID's for check
    suggest_snmp_oids: List[str] = ListField(StringField(validation=check_model))

    _rules_cache = cachetools.TTLCache(10, ttl=300)

    check_proto_map = {p.config.check: p for p in Protocol if p.config.enable_suggest}

    def __str__(self):
        return self.name

    def get_suggest_proto(self) -> List[Protocol]:
        return [Protocol[sp] for sp in self.suggest_protocols]

    def get_suggest_snmp(self) -> List[SNMPCredential]:
        r = []
        for ss in self.suggest_snmp:
            r.append(
                SNMPCredential(
                    snmp_ro=ss.snmp_ro, snmp_rw=ss.snmp_rw, oids=list(self.suggest_snmp_oids)
                )
            )
        for au in self.suggest_auth_profile:
            if not au.auth_profile.snmp_ro:
                r.append(
                    SNMPCredential(snmp_ro=au.auth_profile.snmp_ro, snmp_rw=au.auth_profile.snmp_rw)
                )
        return r

    def get_suggest_cli(self) -> List[CLICredential]:
        r = []
        for ss in self.suggest_credential:
            r.append(
                CLICredential(
                    username=ss.user, password=ss.password, super_password=ss.super_password
                )
            )
        for au in self.suggest_auth_profile:
            if not au.auth_profile.snmp_ro:
                r.append(
                    CLICredential(
                        username=au.auth_profile.user,
                        password=au.auth_profile.password,
                        super_password=au.auth_profile.super_password,
                    )
                )
        return r

    @classmethod
    @cachetools.cachedmethod(operator.attrgetter("_rules_cache"), lock=lambda _: rules_lock)
    def get_suggest_rules(cls) -> List["SuggestItem"]:
        r = []
        for rule in (
            CredentialCheckRule.objects.filter(is_active=True)
            .read_preference(ReadPreference.SECONDARY_PREFERRED)
            .order_by("preference")
        ):
            sr = rule.get_suggest_snmp()
            labels = [frozenset(ll.labels) for ll in rule.match]
            if sr:
                r.append(
                    SuggestItem(
                        sr,
                        labels,
                        {Protocol(6), Protocol(7)},
                    )
                )
            sr = rule.get_suggest_cli()
            if sr:
                r.append(
                    SuggestItem(
                        sr,
                        labels,
                        {Protocol(1), Protocol(1)},
                    )
                )
        return r

    @classmethod
    def get_suggests(cls, protocol: Protocol, labels: Set[str]) -> List[Union[SNMPCredential, CLICredential]]:
        r = []
        if not protocol.config.enable_suggest:
            return r
        for s in cls.get_suggest_rules():
            if protocol not in s.protocols or not s.is_match(labels):
                continue
            r += s.credentials
        return r

    # def clean(self):
    #     super().clean()
    #     # if "snmp" in self.method and self.param.startswith("."):
    #         raise ValidationError("SNMP Param must not be started with dot")
