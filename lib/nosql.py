## -*- coding: utf-8 -*-
##----------------------------------------------------------------------
## MongoDB wrappers
##----------------------------------------------------------------------
## Copyright (C) 2007-2011 The NOC Project
## See LICENSE for details
##----------------------------------------------------------------------

## Django modules
from django.db.models import Model
## Third-party modules
import pymongo
from mongoengine.base import *
from mongoengine import *
## NOC modules
import noc.settings

##
## Create database connection
## @todo: Handle tests
connect(noc.settings.NOSQL_DATABASE_NAME,
        noc.settings.NOSQL_DATABASE_USER,
        noc.settings.NOSQL_DATABASE_PASSWORD)
## Shortcut to ObjectId
ObjectId = pymongo.objectid.ObjectId


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
    
    def __get__(self, instance, owner):
        """Descriptor to allow lazy dereferencing."""
        if instance is None:
            # Document class being used rather than a document object
            return self

        # Get value from document instance if available
        value = instance._data.get(self.name)
        # Dereference
        if isinstance(value, int):
            value = self.document_type.objects.get(id=value)
            if value is not None:
                instance._data[self.name] = value
        return super(ForeignKeyField, self).__get__(instance, owner)

    def to_mongo(self, document):
        if isinstance(document, Model):
            # We need the id from the saved object to create the DBRef
            id_ = document.id
            if id_ is None:
                raise ValidationError("You can only reference models once "
                                      "they have been saved to the database")
        else:
            id_ = document
        return id_


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
