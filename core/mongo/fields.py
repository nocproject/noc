# ----------------------------------------------------------------------
# Custom MongoEngine fields
# ----------------------------------------------------------------------
# Copyright (C) 2007-2020 The NOC Project
# See LICENSE for details
# ----------------------------------------------------------------------

# Python modules
import datetime

# Third-party modules
from mongoengine.document import Document
from mongoengine.base import get_document
from mongoengine.fields import BaseField, DateTimeField, DictField
from mongoengine.base.datastructures import BaseList
from mongoengine.errors import ValidationError
from bson import ObjectId
from django.db.models import Model

# NOC models
from noc.models import get_model

RECURSIVE_REFERENCE_CONSTANT = "self"


class PlainReferenceField(BaseField):
    """
    A reference to the document that will be automatically
    dereferenced on access (lazily). Maps to plain ObjectId
    """

    def __init__(self, document_type, *args, **kwargs):
        if not isinstance(document_type, str):
            if not issubclass(document_type, (Document, str)):
                raise ValidationError(
                    "Argument to PlainReferenceField constructor "
                    "must be a document class or a string"
                )
        self.document_type_obj = document_type
        self.dereference = None
        super().__init__(*args, **kwargs)

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
        if isinstance(self.document_type_obj, str):
            if self.document_type_obj == RECURSIVE_REFERENCE_CONSTANT:
                self.document_type_obj = self.owner_document
            elif isinstance(self.document_type_obj, str):
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
        if isinstance(value, ObjectId) or (isinstance(value, str) and len(value) == 24):
            if self.dereference is None:
                self.set_dereference()
            v = self.dereference(value)
            if v is not None:
                instance._data[self.name] = v
                return v
            else:
                raise ValidationError("Unable to dereference %s:%s" % (self.document_type, value))
        return value

    def to_mongo(self, document):
        if isinstance(document, Document):
            # We need the id from the saved object to create the DBRef
            id_ = document.id
            if id_ is None:
                raise ValidationError(
                    "You can only reference documents once " "they have been saved to the database"
                )
        elif document:
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
                    return self.document_type.get_by_id(ObjectId(value))
                else:
                    v = self.document_type.objects(id=value).first()
                if v is None:
                    raise ValidationError("Unable to dereference %s:%s" % (self.document_type, v))
                return v
            else:
                return value

        if instance is None:
            # Document class being used rather than a document object
            return self
        # Get value from document instance if available
        value = instance._data.get(self.name)
        # Dereference DBRefs value = BaseList(value, instance, self.name)
        if value is not None:
            instance._data[self.name] = BaseList([convert(v) for v in value], instance, self.name)
        return super().__get__(instance, owner)

    def to_mongo(self, document):
        def convert(value):
            if isinstance(value, Document):
                # We need the id from the saved object to create the DBRef
                id = value.id
                if id is None:
                    raise ValidationError(
                        "You can only reference documents once "
                        "they have been saved to the database"
                    )
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
            raise ValidationError("Argument to ForeignKeyField constructor must be a Model class")
        self.document_type = model
        self.set_dereference()
        super().__init__(**kwargs)

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
                raise ValidationError("Unable to dereference %s:%s" % (self.document_type, value))
        return value

    def __set__(self, instance, value):
        if not value:
            value = None
        elif isinstance(value, str):
            value = int(value)
        super().__set__(instance, value)

    def to_mongo(self, document):
        if isinstance(document, Model):
            # We need the id from the saved object to create the DBRef
            id_ = document.pk
            if id_ is None:
                raise ValidationError(
                    "You can only reference models once they have been saved to the database"
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


class ForeignKeyListField(ForeignKeyField):
    def __get__(self, instance, owner):
        def convert(value):
            # Get value from document instance if available
            # Dereference
            if isinstance(value, int):
                v = self.dereference(value)
                if v is not None:
                    instance._data[self.name] = v
                    return v
                else:
                    raise ValidationError(
                        "Unable to dereference %s:%s" % (self.document_type, value)
                    )
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
        return super().__get__(instance, owner)

    def to_mongo(self, document):
        def convert(value):
            if isinstance(value, Model):
                # We need the id from the saved object to create the DBRef
                id_ = value.pk
                if id_ is None:
                    raise ValidationError(
                        "You can only reference models once they have been saved to the database"
                    )
                return id_
            else:
                return value

        if document:
            return [convert(v) for v in document]
        else:
            return document

    def prepare_query_value(self, op, value):
        if value is None:
            return None
        return ForeignKeyField.to_mongo(self, value)


class DateField(DateTimeField):
    def to_mongo(self, value):
        v = super().to_mongo(value)
        if v is None:
            return None
        return datetime.datetime(year=v.year, month=v.month, day=v.day)

    def to_python(self, value):
        if isinstance(value, datetime.datetime):
            return datetime.date(year=value.year, month=value.month, day=value.day)
        else:
            return value


ESC1 = "__"  # Escape for '.'
ESC2 = "^^"  # Escape for '$'


class RawDictField(DictField):
    def validate(self, value):
        if not isinstance(value, dict):
            raise ValidationError("Only dictionaries may be used in a RawDictField")

    def to_python(self, value):
        return {
            k.replace(ESC1, ".").replace(ESC2, "$").replace("\uff0e", "."): v
            for k, v in value.items()
        }

    def to_mongo(self, value):
        return {k.replace(".", ESC1).replace("$", ESC2): v for k, v in value.items()}
