# -*- coding: utf-8 -*-
##----------------------------------------------------------------------
## Search engine with plugin support
##----------------------------------------------------------------------
## Copyright (C) 2007-2009 The NOC Project
## See LICENSE for details
##----------------------------------------------------------------------
"""
"""
from django.db.models.signals import class_prepared
##
## A hash of Model.search classmethods.
## Populated by "class_prepared" signal listener
## Model.search is a generator taking parameters (user,query,limit)
## And yielding a SearchResults (ordered by relevancy)
##
search_methods={}

##
## Register new search handler if model has .search classmethod
##
def on_new_model(sender,**kwargs):
    if hasattr(sender,"search"):
        search_methods[getattr(sender,"search")]=None

##
## Attach to the 'class_prepared' signal
## and on_new_model on every new model
##
class_prepared.connect(on_new_model)

##
## Wrapper for search results
##
class SearchResult(object):
    def __init__(self,url,title,text,relevancy=1.0):
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
