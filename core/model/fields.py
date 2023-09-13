# ----------------------------------------------------------------------
# Custom field types
# ----------------------------------------------------------------------
# Copyright (C) 2007-2020 The NOC Project
# See LICENSE for details
# ----------------------------------------------------------------------

# Python modules
from pickle import loads, dumps, HIGHEST_PROTOCOL

# Third-party modules
import psycopg2
import orjson
from pydantic import RootModel, ValidationError
from psycopg2.extensions import adapt
from django.db import models
from django.core.exceptions import ValidationError as DjangoValidationError
from django.db.models.fields.related_descriptors import ForwardManyToOneDescriptor
from django.db.models import CharField
from django.contrib.postgres.fields import ArrayField
from bson import ObjectId

# NOC Modules
from noc.core.ip import IP
from noc.core.comp import smart_text
from noc.core.validators import is_objectid
from noc.sa.interfaces.base import MACAddressParameter
from noc.models import get_model


class CIDRField(models.Field):
    """
    CIDRField maps to PostgreSQL CIDR
    """

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

    def db_type(self, connection):
        return "CIDR"

    def to_python(self, value):
        return str(value)

    def get_db_prep_value(self, value, connection, prepared=False):
        # Convert value to pure network address to prevent
        # PostgreSQL exception
        return IP.prefix(value).first.prefix


class INETField(models.Field):
    """
    INETField maps to PostgreSQL INET Field
    """

    def db_type(self, connection):
        return "INET"

    def get_db_prep_value(self, value, connection, prepared=False):
        if not value:
            return None
        return value


class MACField(models.Field):
    """
    MACField maps to the PostgreSQL MACADDR field
    """

    def db_type(self, connection):
        return "MACADDR"

    def from_db_value(self, value, expression, connection):
        if value is None:
            return None
        return value.upper()

    def get_db_prep_value(self, value, connection, prepared=False):
        if not value:
            return None
        return MACAddressParameter().clean(value)


class BinaryField(models.Field):
    """
    Binary Field maps to PostgreSQL BYTEA
    """

    def db_type(self, connection):
        return "BYTEA"


class TextArrayField(models.Field):
    """
    Text Array field maps to PostgreSQL TEXT[] type
    """

    def db_type(self, connection):
        return "TEXT[]"

    def from_db_value(self, value, expression, connection):
        def to_unicode(s):
            if isinstance(s, str):
                return s
            else:
                return smart_text(s)

        if value is None:
            return None
        return [to_unicode(x) for x in value]

    def get_default(self):
        if self.has_default():
            r = []
            for v in self.default:
                r += ['"%s"' % v.replace("\\", "\\\\").replace('"', '""')]
            return "{%s}" % ",".join(r)
        return ""


class InetArrayField(models.Field):
    """
    INETArrayField maps to PostgreSQL INET[] type
    """

    def db_type(self, connection):
        return "INET[]"

    def from_db_value(self, value, expression, connection):
        if isinstance(value, list):
            return value
        elif value == "{}":
            return []
        elif value is None:
            return None
        return value[1:-1].split(",")

    def get_db_prep_value(self, value, connection, prepared=False):
        if value is None:
            return None
        return "{ " + ", ".join(value) + " }"


class PickledField(models.Field):
    """
    Pickled object
    """

    def db_type(self, connection):
        return "BYTEA"

    def from_db_value(self, value, expression, connection):
        # if not value:
        #    return None
        try:
            return loads(value)
        except Exception:
            return value

    def get_db_prep_value(self, value, connection, prepared=False):
        return psycopg2.Binary(dumps(value, HIGHEST_PROTOCOL))


class AutoCompleteTagsField(models.Field):
    """
    Autocomplete tags fields
    """

    def db_type(self, connection):
        return "TEXT"


class TagsField(models.Field):
    def db_type(self, connection):
        return "TEXT[]"

    def from_db_value(self, value, expression, connection):
        def to_unicode(s):
            if isinstance(s, str):
                return s
            return smart_text(s)

        if value is None:
            return None
        elif isinstance(value, str):
            # Legacy AutoCompleteTagsField tweak
            if "," in value:
                value = value.split(",")
            value = [to_unicode(x) for x in value]
            return [x for x in value if x]
        else:
            return [to_unicode(x) for x in value]

    def get_db_prep_value(self, value, connection, prepared=False):
        return value


@TagsField.register_lookup
class TagsContainsLookup(models.Lookup):
    lookup_name = "contains"

    def as_sql(self, compiler, connection):
        tags = []
        for t in self.rhs:
            if not t.strip():
                continue
            t = adapt(t.strip())
            t.encoding = "utf8"
            tags += [smart_text(t).strip()]
        return "(ARRAY[%s] <@ %s)" % (",".join(tags), self.lhs.as_sql(compiler, connection)[0]), []


class DocumentReferenceDescriptor(object):
    def __init__(self, field):
        self.field = field
        self.document = self.field.document
        self.cache_name = field.get_cache_name()
        self.name = field.name
        self.dereference = None

    def dereference_cached(self, value):
        obj = self.document.get_by_id(value)
        if not obj:
            raise self.document.DoesNotExist()
        return obj

    def dereference_uncached(self, value):
        return self.document.objects.get(pk=value)

    def set_dereference(self):
        if isinstance(self.document, str):
            self.document = get_model(self.document)
            self.field.document = self.document
        if hasattr(self.document, "get_by_id"):
            self.dereference = self.dereference_cached
        else:
            self.dereference = self.dereference_uncached

    def is_cached(self, instance):
        if not self.dereference:
            self.set_dereference()
        return hasattr(instance, self.cache_name)

    def __get__(self, instance, instance_type=None):
        if instance is None:
            return self
        try:
            # Try already resolved value
            return getattr(instance, self.cache_name)
        except AttributeError:
            val = instance.__dict__.get(self.name) or None
            if val is None:
                # If NULL is an allowed value, return it.
                if self.field.null:
                    return None
                raise self.document.DoesNotExist()
            if not self.dereference:
                self.set_dereference()
            rel_obj = self.dereference(val)
            setattr(instance, self.cache_name, rel_obj)
            return rel_obj

    def _reset_cache(self, instance):
        if self.is_cached(instance):
            del instance.__dict__[self.cache_name]

    def __set__(self, instance, value):
        if instance is None:
            raise AttributeError("%s must be accessed via instance" % self.field.name)
        if not self.dereference:
            self.set_dereference()
        # If null=True, we can assign null here, but otherwise the value needs
        # to be an instance of the related class.
        if value is None and self.field.null is False:
            raise ValueError(
                'Cannot assign None: "%s.%s" does not allow null values.'
                % (instance._meta.object_name, self.field.name)
            )
        elif value is None or isinstance(value, str):
            self._reset_cache(instance)
        elif isinstance(value, ObjectId):
            self._reset_cache(instance)
            value = str(value)
        elif value and isinstance(value, self.document):
            # Save to cache
            setattr(instance, self.cache_name, value)
            value = str(value.id)
        else:
            raise ValueError(
                'Cannot assign "%r": "%s.%s" must be a "%s" instance.'
                % (value, instance._meta.object_name, self.field.name, self.document)
            )
        instance.__dict__[self.name] = value


class DocumentReferenceField(models.Field):
    def __init__(self, document, *args, **kwargs):
        self.document = document
        super().__init__(*args, **kwargs)

    def contribute_to_class(self, cls, name, *args, **kwargs):
        super().contribute_to_class(cls, name, *args, **kwargs)
        setattr(cls, self.name, DocumentReferenceDescriptor(self))

    def db_type(self, connection):
        return "CHAR(24)"

    def get_prep_value(self, value):
        if value is None:
            return None
        elif isinstance(value, str):
            return value
        elif isinstance(value, ObjectId):
            return str(value)
        else:
            # Dereference
            # @todo: Maybe .pk is better way
            return str(value.id)

    def get_cache_name(self):
        return "_%s_cache" % self.name


class CachedForeignKeyDescriptor(ForwardManyToOneDescriptor):
    def get_object(self, instance):
        ref = getattr(instance, self.field.attname, None)
        if ref:
            # Fast cached path
            return self.field.remote_field.model.get_by_id(ref)
        return super().get_object(instance)


class CachedForeignKey(models.ForeignKey):
    forward_related_accessor_class = CachedForeignKeyDescriptor


class CharField24(CharField):
    def db_type(self, connection):
        return "CHAR(24)"


class ObjectIDArrayField(ArrayField):
    """
    ObjectIDArrayField maps to PostgreSQL CHAR[] type
    """

    def __init__(self, size=None, **kwargs):
        super().__init__(CharField24(max_length=24), size=size, **kwargs)

    def db_type(self, connection):
        return "CHAR(24)[]"

    def get_db_prep_value(self, value, connection, prepared=False):
        if value is None:
            return None
        if isinstance(value, (str, ObjectId)):
            value = [value]
        return "{ %s }" % ", ".join(
            str(x) for x in sorted(set(value), key=lambda x: value.index(x)) if is_objectid(str(x))
        )

    def validate(self, value, model_instance):
        # Only form.full_clean execute
        super().validate(value, model_instance)
        if isinstance(value, (str, ObjectId)):
            value = [value]
        for v in value:
            if not is_objectid(v):
                raise ValueError(f"Nont ObjectId value on {model_instance} ObjectIDArrayField")


class PydanticField(models.JSONField):
    def __init__(
        self, verbose_name=None, name=None, encoder=None, decoder=None, schema=None, **kwargs
    ):
        self.schema: RootModel = schema
        super().__init__(verbose_name, name, encoder, decoder, **kwargs)

    def get_db_prep_value(self, value, connection, prepared=False):
        if not prepared:
            try:
                self.schema.model_validate(value)
            except ValidationError as e:
                raise ValueError(e)
        return super().get_db_prep_value(value, connection, prepared=prepared)

    def get_prep_value(self, value):
        if value is None:
            return value
        return orjson.dumps(value).decode("utf-8")

    def validate(self, value, model_instance):
        # Only form.full_clean execute
        super().validate(value, model_instance)
        try:
            self.schema.model_validate(value)
        except ValidationError as e:
            raise DjangoValidationError(e)
