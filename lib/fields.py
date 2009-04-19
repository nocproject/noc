# -*- coding: utf-8 -*-
##----------------------------------------------------------------------
## Custom field types
##----------------------------------------------------------------------
## Copyright (C) 2007-2009 The NOC Project
## See LICENSE for details
##----------------------------------------------------------------------
from django.db import models
from lib.ip import normalize_prefix
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
## Binary Field maps to PostgreSQL BYTEA
##
class BinaryField(models.Field):
    def db_type(self):
        return "BYTEA"
