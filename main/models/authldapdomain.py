# -*- coding: utf-8 -*-
##----------------------------------------------------------------------
## AuthLDAPDomain model
##----------------------------------------------------------------------
## Copyright (C) 2007-2016 The NOC Project
## See LICENSE for details
##----------------------------------------------------------------------

## Python modules
from threading import Lock
import operator
## Third-party modules
from mongoengine.document import Document, EmbeddedDocument
from mongoengine.fields import StringField, BooleanField, IntField, ListField, EmbeddedDocumentField
from django.contrib.auth.models import Group
import cachetools
## NOC modules
from noc.lib.nosql import ForeignKeyField

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


class AuthLDAPDomain(Document):
    meta = {
        "collection": "noc.authldapdomain"
    }

    name = StringField(unique=True)
    is_active = BooleanField()
    description = StringField()
    type = StringField(
        choices=[
            ("ldap", "LDAP"),
            ("ad", "Active Directory")
        ]
    )
    # Bind root
    root = StringField()
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
    # Do not authenticate user if the member of group, provided by DN
    # Ignore if empty
    deny_group = StringField()
    # Group mappings
    groups = ListField(EmbeddedDocumentField(AuthLDAPGroup))

    DEFAULT_USER_SEARCH_FILTER = {
        "ldap": "(uid=%(user)s)",
        "ad": "(samAccountName=%(user)s)"
    }

    DEFAULT_GROUP_SEARCH_FILTER = {
        "ldap": "(&((objectClass=groupOfNames))(member=%(user_dn)s))",
        "ad": "(&(objectClass=group)(member=%(user_dn)s))"
    }

    DEFAULT_DOMAIN = "default"

    _id_cache = cachetools.TTLCache(maxsize=100, ttl=60)
    _name_cache = cachetools.TTLCache(maxsize=100, ttl=60)

    def __unicode__(self):
        return self.name

    @classmethod
    @cachetools.cachedmethod(operator.attrgetter("_id_cache"), lock=lambda _: id_lock)
    def get_by_id(cls, id):
        return AuthLDAPDomain.objects.filter(id=id).first()

    @classmethod
    @cachetools.cachedmethod(operator.attrgetter("_id_cache"), lock=lambda _: id_lock)
    def get_by_name(cls, name):
        return AuthLDAPDomain.objects.filter(name=name).first()

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
