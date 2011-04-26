# -*- coding: utf-8 -*-
##----------------------------------------------------------------------
## Various database utilities
##----------------------------------------------------------------------
## Copyright (C) 2007-2011 The NOC Project
## See LICENSE for details
##----------------------------------------------------------------------

## Django modules
from django.utils import tree
from django.db.models import Q


class SQLExpression(object):
    def __init__(self, sql):
        self.sql = sql
    
    def as_sql(self, qn, connection):
        return "(%s)" % self.sql, []
    

class SQLNode(tree.Node):
    def __init__(self, sql):
        super(SQLNode, self).__init__()
        self.sql = sql
    
    def __deepcopy__(self, memodict):
        obj = super(SQLNode, self).__deepcopy__(memodict)
        obj.sql = self.sql
        return obj
    
    def add_to_query(self, query, aliases):
        query.where.add(SQLExpression(self.sql), self.connector)
    

def SQL(sql):
    """
    Q-style wrapper for SQL statement. Can be used in queryset
    together with Q
    """
    return Q(SQLNode(sql))
