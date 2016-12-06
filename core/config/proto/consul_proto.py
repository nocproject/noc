# -*- coding: utf-8 -*-
##----------------------------------------------------------------------
## Load config from consul
##----------------------------------------------------------------------
## Copyright (C) 2007-2016 The NOC Project
## See LICENSE for details
##----------------------------------------------------------------------

## Python modules
import urlparse
import errno
## Third-party modules
import pycurl
import six
import ujson
## NOC modules
from base import BaseProtocol


class ConsulProtocol(BaseProtocol):
    """
    Environment variables mapping
    URL:
        consul:///<ip1>,...,<ipN>/<path>
    """
    DEFAULT_PORT = 8500
    REQUEST_TIMEOUT = 30
    CONNECT_TIMEOUT = 30

    RETRY_SOCKET_ERRORS = (
        errno.ECONNREFUSED, errno.EHOSTDOWN,
        errno.EHOSTUNREACH, errno.ENETUNREACH)

    RETRY_CURL_ERRORS = set([
        pycurl.E_COULDNT_CONNECT,
        pycurl.E_OPERATION_TIMEDOUT,
        pycurl.E_RECV_ERROR
    ])

    def __init__(self, config, url):
        super(ConsulProtocol, self).__init__(config, url)
        c = urlparse.urlparse(url)
        self.hosts = []
        for x in c.netloc.split(","):
            if ":" in x:
                self.hosts += [x]
            else:
                self.hosts += ["%s:%s" % (x, self.DEFAULT_PORT)]
        self.path = c.path

    def _get(self, path):
        """
        Perform HTTP get
        :param url:
        :return:
        """
        buff = six.StringIO()
        for host in self.hosts:
            url = "http://%s%s" % (host, path)
            c = pycurl.Curl()
            c.setopt(c.URL, url)
            c.setopt(c.WRITEDATA, buff)
            c.setopt(c.NOPROXY, "*")
            c.setopt(c.TIMEOUT, self.REQUEST_TIMEOUT)
            c.setopt(c.CONNECTTIMEOUT, self.CONNECT_TIMEOUT)
            c.setopt(c.TCP_KEEPALIVE, 1)
            c.setopt(c.TCP_KEEPIDLE, 60)
            c.setopt(c.TCP_KEEPINTVL, 60)
            try:
                c.perform()
                return ujson.loads(buff.getvalue())
            except pycurl.error as e:
                errno, errstr = e
                if errno in self.RETRY_CURL_ERRORS:
                    continue
                break
            finally:
                c.close()
        return None

    def load(self):
        r = self._get("/v1/kv%s?recurse" % self.path)
        if not r:
            raise ValueError("Cannot get config")
        # Convert to dict
        data = {}
        if self.path.endswith("/"):
            pl = len(self.path) - 1
        else:
            pl = len(self.path)
        for i in r:
            if not i.get("Value"):
                continue
            k = i["Key"][pl:]
            v = i["Value"].decode("base64")
            if k.count("/") == 0:
                data[k.replace("/", ".")] = v
            elif k.count("/") == 1:
                d = k.split("/")
                data.update({
                    d[0]: {
                        d[1]: v
                    }
                })
        # Upload to config
        for name in self.config:
            c = data
            parts = name.split(".")
            for n in parts[:-1]:
                if n in c and isinstance(c[n], dict):
                    c = c[n]
                else:
                    c = None
                    break
            if c and parts[-1] in c:
                self.config.set_parameter(name, c[parts[-1]])

    def dump(self):
        raise NotImplementedError
