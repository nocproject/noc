# ---------------------------------------------------------------------
# CredentialCheckRule
# ---------------------------------------------------------------------
# Copyright (C) 2007-2024 The NOC Project
# See LICENSE for details
# ---------------------------------------------------------------------

# Python modules
import operator
from collections import defaultdict
from dataclasses import dataclass
from threading import Lock
from typing import List, Set, Union, FrozenSet, Tuple, Dict, Any, Optional, Iterable, Callable

# Third-party modules
import cachetools
import bson
from mongoengine.document import Document, EmbeddedDocument
from mongoengine.fields import (
    StringField,
    IntField,
    EmbeddedDocumentListField,
    ListField,
    BooleanField,
    ObjectIdField,
)
from mongoengine.errors import ValidationError
from pymongo import ReadPreference
from django.db.models.query_utils import Q as d_Q

# NOC modules
from noc.core.mongo.fields import ForeignKeyField
from noc.core.script.scheme import Protocol, SNMPCredential, CLICredential, CLI_PROTOCOLS
from noc.core.validators import is_oid
from noc.core.matcher import build_matcher
from noc.core.change.decorator import change
from noc.main.models.label import Label
from noc.sa.models.authprofile import AuthProfile

id_lock = Lock()
rules_lock = Lock()


def check_model(oid):
    if not is_oid(oid):
        raise ValidationError(f"Bad SNMP OID value: {oid}")


@dataclass(frozen=True)
class SuggestItem(object):
    """
    Attributes:
        credentials: List of suggests credentials
        labels: Match labels for rule
        protocols: List of allowed protocols
    """

    credentials: List[Union[SNMPCredential, CLICredential]]
    labels: List[FrozenSet[str]]
    protocols: Tuple[Protocol, ...]

    def is_match(self, labels: Set[str]) -> bool:
        if not self.labels:
            return True
        return bool(any(not set(ll) - labels for ll in self.labels))


class Match(EmbeddedDocument):
    labels = ListField(StringField())
    exclude_labels = ListField(StringField())
    groups = ListField(ObjectIdField(required=True))
    exclude_groups = ListField(ObjectIdField(required=True))

    def __str__(self):
        return ", ".join(self.labels)

    def get_labels(self):
        return list(Label.objects.filter(name__in=self.labels))

    def get_match_expr(self) -> Dict[str, Any]:
        r = {}
        if self.labels:
            r["labels"] = {"$all": list(self.labels)}
        elif self.exclude_labels:
            r["labels"] = {"$all_ne": list(self.exclude_labels)}
        if self.groups:
            r["service_groups"] = {"$all": [str(x) for x in self.resource_groups]}
        if self.exclude_groups:
            r["service_groups"] = {"$all_ne": [str(x) for x in self.resource_groups]}
        return r

    def get_q(self):
        """Return instance queryset"""
        q = d_Q()
        if self.labels:
            q &= d_Q(effective_labels__contains=self.labels)
        # if self.exclude_labels:
        #
        if self.resource_groups:
            q &= d_Q(effective_service_groups__contains=[str(x) for x in self.resource_groups])
        return q


class SuggestSNMP(EmbeddedDocument):
    snmp_ro = StringField(blank=True, null=True, max_length=64)
    snmp_rw = StringField(blank=True, null=True, max_length=64)


class SuggestCLI(EmbeddedDocument):
    user = StringField(max_length=32, blank=True, null=True)
    password = StringField(max_length=32, blank=True, null=True)
    super_password = StringField(max_length=32, blank=True, null=True)


class SuggestAuthProfile(EmbeddedDocument):
    auth_profile: "AuthProfile" = ForeignKeyField(AuthProfile)


@change
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

    _id_cache = cachetools.TTLCache(maxsize=100, ttl=300)
    _rules_cache = cachetools.TTLCache(10, ttl=300)
    _credential_rules_matcher = cachetools.TTLCache(maxsize=100, ttl=300)
    _credential_rules = cachetools.TTLCache(maxsize=10, ttl=300)

    def __str__(self):
        return self.name

    @classmethod
    @cachetools.cachedmethod(operator.attrgetter("_id_cache"), lock=lambda _: id_lock)
    def get_by_id(cls, oid: Union[str, bson.ObjectId]) -> Optional["CredentialCheckRule"]:
        return CredentialCheckRule.objects.filter(id=oid).first()

    def get_suggest_proto(self) -> List[Protocol]:
        return [Protocol[sp] for sp in self.suggest_protocols]

    def get_suggest_snmp(self) -> List[SNMPCredential]:
        r = []
        for ss in self.suggest_snmp:
            r.append(
                SNMPCredential(
                    snmp_ro=ss.snmp_ro,
                    snmp_rw=ss.snmp_rw,
                    oids=list(self.suggest_snmp_oids) or None,
                )
            )
        for au in self.suggest_auth_profile:
            if au.auth_profile.snmp_ro and au.auth_profile.enable_suggest:
                r.append(
                    SNMPCredential(snmp_ro=au.auth_profile.snmp_ro, snmp_rw=au.auth_profile.snmp_rw)
                )
        return r

    def get_suggest_cli(self, raise_privilege: bool = True) -> List[CLICredential]:
        r = []
        sp = tuple(p.value for p in self.get_suggest_proto() if p.config.is_cli)
        proto = sp or (1, 2)
        for ss in self.suggest_credential:
            r.append(
                CLICredential(
                    username=ss.user,
                    password=ss.password,
                    super_password=ss.super_password,
                    enable_protocols=proto,
                )
            )
        for au in self.suggest_auth_profile:
            if au.auth_profile.user and au.auth_profile.enable_suggest:
                r.append(
                    CLICredential(
                        username=au.auth_profile.user,
                        password=au.auth_profile.password,
                        super_password=au.auth_profile.super_password,
                        raise_privilege=raise_privilege,
                        enable_protocols=proto,
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
            sr: List[SNMPCredential] = rule.get_suggest_snmp()
            labels = [frozenset(ll.labels) for ll in rule.match]
            protos: List[Protocol] = rule.get_suggest_proto()
            if sr:
                r.append(
                    SuggestItem(
                        sr,
                        labels,
                        tuple(
                            p
                            for p in Protocol
                            if p.config.snmp_version and (not protos or p in protos)
                        ),
                    )
                )
            sr: List[CLICredential] = rule.get_suggest_cli()
            if sr:
                c_protos = protos or CLI_PROTOCOLS
                r.append(
                    SuggestItem(
                        sr,
                        labels,
                        tuple(Protocol(p) for p in c_protos if not protos or p in protos),
                    )
                )
        return r

    @classmethod
    def get_suggests(
        cls, o
    ) -> List[Tuple[Tuple[Protocol, ...], Union[SNMPCredential, CLICredential]]]:
        r = []
        for s in cls.get_suggests_by(o.effective_labels, o.effective_service_groups):
            for c in s.credentials:
                if isinstance(c, CLICredential) and c.raise_privilege != o.to_raise_privileges:
                    c = CLICredential(
                        username=c.username,
                        password=c.password,
                        super_password=c.super_password,
                        raise_privilege=o.to_raise_privileges,
                    )
                r.append((s.protocols, c))
        return r

    @cachetools.cachedmethod(
        operator.attrgetter("_credential_rules_matcher"),
        lock=lambda _: rules_lock,
        key=operator.attrgetter("id"),
    )
    def get_matcher(self) -> Callable:
        """"""
        expr = []
        for mr in self.match:
            expr.append(mr.get_match_expr())
        if len(expr) == 1:
            return build_matcher(expr[0])
        return build_matcher({"$or": expr})

    def is_match(self, o) -> bool:
        """Local Match rules"""
        matcher = self.get_matcher()
        ctx = o.get_matcher_ctx()
        return matcher(ctx)

    @classmethod
    @cachetools.cachedmethod(
        operator.attrgetter("_credential_rules"),
        key=lambda x: "ruleset",
        lock=lambda _: rules_lock,
    )
    def get_profiles_matcher(cls) -> Tuple[Tuple[str, Tuple[Callable, ...]], ...]:
        """Build matcher based on Profile Match Rules"""
        r = defaultdict(list)
        for rule_id, pref, rules in CredentialCheckRule.objects.filter(is_active=True).values_list(
            "id", "preference", "match"
        ):
            for mr in rules:
                r[(str(rule_id), pref)].append(build_matcher(mr.get_match_expr()))
        return tuple((x[0], tuple(r[x])) for x in sorted(r, key=lambda i: i[1]))

    @classmethod
    def iter_suggests_rules(
        cls, labels: List[str], groups: List[str]
    ) -> Iterable["CredentialCheckRule"]:
        """"""
        ctx = {"labels": labels, "groups": groups}
        for rule_id, matches in cls.get_profiles_matcher():
            for match in matches:
                if match(ctx):
                    rule = CredentialCheckRule.get_by_id(rule_id)
                    if rule:
                        yield rule
                    break

    @classmethod
    def get_suggests_by(cls, labels: List[str], groups: List[str]) -> List["SuggestItem"]:
        r = []
        for rule in cls.iter_suggests_rules(labels, groups):
            snmp: List[SNMPCredential] = rule.get_suggest_snmp()
            protos: List[Protocol] = rule.get_suggest_proto()
            if snmp:
                r.append(
                    SuggestItem(
                        snmp,
                        labels,
                        tuple(
                            p
                            for p in Protocol
                            if p.config.snmp_version and (not protos or p in protos)
                        ),
                    )
                )
            cli: List[CLICredential] = rule.get_suggest_cli()
            if cli:
                c_protos = protos or CLI_PROTOCOLS
                r.append(
                    SuggestItem(
                        cli,
                        labels,
                        tuple(Protocol(p) for p in c_protos if not protos or p in protos),
                    )
                )
        return r

    # def clean(self):
    #     super().clean()
    #     # if "snmp" in self.method and self.param.startswith("."):
    #         raise ValidationError("SNMP Param must not be started with dot")
