# -*- coding: utf-8 -*-
##----------------------------------------------------------------------
## URL Processing functions
##----------------------------------------------------------------------
## Copyright (C) 2007-2009 The NOC Project
## See LICENSE for details
##----------------------------------------------------------------------
import re,urllib

rx_url=re.compile(r"^(?P<scheme>[^:]+)://(?:(?P<user>[^:]+):(?P<password>[^@]+)@)(?P<host>[^/:]+)(?::(?P<port>\d+))?(?P<path>.*)$")

class InvalidURLException(Exception): pass

class URL(object):
    def __init__(self,url):
        self.url=url
        match=rx_url.match(self.url)
        if not match:
            raise InvalidURLException
        self.scheme=match.group("scheme")
        self.user=urllib.unquote(match.group("user"))
        self.password=urllib.unquote(match.group("password"))
        self.host=match.group("host")
        if match.group("port"):
            self.port=int(match.group("port"))
        else:
            self.port=None
        self.path=match.group("path")
