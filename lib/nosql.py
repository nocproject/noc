## -*- coding: utf-8 -*-
##----------------------------------------------------------------------
## MongoDB wrappers
##----------------------------------------------------------------------
## Copyright (C) 2007-2011 The NOC Project
## See LICENSE for details
##----------------------------------------------------------------------

## Python modules
import logging
import sys
## Django modules
from django.db.models import Model
from django.db import IntegrityError
import django.db.models.signals
## Third-party modules
import pymongo
from mongoengine.base import *
from mongoengine import *
import mongoengine
## NOC modules
from noc import settings

##
## Create database connection
## @todo: Handle tests
if settings.IS_TEST:
    db_name = settings.NOSQL_DATABASE_TEST_NAME
else:
    db_name = settings.NOSQL_DATABASE_NAME
connection_args = {
    "db": db_name,
    "username": settings.NOSQL_DATABASE_USER,
    "password": settings.NOSQL_DATABASE_PASSWORD
}
if settings.NOSQL_DATABASE_HOST:
    connection_args["host"] = settings.NOSQL_DATABASE_HOST
if settings.NOSQL_DATABASE_PORT:
    connection_args["port"] = int(settings.NOSQL_DATABASE_PORT)

## Connect to the database
try:
    connect(**connection_args)
except mongoengine.connection.ConnectionError, why:
    logging.error("Cannot connect to mongodb: %s" % why)
    sys.exit(1)

## Shortcut to ObjectId
try:
    import pymongo.objectid
    ObjectId = pymongo.objectid.ObjectId
except ImportError:
    import bson.objectid
    ObjectId = bson.objectid.ObjectId

RECURSIVE_REFERENCE_CONSTANT = "self"


def get_connection():
    return mongoengine.connection._get_connection()


def get_db():
    return mongoengine.connection._get_db()


class PlainReferenceField(BaseField):
    """
    A reference to the document that will be automatically
    dereferenced on access (lazily). Maps to plain ObjectId
    """
    def __init__(self, document_type, *args, **kwargs):
        if not isinstance(document_type, basestring):
            if not issubclass(document_type, (Document, basestring)):
                raise ValidationError("Argument to PlainReferenceField constructor "
                                      "must be a document class or a string")
        self.document_type_obj = document_type
        super(PlainReferenceField, self).__init__(*args, **kwargs)

    @property
    def document_type(self):
        if isinstance(self.document_type_obj, basestring):
            if self.document_type_obj == RECURSIVE_REFERENCE_CONSTANT:
                self.document_type_obj = self.owner_document
            else:
                self.document_type_obj = get_document(self.document_type_obj)
        return self.document_type_obj

    def __get__(self, instance, owner):
        """Descriptor to allow lazy dereferencing."""
        if instance is None:
            # Document class being used rather than a document object
            return self
        # Get value from document instance if available
        value = instance._data.get(self.name)
        # Dereference DBRefs
        if isinstance(value, ObjectId):
            v = self.document_type.objects(id=value).first()
            if v is not None:
                instance._data[self.name] = v
            else:
                raise ValidationError("Unable to dereference %s:%s" % (
                    self.document_type, value))
        return super(PlainReferenceField, self).__get__(instance, owner)

    def to_mongo(self, document):
        if isinstance(document, Document):
            # We need the id from the saved object to create the DBRef
            id_ = document.id
            if id_ is None:
                raise ValidationError("You can only reference documents once "
                                      "they have been saved to the database")
        else:
            id_ = document
        id_field_name = self.document_type._meta["id_field"]
        id_field = self.document_type._fields[id_field_name]
        return id_field.to_mongo(id_)

    def lookup_member(self, name):
        return self.document_type._fields.get(name)

    def prepare_query_value(self, op, value):
        if value is None:
            return None
        return self.to_mongo(value)


class PlainReferenceListField(PlainReferenceField):
    def __get__(self, instance, owner):
        def convert(value):
            if isinstance(value, ObjectId):
                # Dereference
                v = self.document_type.objects(id=value).first()
                if v is None:
                    raise ValidationError("Unable to dereference %s:%s" % (
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
        super(ForeignKeyField, self).__init__(**kwargs)
        if not settings.IS_TEST:
            django.db.models.signals.pre_delete.connect(self.on_ref_delete,
                                                        sender=model)

    def on_ref_delete(self, sender, instance, **kwargs):
        """
        Check referenced object is not deleted
        :param sender:
        :param instance:
        :param using:
        :return:
        """
        if not self.name:
            return
        doc = self.owner_document
        if doc.objects.filter(**{self.name: instance.id}).first() is not None:
            raise IntegrityError("%r object is referenced from %r" % (instance,
                                                                      doc))

    def __get__(self, instance, owner):
        """Descriptor to allow lazy dereferencing."""
        if instance is None:
            # Document class being used rather than a document object
            return self

        # Get value from document instance if available
        value = instance._data.get(self.name)
        # Dereference
        if isinstance(value, int):
            value = self.document_type.objects.get(pk=value)
            if value is not None:
                instance._data[self.name] = value
        return super(ForeignKeyField, self).__get__(instance, owner)

    def to_mongo(self, document):
        if isinstance(document, Model):
            # We need the id from the saved object to create the DBRef
            id_ = document.pk
            if id_ is None:
                raise ValidationError("You can only reference models once "
                                      "they have been saved to the database")
        else:
            id_ = document
        return id_

    def lookup_member(self, name):
        return None

    def prepare_query_value(self, op, value):
        if value is None:
            return None
        return self.to_mongo(value)


ESC1 = "__"  # Escape for '.'
ESC2 = "^^"  # Escape for '$'


class RawDictField(DictField):
    def validate(self, value):
        if not isinstance(value, dict):
            raise ValidationError("Only dictionaries may be used in a "
                                  "RawDictField")

    def to_python(self, value):
        return dict([(k.replace(ESC1, ".").replace(ESC2, "$").replace(u"\uff0e", "."), v)
            for k, v in value.items()])

    def to_mongo(self, value):
        return dict([(k.replace(".", ESC1).replace("$", ESC2), v)
            for k, v in value.items()])


class Sequence(object):
    """
    Unique sequence number generator
    """
    def __init__(self, name, prefix, shard_id):
        # Generate sequence template
        self.format = "%s%d.%%d" % (prefix, shard_id)
        self.name = name
        self.sequences = get_db().noc.sequences["s%d" % shard_id]
        self.sequences.insert({"_id": self.name, "value": 0L})

    def next(self):
        s = self.sequences.find_and_modify(
            query={"_id": self.name},
            update={"$inc": {"value": 1}},
            new=True
        )
        return self.format % s["value"]


def create_test_db(verbosity, autoclobber):
    connect(**connection_args)

    
def destroy_test_db(verbosity):
    get_connection().drop_database(settings.NOSQL_DATABASE_TEST_NAME)
