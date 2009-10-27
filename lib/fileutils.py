# -*- coding: utf-8 -*-
##----------------------------------------------------------------------
## Copyright (C) 2007-2009 The NOC Project
## See LICENSE for details
##----------------------------------------------------------------------
import os,tempfile,hashlib,urllib2,cStringIO,gzip
from noc.lib.version import get_version
##
## Create new file filled with "text" safely
##
def safe_rewrite(path,text,mode=None):
    d=os.path.dirname(path)
    if d and not os.path.exists(d):
        os.makedirs(d)
    b=os.path.basename(path)
    h,p=tempfile.mkstemp(suffix=".tmp",prefix=b,dir=d)
    f=os.fdopen(h,"w")
    f.write(text)
    f.close()
    if os.path.exists(path):
        os.unlink(path)
    os.link(p,path)
    os.unlink(p)
    if mode:
        os.chmod(path,mode)
##
## Check file content is differ from string
##
def is_differ(path,content):
    if os.path.isfile(path):
        f=open(path)
        cs1=hashlib.sha1(f.read()).digest()
        f.close()
        cs2=hashlib.sha1(content).digest()
        return cs1!=cs2
    else:
        return True
##
## Rewrites file when content is differ
## Returns boolean signalling wherher file was rewritten
##
def rewrite_when_differ(path,content):
    d=is_differ(path,content)
    if d:
        safe_rewrite(path,content)
    return d
##
## Read file and return file's content.
## Return None when file does not exists
##
def read_file(path):
    if os.path.exists(path):
        f=open(path,"r")
        data=f.read()
        f.close()
        return data
    else:
        return None
##
## Copy File
##
def copy_file(f,t):
    d=read_file(f)
    if d is None:
        d=""
    safe_rewrite(t,d)
##
## Create temporary file, write content and return path
##
def write_tempfile(text):
    h,p=tempfile.mkstemp()
    f=os.fdopen(h,"w")
    f.write(text)
    f.close()
    return p
##
## Temporary file context manager.
## Writes data to temporary file an returns path.
## Unlinks temporary file on exit
## USAGE:
##     with temporary_file("line1\nline2") as p:
##         subprocess.Popen(["wc","-l",p])
##
class temporary_file(object):
    def __init__(self,text):
        self.text=text
    def __enter__(self):
        self.p=write_tempfile(self.text)
        return self.p
    def __exit__(self, type, value, tb):
        os.unlink(self.p)
##
## Check file is inside dir
##
def in_dir(file,dir):
    return os.path.commonprefix([dir,os.path.normpath(file)])==dir
##
## urlopen wrapper
##
def urlopen(url,auto_deflate=False):
    if url.startswith("http://") or url.startswith("https://"):
        r=urllib2.Request(url,headers={"User-Agent":"NOC/%s"%get_version()})
    else:
        r=url
    if auto_deflate and url.endswith(".gz"):
        f=cStringIO.StringIO(urllib2.urlopen(r).read())
        return gzip.GzipFile(fileobj=f)
    else:
        return urllib2.urlopen(r)
