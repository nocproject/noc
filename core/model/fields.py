# -*- coding: utf-8 -*-
##----------------------------------------------------------------------
## Custom field types
##----------------------------------------------------------------------
## Copyright (C) 2007-2015 The NOC Project
## See LICENSE for details
##----------------------------------------------------------------------

## Python modules
import types
import cPickle
## Django modules
from django.db import models
## Third-party modules
from south.modelsinspector import add_introspection_rules
## NOC Modules
from noc.lib.ip import IP
from noc.sa.interfaces.base import MACAddressParameter
from noc.lib.text import ranges_to_list, list_to_ranges


class CIDRField(models.Field):
    """
    CIDRField maps to PostgreSQL CIDR
    """

    def __init__(self, *args, **kwargs):
        super(CIDRField, self).__init__(*args, **kwargs)

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

    def to_python(self, value):
        return str(value)

    def get_db_prep_value(self, value, connection, prepared=False):
        if not value:
            return None
        return value


class MACField(models.Field):
    """
    MACField maps to the PostgreSQL MACADDR field
    """
    __metaclass__ = models.SubfieldBase

    def db_type(self, connection):
        return "MACADDR"

    def to_python(self, value):
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
    __metaclass__ = models.SubfieldBase

    def db_type(self, connection):
        return "TEXT[]"

    def to_python(self, value):
        def to_unicode(s):
            if isinstance(s, unicode):
                return s
            else:
                return unicode(s, "utf-8")

        if value is None:
            return None
        return [to_unicode(x) for x in value]

    def get_default(self):
        if self.has_default():
            r = []
            for v in self.default:
                r += [
                    "\"%s\"" % v.replace("\\", "\\\\")
                        .replace("\"", "\"\"")
                ]
            return "{%s}" % ",".join(r)
        return ""


class TextArray2Field(models.Field):
    """
    Two-dimensioned text array field maps to PostgreSQL TEXT[][]
    """
    __metaclass__ = models.SubfieldBase

    def db_type(self, connection):
        return "TEXT[][]"

    def to_python(self, value):
        def to_unicode(s):
            if type(s) == types.UnicodeType:
                return s
            else:
                try:
                    return unicode(s.replace("\\\\", "\\"), "utf-8")
                except UnicodeDecodeError:
                    return s

        if value is None:
            return None
        return [[to_unicode(y) for y in x] for x in value]


class InetArrayField(models.Field):
    """
    INETArrayField maps to PostgreSQL INET[] type
    """
    __metaclass__ = models.SubfieldBase

    def db_type(self, connection):
        return "INET[]"

    def to_python(self, value):
        if isinstance(value, types.ListType):
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


class IntArrayField(models.Field):
    """
    IntArrayField maps to PostgreSQL INT[] type
    """
    __metaclass__ = models.SubfieldBase

    def db_type(self, connection):
        return "INT[]"

    def to_python(self, value):
        if isinstance(value, types.ListType):
            return value
        elif value == "{}":
            return []
        elif value is None:
            return None
        return [int(x) for x in value[1:-1].split(",")]

    def get_db_prep_value(self, value, connection, prepared=False):
        if value is None:
            return None
        return "{ " + ", ".join([str(x) for x in value]) + " }"


class DateTimeArrayField(models.Field):
    __metaclass__ = models.SubfieldBase

    def db_type(self, connection):
        return "TIMESTAMP[]"

    def to_python(self, value):
        if type(value) == types.ListType:
            return value
        elif value == "{}":
            return []
        elif value is None:
            return None
        return [x for x in value[1:-1].split(",")]  # @todo: fix

    def get_db_prep_value(self, value, connection, prepared=False):
        if value is None:
            return None
        return "{ " + ", ".join([str(x) for x in value]) + " }"


class IntMapField(models.Field):
    """
    A set of integer. Compactly encoded with ranges
    """
    __metaclass__ = models.SubfieldBase

    def db_type(self, connection):
        return "TEXT"

    def to_python(self, value):
        if not value:
            return set()
        if isinstance(value, basestring):
            return set(ranges_to_list(value))
        else:
            return value

    def get_db_prep_value(self, value, connection, prepared=False):
        return list_to_ranges(sorted(value))


class PickledField(models.Field):
    """
    Pickled object
    """
    __metaclass__ = models.SubfieldBase

    def db_type(self, connection):
        return "TEXT"

    def to_python(self, value):
        # if not value:
        #    return None
        try:
            return cPickle.loads(str(value))
        except:
            return value

    def get_db_prep_value(self, value, connection, prepared=False):
        return cPickle.dumps(value)


class AutoCompleteTagsField(models.Field):
    """
    Autocomplete tags fields
    """

    def db_type(self, connection):
        return "TEXT"

    def formfield(self, **kwargs):
        from noc.lib.widgets import AutoCompleteTags
        defaults = {'widget': AutoCompleteTags}
        defaults.update(kwargs)
        if defaults['widget'] == AdminTextInputWidget:
            defaults['widget'] = AutoCompleteTags
        return super(AutoCompleteTagsField, self).formfield(**defaults)


class TagsField(models.Field):
    __metaclass__ = models.SubfieldBase

    def db_type(self, connection):
        return "TEXT[]"

    def to_python(self, value):
        def to_unicode(s):
            if type(s) == types.UnicodeType:
                return s
            else:
                return unicode(s, "utf-8")

        if value is None:
            return None
        elif isinstance(value, basestring):
            # Legacy AutoCompleteTagsField tweak
            if "," in value:
                value = value.split(",")
            value = [to_unicode(x) for x in value]
            return [x for x in value if x]
        else:
            return [to_unicode(x) for x in value]

    def formfield(self, **kwargs):
        from noc.lib.widgets import AutoCompleteTags
        defaults = {'widget': AutoCompleteTags}
        defaults.update(kwargs)
        if defaults['widget'] == AdminTextInputWidget:
            defaults['widget'] = AutoCompleteTags
        return super(TagsField, self).formfield(**defaults)

    def get_db_prep_value(self, value, connection, prepared=False):
        return value


class ColorField(models.Field):
    """
    Color field
    """
    __metaclass__ = models.SubfieldBase
    default_validators = []

    def db_type(self, connection):
        return "INTEGER"

    def __init__(self, *args, **kwargs):
        super(ColorField, self).__init__(*args, **kwargs)

    def to_python(self, value):
        if isinstance(value, basestring):
            return value
        return u"#%06x" % value

    def get_db_prep_value(self, value, connection, prepared=False):
        if isinstance(value, basestring):
            if value.startswith("#"):
                value = value[1:]
            return int(value, 16)
        else:
            return value


class DocumentReferenceDescriptor(object):
    def __init__(self, field):
        self.field = field
        self.cache_name = field.get_cache_name()
        self.raw_name = field.raw_name

    def is_cached(self, instance):
        return hasattr(instance, self.cache_name)

    def __get__(self, instance, instance_type=None):
        if instance is None:
            return self
        try:
            # Try already resolved value
            return getattr(instance, self.cache_name)
        except AttributeError:
            val = getattr(instance, self.raw_name)
            if val is None:
                # If NULL is an allowed value, return it.
                if self.field.null:
                    return None
                raise self.field.document.DoesNotExist
            rel_obj = self.field.document.objects.get(id=val)
            setattr(instance, self.cache_name, rel_obj)
            return rel_obj

    def __set__(self, instance, value):
        if instance is None:
            raise AttributeError(
                "%s must be accessed via instance" % self.field.name)
        # If null=True, we can assign null here, but otherwise the value needs
        # to be an instance of the related class.
        if value is None and self.field.null == False:
            raise ValueError(
                "Cannot assign None: \"%s.%s\" does not allow null values." % (
                    instance._meta.object_name, self.field.name)
            )
        elif value is not None and not isinstance(value, (self.field.document, basestring)):
            raise ValueError(
                "Cannot assign \"%r\": \"%s.%s\" must be a \"%s\" instance." % (
                    value, instance._meta.object_name,
                    self.field.name, self.field.document))
        elif value and isinstance(value, self.field.document):
            # Save to cache
            setattr(instance, self.cache_name, value)
            value = str(value.id)
        setattr(instance, self.raw_name, value)


class DocumentReferenceField(models.Field):
    def __init__(self, document, *args, **kwargs):
        self.document = document
        super(DocumentReferenceField, self).__init__(*args, **kwargs)

    def contribute_to_class(self, cls, name):
        super(DocumentReferenceField, self).contribute_to_class(cls,
                                                                name)
        self.raw_name = name + "_raw"
        setattr(cls, self.name, DocumentReferenceDescriptor(self))

    def db_type(self, connection):
        return "CHAR(24)"

    def get_prep_value(self, value):
        if value is None:
            return None
        elif isinstance(value, basestring):
            return value
        else:
            return str(value.id)

##
add_introspection_rules([], ["^noc\.core\.model\.fields\."])
from django.contrib.admin.widgets import AdminTextInputWidget
