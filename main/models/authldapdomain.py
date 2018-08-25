# -*- coding: utf-8 -*-
# ---------------------------------------------------------------------
# AuthLDAPDomain model
# ---------------------------------------------------------------------
# Copyright (C) 2007-2017 The NOC Project
# See LICENSE for details
# ---------------------------------------------------------------------

# Python modules
from threading import Lock
import operator
# Third-party modules
from mongoengine.document import Document, EmbeddedDocument
from mongoengine.fields import StringField, BooleanField, IntField, ListField, EmbeddedDocumentField
from django.contrib.auth.models import Group
import cachetools
# NOC modules
from noc.lib.nosql import ForeignKeyField
from noc.core.model.decorator import on_save

id_lock = Lock()


class AuthLDAPServer(EmbeddedDocument):
    name = StringField()
    is_active = BooleanField()
    address = StringField()
    port = IntField()
    use_tls = BooleanField()

    def __unicode__(self):
        return self.name or self.address


class AuthLDAPGroup(EmbeddedDocument):
    # LDAP group dn
    group_dn = StringField()
    is_active = BooleanField()
    group = ForeignKeyField(Group)


@on_save
class AuthLDAPDomain(Document):
    meta = {
        "collection": "noc.authldapdomain"
    }

    name = StringField(unique=True)
    is_active = BooleanField()
    is_default = BooleanField()
    description = StringField()
    type = StringField(
        choices=[
            ("ldap", "LDAP"),
            ("ad", "Active Directory")
        ]
    )
    # Bind root
    root = StringField()
    # Users search tree
    user_search_dn = StringField()
    # Groups search tree
    group_search_dn = StringField()
    # Search expression to find user
    # Use DEFAULT_USER_SEARCH_FILTER when empty
    user_search_filter = StringField()
    # Search expression to find groups
    # Use DEFAULT_GROUP_SEARCH_FILTER when empty
    group_search_filter = StringField()
    # LDAP servers
    servers = ListField(EmbeddedDocumentField(AuthLDAPServer))
    # user and password to search groups
    # Use user dn and password when empty
    bind_user = StringField()
    bind_password = StringField()
    # Authenticate user only if the member of group, provided by DN
    # Authenticate anyway if empty
    require_group = StringField()
    # Authenticane ony if any mapped group is active
    require_any_group = BooleanField(default=False)
    # Do not authenticate user if the member of group, provided by DN
    # Ignore if empty
    deny_group = StringField()
    # Group mappings
    groups = ListField(EmbeddedDocumentField(AuthLDAPGroup))
    # Convert username
    convert_username = StringField(
        choices=[
            ("0", "As-is"),
            ("l", "Lowercase"),
            ("u", "Uppercase")
        ],
        default="l"
    )
    # Synchronize first_name/last_name with LDAP
    sync_name = BooleanField(default=False)
    # Synchronize email with LDAP
    sync_mail = BooleanField(default=False)

    DEFAULT_USER_SEARCH_FILTER = {
        "ldap": "(&(objectClass=posixAccount)(uid=%(user)s))",
        "ad": "(samAccountName=%(user)s)"
    }

    DEFAULT_GROUP_SEARCH_FILTER = {
        "ldap": "(&(objectClass=posixGroup)(memberUid=%(user)s))",
        "ad": "(&(objectClass=group)(member=%(user_dn)s))"
    }

    DEFAULT_ATTR_MAPPING = {
        "ad": {
            "givenName": "first_name",
            "sn": "last_name",
            "mail": "email"
        },
        "ldap": {
            "givenName": "first_name",
            "sn": "last_name",
            "mail": "email"
        }
    }

    _id_cache = cachetools.TTLCache(maxsize=100, ttl=60)
    _name_cache = cachetools.TTLCache(maxsize=100, ttl=60)
    _default_cache = cachetools.TTLCache(maxsize=100, ttl=60)

    def __unicode__(self):
        return self.name

    @classmethod
    @cachetools.cachedmethod(operator.attrgetter("_id_cache"),
                             lock=lambda _: id_lock)
    def get_by_id(cls, id):
        return AuthLDAPDomain.objects.filter(id=id).first()

    @classmethod
    @cachetools.cachedmethod(operator.attrgetter("_name_cache"),
                             lock=lambda _: id_lock)
    def get_by_name(cls, name):
        return AuthLDAPDomain.objects.filter(name=name).first()

    @classmethod
    @cachetools.cachedmethod(operator.attrgetter("_default_cache"),
                             lock=lambda _: id_lock)
    def get_default_domain(cls):
        return AuthLDAPDomain.objects.filter(is_default=True).first()

    def on_save(self):
        if self.is_default and (
                not hasattr(self, "_changed_fields") or
                "is_default" in self._changed_fields
        ):
            # Only one default domain permitted
            AuthLDAPDomain._get_collection().update_many({
                "is_default": True,
                "_id": {
                    "$ne": self.id
                }
            }, {
                "$set": {
                    "is_default": False
                }
            })

    def get_user_search_filter(self):
        if self.user_search_filter:
            return self.user_search_filter
        else:
            return self.DEFAULT_USER_SEARCH_FILTER[self.type]

    def get_group_search_filter(self):
        if self.group_search_filter:
            return self.group_search_filter
        else:
            return self.DEFAULT_GROUP_SEARCH_FILTER[self.type]

    def clean_username(self, username):
        if self.convert_username == "0":
            return username
        elif self.convert_username == "l":
            return username.lower()
        elif self.convert_username == "u":
            return username.upper()
        else:
            # Preserve existing behavior
            return username.lower()

    def get_attr_mappings(self):
        return self.DEFAULT_ATTR_MAPPING[self.type]

    def get_user_search_attributes(self):
        return ["dn"] + list(self.DEFAULT_ATTR_MAPPING[self.type])

    def get_user_search_dn(self):
        if self.user_search_dn:
            user_search_dn = self.user_search_dn
        else:
            user_search_dn = self.root
        return user_search_dn

    def get_group_search_dn(self):
        if self.group_search_dn:
            group_search_dn = self.group_search_dn
        else:
            group_search_dn = self.root
        return group_search_dn

    def get_group_mappings(self):
        if not hasattr(self, "_group_dn"):
            mappings = {}
            for gm in self.groups:
                if not gm.is_active:
                    continue
                if gm.group in mappings:
                    mappings[gm.group].add(gm.group_dn.lower())
                else:
                    mappings[gm.group] = {gm.group_dn.lower()}
            self._group_dn = mappings
        return self._group_dn
