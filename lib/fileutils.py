# -*- coding: utf-8 -*-
##----------------------------------------------------------------------
## Copyright (C) 2007-2011 The NOC Project
## See LICENSE for details
##----------------------------------------------------------------------

## Python modules
from __future__ import with_statement
import os
import tempfile
import hashlib
import urllib2
import cStringIO
import gzip
## NOC modules
from noc.lib.version import get_version
from noc.settings import config

## Setup proxy
PROXY = {}
for proto in ["http", "https", "ftp"]:
    p = config.get("proxy", "%s_proxy" % proto)
    if p:
        PROXY[proto] = p
if PROXY:
    ph = urllib2.ProxyHandler(PROXY)
    opener = urllib2.build_opener(ph)
    urllib2.install_opener(opener)


def safe_rewrite(path, text, mode=None):
    """
    Create new file filled with "text" safely
    """
    if isinstance(text, unicode):
        text = text.encode("utf-8")
    d = os.path.dirname(path)
    if d and not os.path.exists(d):
        os.makedirs(d)
    b = os.path.basename(path)
    h, p = tempfile.mkstemp(suffix=".tmp", prefix=b, dir=d)
    f = os.fdopen(h, "w")
    f.write(text)
    f.close()
    if os.path.exists(path):
        os.unlink(path)
    os.link(p, path)
    os.unlink(p)
    if mode:
        os.chmod(path, mode)


def is_differ(path, content):
    """
    Check file content is differ from string
    """
    if os.path.isfile(path):
        with open(path) as f:
            cs1 = hashlib.sha1(f.read()).digest()
        cs2 = hashlib.sha1(content).digest()
        return cs1 != cs2
    else:
        return True


def rewrite_when_differ(path, content):
    """
    Rewrites file when content is differ
    Returns boolean signalling wherher file was rewritten
    """
    d = is_differ(path, content)
    if d:
        safe_rewrite(path, content)
    return d


def read_file(path):
    """
    Read file and return file's content.
    Return None when file does not exists
    """
    if os.path.isfile(path) and os.access(path, os.R_OK):
        with open(path, "r") as f:
            return f.read()
    else:
        return None


def copy_file(f, t, mode=None):
    """
    Copy File
    """
    d = read_file(f)
    if d is None:
        d = ""
    safe_rewrite(t, d, mode=mode)


def write_tempfile(text):
    """
    Create temporary file, write content and return path
    """
    h, p = tempfile.mkstemp()
    f = os.fdopen(h, "w")
    f.write(text)
    f.close()
    return p


class temporary_file(object):
    """
    Temporary file context manager.
    Writes data to temporary file an returns path.
    Unlinks temporary file on exit
    USAGE:
         with temporary_file("line1\nline2") as p:
             subprocess.Popen(["wc","-l",p])
    """
    def __init__(self, text=""):
        self.text = text

    def __enter__(self):
        self.p = write_tempfile(self.text)
        return self.p

    def __exit__(self, type, value, tb):
        os.unlink(self.p)


def in_dir(file, dir):
    """
    Check file is inside dir
    """
    return os.path.commonprefix([dir, os.path.normpath(file)]) == dir


def urlopen(url, auto_deflate=False):
    """
    urlopen wrapper
    """
    global PROXY

    if url.startswith("http://") or url.startswith("https://"):
        r = urllib2.Request(
            url, headers={"User-Agent": "NOC/%s" % get_version()})
    else:
        r = url
    if auto_deflate and url.endswith(".gz"):
        u = urllib2.urlopen(r)
        f = cStringIO.StringIO(u.read())
        return gzip.GzipFile(fileobj=f)
    else:
        return urllib2.urlopen(r)


def search_path(file):
    """
    Search for executable file in $PATH
    :param file: File name
    :return: path or None
    :rtype: str or None
    """
    if os.path.exists(file):
        return file  # Found
    for d in os.environ["PATH"].split(os.pathsep):
        f = os.path.join(d, file)
        if os.path.exists(f):
            return f
    return None


def tail(path, lines):
    """
    Return string containing last lines of file
    :param lines:
    :return:
    """
    with open(path) as f:
        avg = 74
        while True:
            try:
                f.seek(-avg * lines, 2)
            except IOError:
                f.seek(0)
            pos = f.tell()
            l = f.read().splitlines()
            if len(l) >= lines or not pos:
                return l[-lines:]
            avg *= 1.61
