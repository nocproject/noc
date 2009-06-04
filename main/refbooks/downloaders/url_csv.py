# -*- coding: utf-8 -*-
##----------------------------------------------------------------------
## CSV-file downloader
## First line is a field names
##----------------------------------------------------------------------
## Copyright (C) 2007-2009 The NOC Project
## See LICENSE for details
##----------------------------------------------------------------------
"""
"""
from noc.main.refbooks.downloaders import Downloader as DownloaderBase
import urllib2,csv
##
##
##
class Downloader(DownloaderBase):
    name="CSV"
    @classmethod
    def download(cls,ref_book):
        out=[]
        f=urllib2.urlopen(ref_book.download_url)
        reader=csv.reader(f)
        header={}
        for row in reader:
            if not row:
                continue
            if not header:
                # Read first line
                for i,h in enumerate(row):
                    header[i]=h
                continue
            r={}
            for i,v in enumerate(row):
                r[header[i]]=v
            out.append(r)
        f.close()
        return out
