# -*- coding: utf-8 -*-
##----------------------------------------------------------------------
## Built-in refbooks
##----------------------------------------------------------------------
## Copyright (C) 2007-2009 The NOC Project
## See LICENSE for details
##----------------------------------------------------------------------
"""
"""
from noc.main.models import RefBook as RB
from noc.main.models import RefBookField,Language
##
lang_cache={}
def get_language(name):
    global lang_cache
    if name not in lang_cache:
        l=Language.objects.get(name=name)
        lang_cache[name]=l
    return lang_cache[name]
##
## RefBook descruiption base
##
class RefBook(object):
    name=None
    language="English"
    description=""
    downloader=None
    download_url=None
    refresh_interval=30
    fields=[]
    ##
    ## Syncronization
    ##
    @classmethod
    def sync(cls):
        # Sync Refbook
        try:
            rb=RB.objects.get(name=cls.name)
            rb.description=cls.description
            rb.language=get_language(cls.language)
            rb.refresh_interval=cls.refresh_interval
            rb.downloader=cls.downloader
            rb.download_url=cls.download_url
            rb.is_builtin=True
            print "UPDATE RefBook ",cls.name
        except RB.DoesNotExist:
            rb=RB(
                name=cls.name,
                description=cls.description,
                language=get_language(cls.language),
                refresh_interval=cls.refresh_interval,
                downloader=cls.downloader,
                download_url=cls.download_url,
                is_builtin=True,
                is_enabled=False
            )
            print "CREATE RefBook ",cls.name
        rb.save()
        # Sync Fields
        es=set()
        for f in rb.refbookfield_set.all():
            es.add(f.name)
        ns=set()
        for f in cls.fields:
            ns.add(unicode(f.name,"utf-8"))
        if es!=ns:
            print "Recreating fields"
            rb.flush_refbook()
            rb.refbookfield_set.all().delete()
            idx=1
            for f in cls.fields:
                RefBookField(ref_book=rb,name=f.name,order=idx,is_required=f.is_required,description=f.description,search_method=f.search_method).save()
                idx+=1
        else:
            # Update descriptions and search methods
            for f in cls.fields:
                field=RefBookField.objects.get(ref_book=rb,name=f.name)
                field.description=f.description
                field.search_method=f.search_method
                field.save()

##
## RefBook fields
##
class Field(object):
    def __init__(self,name,description=None,is_required=True,search_method=None):
        self.name=name
        self.description=description
        self.is_required=is_required
        self.search_method=search_method

