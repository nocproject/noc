# -*- coding: utf-8 -*-
##----------------------------------------------------------------------
## RefBook Downloaders
## Downloader is a class performing download and parsing of refbook
## And returning a list of hashes (for RefBook.bulk_upload)
##----------------------------------------------------------------------
## Copyright (C) 2007-2009 The NOC Project
## See LICENSE for details
##----------------------------------------------------------------------
"""
"""
from noc.lib.registry import Registry
##
## Downloader registry
##
class DownloaderRegistry(Registry):
    name="DownloaderRegistry"
    subdir="refbooks/downloaders"
    classname="Downloader"
    apps=["noc.main"]
downloader_registry=DownloaderRegistry()
##
## Metaclass for refbook downloaders
##
class DownloaderBase(type):
    def __new__(cls,name,bases,attrs):
        m=type.__new__(cls,name,bases,attrs)
        m.scripts={}
        downloader_registry.register(m.name,m)
        return m
##
## Downloader base class
##
class Downloader(object):
    __metaclass__=DownloaderBase
    # Profile name
    name=None
    ##
    ## Abstract metrod returning a list of records
    ## Each record is a hash with field name -> value mapping
    ##
    @classmethod
    def download(cls,ref_book):
        return []
