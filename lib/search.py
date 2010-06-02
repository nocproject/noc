# -*- coding: utf-8 -*-
##----------------------------------------------------------------------
## Search engine with plugin support
##----------------------------------------------------------------------
## Copyright (C) 2007-2009 The NOC Project
## See LICENSE for details
##----------------------------------------------------------------------
"""
"""
from noc.lib.app import site
from noc.main.models import search_methods
import types
##
## Wrapper for search results
##
class SearchResult(object):
    def __init__(self,url,title,text,relevancy=1.0):
        if type(url) in [types.TupleType,types.ListType]:
            self.url=site.reverse(*url)
        else:
            self.url=url
        self.title=title
        self.text=text
        self.relevancy=relevancy
    
    def __cmp__(self,other):
        return cmp(other.relevancy,self.relevancy)
##
## Interface to built-in search system
##
def search(user,query,limit=100):
    r=[]
    for sm in search_methods:
        r+=list(sm(user,query,limit))
    return sorted(r)[:limit]
