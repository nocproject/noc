# -*- coding: utf-8 -*-
# ----------------------------------------------------------------------
# APIKey model
# ----------------------------------------------------------------------
# Copyright (C) 2007-2018 The NOC Project
# See LICENSE for details
# ----------------------------------------------------------------------

# Python modules
import datetime
# Third-party modules
from mongoengine.document import Document, EmbeddedDocument
from mongoengine.fields import (StringField, BooleanField, DateTimeField, ListField,
                                EmbeddedDocumentField)


class APIAccess(EmbeddedDocument):
    # Api name
    api = StringField()
    # Additional API role, * for wildcard
    role = StringField()

    def __unicode__(self):
        return "%s:%s" % (self.api, self.role)


class APIKey(Document):
    meta = {
        "collection": "apikeys",
        "strict": False,
        "auto_create_index": False
    }

    name = StringField(unique=True)
    is_active = BooleanField()
    description = StringField()
    expires = DateTimeField()
    # Secret API key
    key = StringField(unique=True)
    # Access settings
    access = ListField(EmbeddedDocumentField(APIAccess))

    def __unicode__(self):
        return self.name

    @classmethod
    def get_name_and_access(cls, key):
        """
        Return access settings for key and key name
        :param key: API key
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
        # Process key access
        access = doc.get("access", [])
        r = []
        for a in access:
            r += [(a.get("api"), a.get("role", "*"))]
        return doc["name"], r

    @classmethod
    def get_access(cls, key):
        """
        Return access settings for key
        :param key: API key
        :return: List of (api, role). Empty list for denied permissions
        """
        return cls.get_name_and_access(key)[1]

    @classmethod
    def get_access_str(cls, key):
        """
        Return access settings as string
        :param key: API key
        :return: String of '<api>:<role>,<api>:<role>,...'
        """
        r = ["%s:%s" % a for a in cls.get_access(key)]
        return str(",".join(r))

    @classmethod
    def get_name_and_access_str(cls, key):
        """
        Return key name and access settings as string
        :param key:
        :return:
        """
        name, permissions = cls.get_name_and_access(key)
        if not name:
            return None, ""
        r = ["%s:%s" % a for a in permissions]
        return name, str(",".join(r))
