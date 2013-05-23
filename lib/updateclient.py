# -*- coding: utf-8 -*-
##----------------------------------------------------------------------
## Remote daemon's update client
##----------------------------------------------------------------------
## Copyright (C) 2007-2012 The NOC Project
## See LICENSE for details
##----------------------------------------------------------------------

## Python modules
import os
import hashlib
import urllib2
import urllib
import logging
import tempfile
## NOC modules
from noc.lib.serialize import json_encode, json_decode


class UpdateClient(object):
    class ManifestNotFound(Exception):
        pass

    def __init__(self, url, names):
        self.url = url + "main/update/"
        self.manifest = {}
        # Load manifests
        self.names = names
        self.debug("Loading manifests")
        for name in self.names:
            self.load_manifest(name)

    def error(self, msg):
        logging.error("[UpdateClient] %s" % msg)

    def info(self, msg):
        logging.info("[UpdateClient] %s" % msg)

    def debug(self, msg):
        logging.debug("[UpdateClient] %s" % msg)

    def load_manifest(self, name):
        """
        Load manifest "name" into self.manifests
        :param name: manifest name
        :return:
        """
        dmfn = "etc/manifests/%s.defaults" % name
        mfn = "etc/manifests/%s.conf" % name

        # Find manifest
        if os.path.isfile(mfn):
            self.info("Loading manifest for %s" % name)
            fn = mfn
        elif os.path.isfile(dmfn):
            self.info("Loading default for %s" % name)
            fn = dmfn
        else:
            self.error("Manifest not found: %s" % name)
            raise self.ManifestNotFound(
                "Manifest not found: %s" % name)
        # Load manifest
        with open(fn) as f:
            for l in f:
                l = l.strip()
                if not l or l.startswith("#"):
                    continue
                if l.endswith("/"):
                    # Directory
                    for root, dirs, files in os.walk(l):
                        for df in files:
                            if (df.endswith(".pyc") or
                                    df.endswith(".pyo") or
                                    df.startswith(".") or
                                    df.endswith(".orig")):
                                continue
                            self.update_manifest(os.path.join(root, df))
                else:
                    self.update_manifest(l)

    def get_hash(self, path):
        """
        Calculate file hash. Return None if file is not found
        :param path: File path
        :return: hash of None
        """
        if not os.path.isfile(path):
            return None
        with open(path) as f:
            return hashlib.sha1(f.read()).hexdigest()

    def update_manifest(self, path):
        """
        Update manifest for single file
        :param path: File path
        :return:
        """
        if path in self.manifest:
            return
        self.manifest[path] = self.get_hash(path)

    def get_request_data(self):
        return json_encode(self.manifest.items())

    def write_file(self, path, data):
        """
        Create new file filled with "text" safely
        """
        d = os.path.dirname(path)
        if d and not os.path.exists(d):
            os.makedirs(d)
        b = os.path.basename(path)
        h, p = tempfile.mkstemp(suffix=".tmp", prefix=b, dir=d)
        f = os.fdopen(h, "w")
        f.write(data)
        f.close()
        if os.path.exists(path):
            os.unlink(path)
        os.link(p, path)
        os.unlink(p)

    def request_update(self):
        """
        Request updates from server
        :return:
        """
        # Request data
        self.info("Requesting updates")
        uri = "%s?%s" % (
            self.url,
            "&".join("name=%s" % urllib.quote(n) for n in self.names))
        self.debug("GET %s" % uri)
        try:
            f = urllib2.urlopen(
                uri, data=self.get_request_data(), timeout=60)
            data = json_decode(f.read())
            f.close()
        except urllib2.URLError, why:
            self.error("Failed to get updates: %s" % why)
            return False
        for path, hash, value in data:
            if hash:
                # Replace file
                self.debug("Replacing %s [%s]" % (path, hash))
                self.write_file(path, value)
            else:
                # Delete files
                self.debug("Deleting %s" % path)
                if os.path.exists(path):
                    os.unlink(path)
        if data:
            self.info("System has been updated")
        else:
            self.info("System is up to date")
        return bool(data)
