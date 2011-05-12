## -*- coding: utf-8 -*-
##----------------------------------------------------------------------
## MongoDB wrappers
##----------------------------------------------------------------------
## Copyright (C) 2007-2011 The NOC Project
## See LICENSE for details
##----------------------------------------------------------------------

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
    def __init__(self, document_type, **kwargs):
        if not isinstance(document_type, basestring):
            if not issubclass(document_type, (Document, basestring)):
                raise ValidationError('Argument to PlainReferenceField constructor '
                                      'must be a document class or a string')
        self.document_type_obj = document_type
        super(PlainReferenceField, self).__init__(**kwargs)
    
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
            value = self.document_type.objects(id=value).first()
            if value is not None:
                instance._data[self.name] = value
        return super(PlainReferenceField, self).__get__(instance, owner)

    def to_mongo(self, document):
        if isinstance(document, Document):
            # We need the id from the saved object to create the DBRef
            id_ = document.id
            if id_ is None:
                raise ValidationError('You can only reference documents once '
                                      'they have been saved to the database')
        else:
            id_ = document
        
        id_field_name = self.document_type._meta['id_field']
        id_field = self.document_type._fields[id_field_name]
        return id_field.to_mongo(id_)

    #def prepare_query_value(self, op, value):
    #    return self.to_mongo(value)

    #def validate(self, value):
    #    assert isinstance(value, (self.document_type, pymongo.dbref.DBRef))

    #def lookup_member(self, member_name):
    #    return self.document_type._fields.get(member_name)
