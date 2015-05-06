# -*- coding: utf-8 -*-
##----------------------------------------------------------------------
## HTTP provider
##----------------------------------------------------------------------
## Copyright (C) 2007-2011 The NOC Project
## See LICENSE for details
##----------------------------------------------------------------------

## Python modules
import random
import urllib
import base64
import hashlib
import socket
import types
import Queue
## NOC modules
from noc.lib.nbsocket import ConnectedTCPSocket
from noc.lib.version import get_version


class HTTPError(Exception):
    """
    HTTP Error exception wrapper
    """
    def __init__(self, code, msg=None):
        self.code = code
        if msg is None:
            msg = "HTTP Error: %s" % code
        super(HTTPError, self).__init__(msg)


class HTTPResponse(object):
    def __init__(self, response):
        self.headers = {}
        self.status = None
        self.reason = None
        self.data = None
        if response:
            self.parse_headers(response) and self.parse_data(response)
        else:
            self.reason = "Request failed. No data"

    def parse_headers(self, response):
        """
        Parse response and set status and headers

        @todo: Properly parse multi-line headers

        :param response: Raw response
        :type response: Str
        :returns: True if headers parsed properly, else False
        :rtype: Bool
        """
        # Parse status
        h, _ = response.split("\r\n\r\n", 1)
        l = h.splitlines()
        version, status, self.reason = l[0].split(" ", 2)
        self.status = int(status)
        if version != "HTTP/1.0" and version != "HTTP/1.1":
            self.status = None
            self.reason = "Invalid HTTP version: %s" % version
            return False
        # Parse headers
        headers = [x.split(":", 1) for x in l[1:]]
        self.headers = dict([(x[0].strip().lower(), x[1].strip())
                             for x in headers])
        return True

    def parse_data(self, response):
        _, d = response.split("\r\n\r\n", 1)
        if "transfer-encoding" in self.headers:
            self.data = self.decode_encoding(self.headers["transfer-encoding"],
                                             d)
        else:
            self.data = d
        return True

    def decode_encoding(self, encoding, data):
        if encoding == "chunked":
            return self.decode_chunked(data)
        else:
            self.status = None
            self.reason = "Unsupported encoding: %s" % encoding
            return None

    def decode_chunked(self, data):
        r = []
        while data:
            l, data = data.split("\r\n", 1)
            l = int(l, 16)
            if not l:
                break
            r += [data[:l]]
            data = data[l + 2:]
        return "".join(r)


class NOCHTTPSocket(ConnectedTCPSocket):
    """
    HTTP Connection
    """
    TTL = 30

    def __init__(self, parent, address, port):
        self.buffer = ""
        self.queue = Queue.Queue()
        super(NOCHTTPSocket, self).__init__(parent.script.activator.factory,
                                            address, port)

    def on_read(self, data):
        self.buffer += data

    def on_conn_refused(self):
        pass

    def on_close(self):
        self.queue.put(HTTPResponse(self.buffer))

    def request(self, method, path, params=None, headers={}):
        # Build request
        headers = headers.copy()
        h_keys = set([k.lower() for k in headers])
        if "host" not in headers:
            headers["Host"] = self.address
        headers["Connection"] = "close"
        if "user-agent" not in headers:
            headers["User-Agent"] = "NOC/%s" % get_version()
        r = "%s %s HTTP/1.1\r\n" % (method, path)
        r += "\r\n".join(["%s: %s" % (k, v) for k, v in headers.items()])
        r += "\r\n\r\n"
        self.write(r)
        return self.queue.get(block=True)


class HTTPProvider(object):
    """
    HTTP Provider
    """
    HTTPError = HTTPError

    def __init__(self, script):
        self.script = script
        self.access_profile = script.access_profile
        self.authorization = None

    def debug(self, msg):
        self.script.debug("HTTP: %s" % msg)

    def request(self, method, path, params=None, headers={}):
        if self.authorization:
            headers["Authorization"] = self.authorization
        self.debug("%s %s %s %s" % (method, path, params, headers))
        s = NOCHTTPSocket(self,
                self.access_profile.address,
                int(self.access_profile.port) if self.access_profile.port
                                              else 80)
        try:
            response = s.request(method, path, params, headers)
            if response.status == 200:
                return response.data
            elif (response.status == 401 and
                  self.authorization is None and
                  "www-authenticate" in response.headers):
                self.set_authorization(response.headers["www-authenticate"],
                                       method, path)
                return self.request(method, path, params, headers)
            elif response.status is None:
                raise self.HTTPError(response.reason)
            else:
                raise self.HTTPError(response.status)
        finally:
            s.close()

    def set_authorization(self, auth, method, path):
        scheme, data = auth.split(" ", 1)
        scheme = scheme.lower()
        d = {}
        for s in data.split(","):
            s = s.strip()
            if "=" in s:
                k, v = s.split("=", 1)
                if v.startswith("\"") and v.endswith("\""):
                    v = v[1:-1]
                d[k] = v
            else:
                d[s] = None
        if scheme == "basic":
            self.authorization = "Basic %s" % base64.b64encode(
                "%s:%s" % (self.access_profile.user,
                           self.access_profile.password)).strip()
        elif scheme == "digest":
            H = lambda x: hashlib.md5(x).hexdigest()
            KD = lambda x, y: H("%s:%s" % (x, y))
            A1 = "%s:%s:%s" % (self.access_profile.user, d["realm"],
                               self.access_profile.password)
            A2 = "%s:%s" % (method, path)
            f = {
                "username": self.access_profile.user,
                "realm"   : d["realm"],
                "nonce"   : d["nonce"],
                "uri"     : path,
            }
            if "qop" not in d:
                noncebit = "%s:%s" % (d["nonce"], H(A2))
            elif d["qop"] == "auth":
                nc = "00000001"
                cnonce = H(str(random.random()))
                f["nc"] = nc
                f["cnonce"] = cnonce
                f["qop"] = d["qop"]
                noncebit = "%s:%s:%s:%s:%s" % (d["nonce"], nc, cnonce,
                                               d["qop"], H(A2))
            else:
                raise Exception("qop not supported: %s" % d["qop"])
            f["response"] = KD(H(A1), noncebit)
            self.authorization = "Digest " + ", ".join(["%s=\"%s\"" % (k, v)
                                                        for k, v in f.items()])
        else:
            raise Exception("Unknown auth method: %s" % scheme)

    def get(self, path, params=None, headers={}):
        """
        Perform GET request. Path can be given as string or a list of strings.
        If list of strings given, try first element, in case of 404 pass
        to next

        :param path: Path or list of paths
        :type path: String or List of string
        """
        to_save = self.script.activator.to_save_output
        if self.script.activator.use_canned_session:
            r = self.script.activator.http_get(path)
            if isinstance(r, basestring):
                return r
            else:
                raise HTTPError(r)

        if type(path) in (types.ListType, types.TupleType):
            last_code = None
            for p in path:
                try:
                    return self.get(p, params, headers)
                except self.HTTPError, e:
                    last_code = e.code
                    if last_code == 404:
                        continue
                    else:
                        break
            if to_save:
                self.script.activator.save_http_get(path, last_code)
            raise self.HTTPError(last_code)
        else:
            try:
                r = self.request("GET", path, params, headers)
            except socket.error, why:
                raise self.script.LoginError(why[1])
            if to_save:
                self.script.activator.save_http_get(path, r)
            return r

    def post(self, path, params=None, headers={}):
        if params:
            params = urllib.urlencode(params)
            headers["Content-Type"] = "application/x-www-form-urlencoded"
        try:
            return self.request("POST", path, params, headers)
        except socket.error, why:
            raise self.script.LoginError(why[1])
