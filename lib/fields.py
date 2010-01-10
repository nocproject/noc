# -*- coding: utf-8 -*-
##----------------------------------------------------------------------
## Custom field types
##----------------------------------------------------------------------
## Copyright (C) 2007-2009 The NOC Project
## See LICENSE for details
##----------------------------------------------------------------------
from django.db import models
from lib.ip import normalize_prefix
import types,cPickle
##
## CIDRField maps to PostgreSQL CIDR
##
class CIDRField(models.Field):
    def __init__(self,*args,**kwargs):
        super(CIDRField,self).__init__(*args,**kwargs)
        
    def db_type(self):
        return "CIDR"
        
    def to_python(self,value):
        return str(value)
        
    def get_db_prep_value(self,value):
        # Convert value to pure network address to prevent
        # PostgreSQL exception
        return normalize_prefix(value)
##
## INETField maps to PostgreSQL INET Field
##
class INETField(models.Field):
    def db_type(self):
        return "INET"
    
    def to_python(self,value):
        return str(value)
    
    def get_db_prep_value(self,value):
        if not value:
            return None
        return value
##
## Binary Field maps to PostgreSQL BYTEA
##
class BinaryField(models.Field):
    def db_type(self):
        return "BYTEA"
##
## Text Array field maps to PostgreSQL TEXT[] type
##
class TextArrayField(models.Field):
    __metaclass__ = models.SubfieldBase
    
    def db_type(self):
        return "TEXT[]"

    def to_python(self,value):
        def to_unicode(s):
            if type(s)==types.UnicodeType:
                return s
            else:
                return unicode(s,"utf-8")
        return [to_unicode(x) for x in value]
##
## INETArrayField maps to PostgreSQL INET[] type
##
class InetArrayField(models.Field):
    __metaclass__ = models.SubfieldBase
    def db_type(self):
        return "INET[]"

    def to_python(self,value):
        if type(value)==types.ListType:
            return value
        if value=="{}":
            return []
        return value[1:-1].split(",")
        
    def get_db_prep_value(self,value):
        return "{ "+", ".join(value)+" }"
        

##
## Pickled object
##
class PickledField(models.Field):
    __metaclass__ = models.SubfieldBase
    def db_type(self):
        return "TEXT"
    def to_python(self,value):
        if not value:
            return None
        try:
            return cPickle.loads(str(value))
        except:
            return value
    def get_db_prep_value(self,value):
        return cPickle.dumps(value)
