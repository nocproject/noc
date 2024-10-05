# ---------------------------------------------------------------------
# AuthLDAPDomain model
# ---------------------------------------------------------------------
# Copyright (C) 2007-2020 The NOC Project
# See LICENSE for details
# ---------------------------------------------------------------------

# Python modules
import operator
from threading import Lock
from typing import Optional, Union

# Third-party modules
import cachetools
from bson import ObjectId
from mongoengine.document import Document, EmbeddedDocument
from mongoengine.fields import StringField, BooleanField, IntField, ListField, EmbeddedDocumentField

# NOC modules
from noc.aaa.models.group import Group
from noc.core.mongo.fields import ForeignKeyField
from noc.core.model.decorator import on_save

id_lock = Lock()


class AuthLDAPServer(EmbeddedDocument):
    name = StringField()
    is_active = BooleanField()
    address = StringField()
    port = IntField()
    use_tls = BooleanField()
    connect_timeout = IntField(default=5, min_value=0)

    def __str__(self):
        return self.name or self.address


class AuthLDAPGroup(EmbeddedDocument):
    # LDAP group dn
    group_dn = StringField()
    is_active = BooleanField()
    group = ForeignKeyField(Group)


@on_save
class AuthLDAPDomain(Document):
    meta = {"collection": "noc.authldapdomain", "strict": False, "auto_create_index": False}

    name = StringField(unique=True)
    is_active = BooleanField()
    is_default = BooleanField()
    description = StringField()
    type = StringField(choices=[("ldap", "LDAP"), ("ad", "Active Directory")])
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
        choices=[("0", "As-is"), ("l", "Lowercase"), ("u", "Uppercase")], default="l"
    )
    # The pool can have different HA strategies:
    # FIRST: gets the first server in the pool, if ‘active’ is set to True gets the first available server
    # ROUND_ROBIN: each time the connection is open the subsequent server in the pool is used.
    # If active is set to True unavailable servers will be discarded
    # RANDOM: each time the connection is open a random server
    # is chosen in the pool. If active is set to True unavailable servers will be discarded
    ha_policy = StringField(
        choices=[("f", "First"), ("rr", "Round Robin"), ("r", "Random")], default="rr"
    )
    # if you set active=True while defining the ServerPool the strategy will check for server availability,
    # you can also set this attribute to the maximum number of cycles to try before
    # giving up with an LDAPServerPoolExhaustedError exception.
    pool_active = IntField(default=1)
    # With exhaust=True if a server is not active it will be removed by the pool,
    # if you set it to a number this will be the number of seconds an unreachable server is considered offline.
    # When this timout expires the server is reinserted in the pool and checked again for availability. The
    pool_exhaust = IntField()
    # Synchronize first_name/last_name with LDAP
    sync_name = BooleanField(default=False)
    # Synchronize email with LDAP
    sync_mail = BooleanField(default=False)

    DEFAULT_USER_SEARCH_FILTER = {
        "ldap": "(&(objectClass=posixAccount)(uid=%(user)s))",
        "ad": "(samAccountName=%(user)s)",
    }

    DEFAULT_GROUP_SEARCH_FILTER = {
        "ldap": "(&(objectClass=posixGroup)(memberUid=%(user)s))",
        "ad": "(&(objectClass=group)(member=%(user_dn)s))",
    }

    DEFAULT_ATTR_MAPPING = {
        "ad": {"givenName": "first_name", "sn": "last_name", "mail": "email"},
        "ldap": {"givenName": "first_name", "sn": "last_name", "mail": "email"},
    }

    _id_cache = cachetools.TTLCache(maxsize=100, ttl=60)
    _name_cache = cachetools.TTLCache(maxsize=100, ttl=60)
    _default_cache = cachetools.TTLCache(maxsize=100, ttl=60)

    def __str__(self):
        return self.name

    @classmethod
    @cachetools.cachedmethod(operator.attrgetter("_id_cache"), lock=lambda _: id_lock)
    def get_by_id(cls, oid: Union[str, ObjectId]) -> Optional["AuthLDAPDomain"]:
        return AuthLDAPDomain.objects.filter(id=oid).first()

    @classmethod
    @cachetools.cachedmethod(operator.attrgetter("_name_cache"), lock=lambda _: id_lock)
    def get_by_name(cls, name: str) -> Optional["AuthLDAPDomain"]:
        return AuthLDAPDomain.objects.filter(name=name).first()

    @classmethod
    @cachetools.cachedmethod(operator.attrgetter("_default_cache"), lock=lambda _: id_lock)
    def get_default_domain(cls) -> Optional["AuthLDAPDomain"]:
        return AuthLDAPDomain.objects.filter(is_default=True).first()

    def on_save(self):
        if self.is_default and (
            not hasattr(self, "_changed_fields") or "is_default" in self._changed_fields
        ):
            # Only one default domain permitted
            AuthLDAPDomain._get_collection().update_many(
                {"is_default": True, "_id": {"$ne": self.id}}, {"$set": {"is_default": False}}
            )

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
        return ["distinguishedName"] + list(self.DEFAULT_ATTR_MAPPING[self.type])

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

    def get_pool_active(self):
        if self.pool_active:
            return self.pool_active
        return True

    def get_pool_exhaust(self):
        if self.pool_exhaust:
            return self.pool_exhaust
        return True
