# -*- coding: utf-8 -*-
# ---------------------------------------------------------------------
# MongoDB wrappers
# ---------------------------------------------------------------------
# Copyright (C) 2007-2017 The NOC Project
# See LICENSE for details
# ---------------------------------------------------------------------

# Python modules
import logging
import sys
import time
import datetime
# Third-party modules
from django.db.models import Model
from mongoengine.base import *
from mongoengine import *
import mongoengine
import six
import bson
# NOC modules
from noc.config import config
from noc.models import get_model
from noc.core.mongo.pool import Pool

logger = logging.getLogger(__name__)

# Connect to the database
RETRIES = config.mongo.retries
TIMEOUT = config.mongo.timeout

ca = config.mongo_connection_args.copy()
if ca.get("password"):
    ca["host"] = ca["host"].replace(":%s@" % ca["password"], ":********@")
    ca["password"] = "********"
for i in range(RETRIES):
    try:
        logger.info("Connecting to MongoDB %s", ca)
        connect_args = config.mongo_connection_args
        connect_args["_pool_class"] = Pool
        connect(**connect_args)
        break
    except mongoengine.connection.MongoEngineConnectionError as e:
        logger.error("Cannot connect to mongodb: %s", e)
        if i < RETRIES - 1:
            logger.error("Waiting %d seconds", TIMEOUT)
            time.sleep(TIMEOUT)
        else:
            logger.error("Cannot connect %d times. Exiting", RETRIES)
            sys.exit(1)

# Shortcut to ObjectId
try:
    import pymongo.objectid
    ObjectId = pymongo.objectid.ObjectId
except ImportError:
    import bson.objectid
    ObjectId = bson.objectid.ObjectId

RECURSIVE_REFERENCE_CONSTANT = "self"


def get_connection():
    """

    :return:
    :rtype: pymongo.collection.Connection
    """
    return mongoengine.connection._get_connection()


def get_db():
    """

    :return:
    :rtype: pymongo.database.Database
    """
    return mongoengine.connection._get_db()


class PlainReferenceField(BaseField):
    """
    A reference to the document that will be automatically
    dereferenced on access (lazily). Maps to plain ObjectId
    """

    def __init__(self, document_type, *args, **kwargs):
        if not isinstance(document_type, six.string_types):
            if not issubclass(document_type, (Document, six.string_types)):
                raise ValidationError("Argument to PlainReferenceField constructor "
                                      "must be a document class or a string")
        self.document_type_obj = document_type
        self.dereference = None
        super(PlainReferenceField, self).__init__(*args, **kwargs)

    def dereference_cached(self, value):
        return self.document_type.get_by_id(value)

    def dereference_uncached(self, value):
        return self.document_type.objects.filter(pk=value).first()

    def set_dereference(self):
        if hasattr(self.document_type, "get_by_id"):
            self.dereference = self.dereference_cached
        else:
            self.dereference = self.dereference_uncached

    @property
    def document_type(self):
        if isinstance(self.document_type_obj, six.string_types):
            if self.document_type_obj == RECURSIVE_REFERENCE_CONSTANT:
                self.document_type_obj = self.owner_document
            elif isinstance(self.document_type_obj, six.string_types):
                self.document_type_obj = get_model(self.document_type_obj)
            else:
                self.document_type_obj = get_document(self.document_type_obj)
        return self.document_type_obj

    def __get__(self, instance, owner):
        """
        Descriptor to allow lazy dereferencing
        """
        if instance is None:
            # Document class being used rather than a document object
            return self
        # Get value from document instance if available
        value = instance._data.get(self.name)
        # Dereference DBRefs
        if isinstance(value, ObjectId) or (isinstance(value, six.string_types) and len(value) == 24):
            if self.dereference is None:
                self.set_dereference()
            v = self.dereference(value)
            if v is not None:
                instance._data[self.name] = v
                return v
            else:
                raise ValidationError("Unable to dereference %s:%s" % (
                    self.document_type, value))
        return value

    def to_mongo(self, document):
        if isinstance(document, Document):
            # We need the id from the saved object to create the DBRef
            id_ = document.id
            if id_ is None:
                raise ValidationError("You can only reference documents once "
                                      "they have been saved to the database")
        else:
            if document:
                id_ = document
            else:
                return None
        id_field_name = self.document_type._meta["id_field"]
        id_field = self.document_type._fields[id_field_name]
        return id_field.to_mongo(id_)

    def lookup_member(self, name):
        return self.document_type._fields.get(name)

    def prepare_query_value(self, op, value):
        if value is None:
            return None
        return self.to_mongo(value)

    def set_cache(self, ttl=None):
        self.ttl = ttl


class PlainReferenceListField(PlainReferenceField):
    def __get__(self, instance, owner):
        def convert(value):
            if isinstance(value, ObjectId):
                # Dereference
                if hasattr(self.document_type, "get_by_id"):
                    return self.document_type.get_by_id(bson.ObjectId(value))
                else:
                    v = self.document_type.objects(id=value).first()
                if v is None:
                    raise ValidationError(
                        "Unable to dereference %s:%s" % (
                            self.document_type, v))
                return v
            else:
                return value

        if instance is None:
            # Document class being used rather than a document object
            return self
        # Get value from document instance if available
        value = instance._data.get(self.name)
        # Dereference DBRefs
        if value is not None:
            instance._data[self.name] = [convert(v) for v in value]
        return super(PlainReferenceField, self).__get__(instance, owner)

    def to_mongo(self, document):
        def convert(value):
            if isinstance(value, Document):
                # We need the id from the saved object to create the DBRef
                id = value.id
                if id is None:
                    raise ValidationError("You can only reference documents once "
                                          "they have been saved to the database")
            else:
                id = value
            return id_field.to_mongo(id)

        id_field_name = self.document_type._meta["id_field"]
        id_field = self.document_type._fields[id_field_name]
        if document:
            return [convert(v) for v in document]
        else:
            return document

    def prepare_query_value(self, op, value):
        if value is None:
            return None
        return PlainReferenceField.to_mongo(self, value)


class ForeignKeyField(BaseField):
    """
    A reference to the RDBMS" table that will be automatically
    dereferenced on access (lazily). Maps to integer
    """
    def __init__(self, model, **kwargs):
        if not issubclass(model, Model):
            raise ValidationError("Argument to ForeignKeyField constructor "
                                  "must be a Model class")
        self.document_type = model
        self.set_dereference()
        super(ForeignKeyField, self).__init__(**kwargs)

    def dereference_cached(self, value):
        return self.document_type.get_by_id(value)

    def dereference_uncached(self, value):
        o = self.document_type.objects.filter(pk=value)[:1]
        if o:
            return o[0]
        return None

    def set_dereference(self):
        if hasattr(self.document_type, "get_by_id"):
            self.dereference = self.dereference_cached
        else:
            self.dereference = self.dereference_uncached

    def __get__(self, instance, owner):
        """Descriptor to allow lazy dereferencing."""
        if instance is None:
            # Document class being used rather than a document object
            return self

        # Get value from document instance if available
        value = instance._data.get(self.name)
        # Dereference
        if isinstance(value, int):
            v = self.dereference(value)
            if v is not None:
                instance._data[self.name] = v
                return v
            else:
                raise ValidationError("Unable to dereference %s:%s" % (
                    self.document_type, value))
        return value

    def __set__(self, instance, value):
        if not value:
            value = None
        elif isinstance(value, six.string_types):
            value = int(value)
        super(ForeignKeyField, self).__set__(instance, value)

    def to_mongo(self, document):
        if isinstance(document, Model):
            # We need the id from the saved object to create the DBRef
            id_ = document.pk
            if id_ is None:
                raise ValidationError(
                    "You can only reference models once "
                    "they have been saved to the database"
                )
        else:
            id_ = document
        return id_

    def lookup_member(self, name):
        return None

    def prepare_query_value(self, op, value):
        if value is None:
            return None
        return self.to_mongo(value)


class DateField(DateTimeField):
    def to_mongo(self, value):
        v = super(DateField, self).to_mongo(value)
        if v is None:
            return None
        return datetime.datetime(year=v.year, month=v.month, day=v.day)

    def to_python(self, value):
        if isinstance(value, datetime.datetime):
            return datetime.date(year=value.year, month=value.month,
                                 day=value.day)
        else:
            return value


ESC1 = "__"  # Escape for '.'
ESC2 = "^^"  # Escape for '$'


class RawDictField(DictField):
    def validate(self, value):
        if not isinstance(value, dict):
            raise ValidationError("Only dictionaries may be used in a "
                                  "RawDictField")

    def to_python(self, value):
        return dict((k.replace(ESC1, ".").replace(ESC2, "$").replace(u"\uff0e", "."), v)
                    for k, v in value.items())

    def to_mongo(self, value):
        return dict((k.replace(".", ESC1).replace("$", ESC2), v)
                    for k, v in value.items())
