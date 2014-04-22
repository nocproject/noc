# -*- coding: utf-8 -*-
##----------------------------------------------------------------------
## Custom field types
##----------------------------------------------------------------------
## Copyright (C) 2007-2009 The NOC Project
## See LICENSE for details
##----------------------------------------------------------------------
from django.db import models
from noc.lib.ip import IP
import types,cPickle
from django.contrib.admin.widgets import AdminTextInputWidget
from south.modelsinspector import add_introspection_rules
from noc.sa.interfaces.base import MACAddressParameter
from noc.lib.text import ranges_to_list, list_to_ranges
##
## CIDRField maps to PostgreSQL CIDR
##
class CIDRField(models.Field):
    def __init__(self,*args,**kwargs):
        super(CIDRField,self).__init__(*args,**kwargs)
        
    def db_type(self, connection):
        return "CIDR"
        
    def to_python(self,value):
        return str(value)
        
    def get_db_prep_value(self, value, connection, prepared=False):
        # Convert value to pure network address to prevent
        # PostgreSQL exception
        return IP.prefix(value).first.prefix
    

##
## INETField maps to PostgreSQL INET Field
##
class INETField(models.Field):
    def db_type(self, connection):
        return "INET"
    
    def to_python(self,value):
        return str(value)
    
    def get_db_prep_value(self, value, connection, prepared=False):
        if not value:
            return None
        return value
##
## MACField maps to the PostgreSQL MACADDR field
##
class MACField(models.Field):
    __metaclass__=models.SubfieldBase
    def db_type(self, connection):
        return "MACADDR"
    
    def to_python(self,value):
        if value is None:
            return None
        return value.upper()
    
    def get_db_prep_value(self, value, connection, prepared=False):
        if not value:
            return None
        return MACAddressParameter().clean(value)
##
## Binary Field maps to PostgreSQL BYTEA
##
class BinaryField(models.Field):
    def db_type(self, connection):
        return "BYTEA"
##
## Text Array field maps to PostgreSQL TEXT[] type
##
class TextArrayField(models.Field):
    __metaclass__ = models.SubfieldBase
    
    def db_type(self, connection):
        return "TEXT[]"

    def to_python(self,value):
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
                r += ["\"%s\"" % v.replace("\\", "\\\\").replace("\"", "\"\"")]
            return "{%s}" % ",".join(r)
        return ""

##
## Two-dimensioned text array field maps to PostgreSQL TEXT[][]
##
class TextArray2Field(models.Field):
    __metaclass__ = models.SubfieldBase
    
    def db_type(self, connection):
        return "TEXT[][]"

    def to_python(self,value):
        def to_unicode(s):
            if type(s)==types.UnicodeType:
                return s
            else:
                try:
                    return unicode(s.replace("\\\\","\\"),"utf-8")
                except UnicodeDecodeError:
                    return s
        if value is None:
            return None
        return [[to_unicode(y) for y in x] for x in value]
    

##
## INETArrayField maps to PostgreSQL INET[] type
##
class InetArrayField(models.Field):
    __metaclass__ = models.SubfieldBase
    def db_type(self, connection):
        return "INET[]"

    def to_python(self,value):
        if type(value)==types.ListType:
            return value
        elif value=="{}":
            return []
        elif value is None:
            return None
        return value[1:-1].split(",")
        
    def get_db_prep_value(self, value, connection, prepared=False):
        if value is None:
            return None
        return "{ "+", ".join(value)+" }"

##
## IntArrayField maps to PostgreSQL INT[] type
##
class IntArrayField(models.Field):
    __metaclass__ = models.SubfieldBase
    def db_type(self, connection):
        return "INT[]"

    def to_python(self,value):
        if type(value)==types.ListType:
            return value
        elif value=="{}":
            return []
        elif value is None:
            return None
        return [int(x) for x in value[1:-1].split(",")]
        
    def get_db_prep_value(self, value, connection, prepared=False):
        if value is None:
            return None
        return "{ "+", ".join([str(x) for x in value])+" }"

##
##
##
class DateTimeArrayField(models.Field):
    __metaclass__ = models.SubfieldBase
    def db_type(self, connection):
        return "TIMESTAMP[]"
    
    def to_python(self,value):
        if type(value)==types.ListType:
            return value
        elif value=="{}":
            return []
        elif value is None:
            return None
        return [x for x in value[1:-1].split(",")] # @todo: fix
    
    def get_db_prep_value(self, value, connection, prepared=False):
        if value is None:
            return None
        return "{ "+", ".join([str(x) for x in value])+" }"
    

##
## A set of integer. Compactly encoded with ranges
##
class IntMapField(models.Field):
    __metaclass__ = models.SubfieldBase
    def db_type(self, connection):
        return "TEXT"
    
    def to_python(self,value):
        if not value:
            return set()
        if isinstance(value, basestring):
            return set(ranges_to_list(value))
        else:
            return value
    
    def get_db_prep_value(self, value, connection, prepared=False):
        return list_to_ranges(sorted(value))
    

##
## Pickled object
##
class PickledField(models.Field):
    __metaclass__ = models.SubfieldBase
    def db_type(self, connection):
        return "TEXT"
    def to_python(self,value):
        #if not value:
        #    return None
        try:
            return cPickle.loads(str(value))
        except:
            return value
    
    def get_db_prep_value(self, value, connection, prepared=False):
        return cPickle.dumps(value)
##
## Autocomplete tags fields
##
class AutoCompleteTagsField(models.Field):
    def db_type(self, connection):
        return "TEXT"
    def formfield(self, **kwargs):
        from noc.lib.widgets import AutoCompleteTags
        defaults = {'widget': AutoCompleteTags}
        defaults.update(kwargs)
        if defaults['widget'] == AdminTextInputWidget:
            defaults['widget']=AutoCompleteTags
        return super(AutoCompleteTagsField,self).formfield(**defaults)


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


##
## Color field
##
class ColorField(models.Field):
    __metaclass__ = models.SubfieldBase
    default_validators=[]
    
    def db_type(self, connection):
        return "INTEGER"
    
    def __init__(self,*args,**kwargs):
        super(ColorField,self).__init__(*args,**kwargs)
    
    def to_python(self,value):
        if isinstance(value,basestring):
            return value
        return u"#%06x"%value
    
    def get_db_prep_value(self, value, connection, prepared=False):
        if isinstance(value, basestring):
            if value.startswith("#"):
                value = value[1:]
            return int(value, 16)
        else:
            return value


##
add_introspection_rules([],["^noc\.lib\.fields\."])