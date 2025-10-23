# ----------------------------------------------------------------------
# APIKey model
# ----------------------------------------------------------------------
# Copyright (C) 2007-2025 The NOC Project
# See LICENSE for details
# ----------------------------------------------------------------------

# Python modules
import datetime
import operator
from threading import Lock
from typing import Optional, Union

# Third-party modules
import bson
import cachetools
from mongoengine.document import Document, EmbeddedDocument
from mongoengine.fields import (
    StringField,
    BooleanField,
    DateTimeField,
    ListField,
    EmbeddedDocumentField,
)

# NOC modules
from noc.core.acl import match
from noc.core.model.decorator import on_delete_check

id_lock = Lock()


class APIAccess(EmbeddedDocument):
    # Api name
    api = StringField()
    # Additional API role, * for wildcard
    role = StringField()

    def __str__(self):
        return "%s:%s" % (self.api, self.role)


class APIAccessACL(EmbeddedDocument):
    prefix = StringField()
    is_active = BooleanField(default=True)
    description = StringField()

    def __str__(self):
        if self.is_active:
            return self.prefix
        return "%s (inactive)" % self.prefix


@on_delete_check(check=[("main.RemoteSystem", "api_key")])
class APIKey(Document):
    meta = {"collection": "apikeys", "strict": False, "auto_create_index": False}

    name = StringField(unique=True)
    is_active = BooleanField()
    description = StringField()
    expires = DateTimeField()
    # Secret API key
    key = StringField(unique=True)
    # Access settings
    access = ListField(EmbeddedDocumentField(APIAccess))
    # Address restrictions
    acl = ListField(EmbeddedDocumentField(APIAccessACL))

    _api_key_cache = cachetools.TTLCache(maxsize=20, ttl=60)

    def __str__(self):
        return self.name

    @classmethod
    def get_by_id(cls, oid: Union[str, bson.ObjectId]) -> Optional["APIKey"]:
        return APIKey.objects.filter(id=oid).first()

    @classmethod
    @cachetools.cachedmethod(operator.attrgetter("_api_key_cache"), lock=lambda _: id_lock)
    def get_by_api_key(cls, api_key: str) -> Optional["APIKey"]:
        return APIKey.objects.filter(key=api_key).first()

    @classmethod
    def get_name_and_access(cls, key, ip=None):
        """
        Return access settings for key and key name
        :param key: API key
        :param ip: IP address to check against ACL
        :return: (Name, [(api, role), ...]. Name is None for denied permissions
        """
        # Find key
        doc = cls._get_collection().find_one({"key": key})
        if not doc:
            # Key not found
            return None, []
        # Check key activity
        if not doc.get("is_active", False):
            # Inactive key
            return None, []
        # Check key expiration
        expires = doc.get("expires", None)
        if expires and expires < datetime.datetime.now():
            # Expired
            return None, []
        # Check ACL
        if ip:
            acl = doc.get("acl")
            if acl and not match((a["prefix"] for a in acl if a.get("is_active")), ip):
                # Forbidden
                return None, []
        # Process key access
        access = doc.get("access", [])
        r = []
        for a in access:
            r += [(a.get("api"), a.get("role", "*"))]
        return doc["name"], r

    @classmethod
    def get_access(cls, key, ip=None):
        """
        Return access settings for key
        :param key: API key
        :param ip: IP address to check against ACL
        :return: List of (api, role). Empty list for denied permissions
        """
        return cls.get_name_and_access(key, ip)[1]

    @classmethod
    def get_access_str(cls, key, ip=None):
        """
        Return access settings as string
        :param key: API key
        :param ip: IP address to check against ACL
        :return: String of '<api>:<role>,<api>:<role>,...'
        """
        return str(",".join("%s:%s" % a for a in cls.get_name_and_access(key, ip)[1]))

    @classmethod
    def get_name_and_access_str(cls, key, ip=None):
        """
        Return key name and access settings as string
        :param key: API key
        :param ip: IP address to check against ACL
        :return:
        """
        name, permissions = cls.get_name_and_access(key, ip)
        if not name:
            return None, ""
        return name, str(",".join("%s:%s" % a for a in permissions))
