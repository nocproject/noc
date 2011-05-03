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
import httplib
import base64
import hashlib
import socket
import types
import Queue
## NOC modules
from noc.lib.nbsocket import ConnectedTCPSocket


class HTTPError(Exception):
    """
    HTTP Error exception wrapper
    """
    def __init__(self, code, msg=None):
        self.code = code
        if msg is None:
            msg = "HTTP Error: %s" % code
        super(HTTPError, self).__init__(msg)


class NOCHTTPSocketFileWrapper(object):
    def __init__(self, socket):
        self.socket = socket

    def readline(self):
        return self.socket.readline()
    
    def read(self, size=None):
        return self.socket.read(size)

    def close(self):
        return self.socket.close()


class NOCHTTPSocket(ConnectedTCPSocket):
    """
    Wrap ConnectedTCPSocket to use into
    httplib.HTTPConnection
    """
    def __init__(self, factory, address, port, queue):
        self.queue = queue
        self.read_queue = Queue.Queue()
        self.buffer = ""
        super(NOCHTTPSocket, self).__init__(factory, address, port)

    def on_connect(self):
        self.queue.put(True)

    def on_conn_refused(self):
        self.queue.put(False)

    def on_close(self):
        self.queue.put(False)
        self.read_queue.put(None)

    def on_read(self, data):
        self.buffer += data
        self.read_queue.put(None)

    def sendall(self, msg):
        self.write(msg)

    def makefile(self, mode, buffsize):
        return NOCHTTPSocketFileWrapper(self)

    def readline(self):
        while True:
            idx = self.buffer.find("\n")
            if idx >= 0:
                data, self.buffer = self.buffer[:idx], self.buffer[idx:]
                return data
            if not self.socket_is_ready():
                raise HTTPError("Broken pipe")
            self.read_queue.get(block=True)
    
    def read(self, size=None):
        while True:
            if self.buffer:
                if size is None:
                    data, self.buffer = self.buffer, ""
                    return data
                elif len(self.buffer) >= size:
                    data, self.buffer = self.buffer[:size], self.buffer[size:]
            if not self.socket_is_ready():
                return ""
            self.read_queue.get(block=True)


class NOCHTTPConnection(httplib.HTTPConnection):
    def __init__(self, parent, address, port):
        self.parent = parent
        self.queue = Queue.Queue()
        httplib.HTTPConnection.__init__(self, address, port)
        #super(NOCHTTPConnection, self).__init__(address, port)

    def connect(self):
        """
        Override standard connect method
        """
        self.sock = NOCHTTPSocket(self.parent.script.activator.factory,
                                  self.host, self.port, self.queue)
        # Wait for socket to connect
        if not self.queue.get(block=True):
            raise HTTPError("Connection timed out")


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
        conn = NOCHTTPConnection(self,
                self.access_profile.address,
                int(self.access_profile.port) if self.access_profile.port
                                              else 80)
        conn.request(method, path, params, headers)
        response = conn.getresponse()
        try:
            if response.status == 200:
                return response.read()
            elif response.status == 401 and self.authorization is None:
                self.set_authorization(response.getheader("www-authenticate"),
                                       method, path)
                return self.request(method, path, params, headers)
            else:
                raise self.HTTPError(response.status)
        finally:
            conn.close()

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
            raise self.HTTPError(last_code)
        else:
            try:
                return self.request("GET", path)
            except socket.error, why:
                raise self.script.LoginError(why[1])

    def post(self, path, params=None, headers={}):
        if params:
            params = urllib.urlencode(params)
            headers["Content-Type"] = "application/x-www-form-urlencoded"
        try:
            return self.request("POST", path, params, headers)
        except socket.error, why:
            raise self.script.LoginError(why[1])
