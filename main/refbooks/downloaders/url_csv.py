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
import csv,gzip,cStringIO
from noc.lib.fileutils import urlopen
##
## Download reference book from CSV file
## First line of CSV file is field names
##
class Downloader(DownloaderBase):
    name="CSV"
    @classmethod
    def download(cls,ref_book):
        out=[]
        # Fetch data into StringIO wrapper
        f=urlopen(ref_book.download_url)
        data=cStringIO.StringIO(f.read())
        f.close()
        # Wrap GzipFile for gzipped content
        if ref_book.download_url.endswith(".gz"):
            data=gzip.GzipFile(fileobj=data)
        # Iterate through CSV
        reader=csv.reader(data)
        header={}
        for row in reader:
            if not row:
                continue
            if not header:
                # Read field names from first line
                for i,h in enumerate(row):
                    header[i]=unicode(h,"utf8","ignore")
                continue
            r={}
            for i,v in enumerate(row):
                r[header[i]]=unicode(v,"utf8","ignore")
            out.append(r)
        return out
