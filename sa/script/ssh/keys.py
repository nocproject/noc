# -*- coding: utf-8 -*-
##----------------------------------------------------------------------
## SSH Key Management
## Based upon twisted.conch.ssh code
##----------------------------------------------------------------------
## Copyright (C) 2007-2011 The NOC Project
## See LICENSE for details
##----------------------------------------------------------------------

from __future__ import with_statement
## Python modules
import os
import base64
from hashlib import sha1, sha256
## Third-party modules
from Crypto.PublicKey import RSA, DSA
from ecdsa import SigningKey, VerifyingKey, curves
## NOC modules
from noc.sa.script.ssh.util import *
from noc.lib.fileutils import read_file, safe_rewrite

##
##
##
class Key(object):
    def __init__(self, key, ssh_type=None):
        self.key = key
        self._ssh_type = ssh_type
    
    @classmethod
    def generate(cls, type, bits):
        """
        Return new generated key
        """
        if type == "RSA":
            k = RSA
        elif type == "DSA":
            k = DSA
        else:
            raise ValueError("Invalid key type")
        return cls(k.generate(bits, secure_random))
    
    @classmethod
    def from_file(cls, path):
        """
        Load key from file. Returns Key instance
        """
        return cls.from_string(read_file(path))
    
    @classmethod
    def guess_key_type(cls, data):
        """
        Try to guess key type. Returns string with key type or None
        """
        if data.startswith("ssh-"):
            return "public_openssh"
        elif data.startswith("-----BEGIN"):
            return "private_openssh"
        #elif data.startswith("{"):
        #    return "public_lsh"
        #elif data.startswith("("):
        #    return "private_lsh"
        elif data.startswith("\x00\x00\x00\x07ssh-"):
            ignored, rest = get_NS(data, 1)
            count = 0
            while rest:
                count += 1
                ignored, rest = get_MP(rest)
            if count > 4:
                return "agentv3"
            else:
                return "blob"
        elif data.startswith("\x00\x00\x00\x13ecdsa-"):
            return "blob"
    
    @classmethod
    def from_string(cls, data, type=None):
        """
        Create key instance from string
        """
        if type is None:
            type = cls.guess_key_type(data)
        if type is None:
            raise RuntimeError("Cannot guess key type for: %r" % data)
        method = getattr(cls, "from_string_%s" % type.lower(), None)
        if method is None:
            raise ValueError("Key type '%s' is not supported" % type)
        return method(data)
    
    @classmethod
    def from_string_blob(cls, data):
        """
        Parse blob string key
        """
        key_type, rest = get_NS(data, 1)
        if key_type == "ssh-rsa":
            e, n, rest = get_MP(rest, 2)
            return cls(RSA.construct((n, e)))
        elif key_type == "ssh-dss":
            p, q, g, y, rest = get_MP(rest, 4)
            return cls(DSA.construct((y, g, p, q)))
        elif key_type == "ecdsa-sha2-nistp256":
            curve, s, rest = get_NS(rest, 2)
            if curve not in ECDSA_CURVES:
                raise ValueError("Unsupported ECDSA curve: %s" % curve)
            if s[0] != "\x04":
                raise ValueError("ECDSA point compression has been used")
            return cls(VerifyingKey.from_string(s[1:], ECDSA_CURVES[curve]), key_type)
        else:
            raise Exception("Unknown blob type: %s" % key_type)
    
    ##
    ## RSA keys::
    ##     string 'ssh-rsa'
    ##     integer n
    ##     integer e
    ##     integer d
    ##     integer u
    ##     integer p
    ##     integer q
    ## 
    ## DSA keys::
    ##     string 'ssh-dss'
    ##     integer p
    ##     integer q
    ##     integer g
    ##     integer y
    ##     integer x
    ##
    @classmethod
    def from_string_private_blob(cls, data):
        key_type, rest = get_NS(data, 1)
        if key_type == "ssh-rsa":
            n, e, d, u, p, q, rest = get_MP(rest, 6)
            rsakey = cls(RSA.construct((n, e, d, p, q, u)))
            return rsakey
        elif key_type == "ssh-dss":
            p, q, g, y, x, rest = get_MP(rest, 5)
            dsakey = cls(DSA.construct((y, g, p, q, x)))
            return dsakey
        else:
            raise ValueError('unknown blob type: %s' % key_type)
        
    @classmethod
    def from_string_public_openssh(cls, data):
        """
        Parse openSSH-style keys
        """
        blob = base64.decodestring(data.split()[1])
        return cls.from_string_blob(blob)
    
    @classmethod
    def from_string_private_noc(cls, data):
        blob = base64.decodestring(data.split()[1])
        return cls.from_string_private_blob(blob)
    
    def verify(self, signature, data):
        """
        Verify data signature
        """
        signature_type, signature = get_NS(signature)
        if signature_type != self.ssh_type():
            raise ValueError("Bad signature type: %s" % signature_type)
        if self.type() == "RSA":
            numbers = list(get_MP(signature))
            digest = pkcs1_digest(data, self.key.size() / 8)
            return self.key.verify(digest, numbers)
        elif self.type() == "DSA":
            signature, rest = get_NS(signature)
            numbers = [bytes_to_long(n) for n in signature[:20], signature[20:]]
            digest = sha1(data).digest()
            return self.key.verify(digest, numbers)
        elif self.type() == "ECDSA":
            signature, _ = get_NS(signature)
            signdecode = lambda sig, order: get_MP(sig, 2)[:2]
            digest = sha256(data).digest()
            return self.key.verify_digest(signature, digest, sigdecode=signdecode)
        else:
            raise NotImplementedError("Unsupported signature type: %s" % signature_type)

    def ssh_type(self):
        """
        Detects key's ssh type
        """
        if self._ssh_type:
            return self._ssh_type
        else:
            return {
                "RSA": "ssh-rsa",
                "DSA": "ssh-dss"
            }[self.type()]
    
    def type(self):
        """
        Return key type (RSA/DSA/ECDSA)
        """
        # Possible classes:
        # Crypto.PublicKey.RSA.*, Crypto.PublicKey.DSA.*
        # @todo: SigningKey
        c = str(self.key.__class__)
        if c.startswith("Crypto.PublicKey"):
            type = c.split(".")[2]
            if type in ("RSA", "DSA"):
                return type
            else:
                raise RuntimeError("unknown type of key: %s" % type)
            return type
        elif c.startswith("ecdsa.keys."):
            return "ECDSA"
        else:
            raise RuntimeError("unknown type of object: %r" % self.keyObject)

    ##
    ## Returns public key blob:
    ##     RSA keys::
    ##        string  'ssh-rsa'
    ##        integer e
    ##        integer n
    ##     
    ##     DSA keys::
    ##        string  'ssh-dss'
    ##        integer p
    ##        integer q
    ##        integer g
    ##        integer y
    ##     
    def blob(self):
        type=self.type()
        if type=="RSA":
            return (
                NS("ssh-rsa")+
                MP(self.key.e)+
                MP(self.key.n)
            )
        elif type=="DSA":
            return (
                NS("ssh-dss") +
                common.MP(self.key.p) +
                common.MP(self.key.q) +
                common.MP(self.key.g) +
                common.MP(self.key.y)
            )
    
    def public(self):
        """
        Returns only public part of key
        """
        return Key(self.key.publickey())
    
    def is_public(self):
        """
        Returns true if key is public key
        """
        # @todo: ECDSA
        return not self.key.has_private()
    
    def to_string(self):
        """
        Convert key to string
        """
        extra = "noc@%s"%os.uname()[1]
        if self.is_public():
            data = self.blob()
        else:
            key_type=self.ssh_type()
            if key_type == "ssh-rsa":
                data = (
                    NS("ssh-rsa") +
                    MP(self.key.n) +
                    MP(self.key.e) +
                    MP(self.key.d) +
                    MP(self.key.u) +
                    MP(self.key.p) +
                    MP(self.key.q)
                )
            elif key_type == "ssh-dss":
                data = (
                    NS("ssh-dss") +
                    MP(self.key.p) +
                    MP(self.key.q) +
                    MP(self.key.g) +
                    MP(self.key.y) +
                    MP(self.key.x)
                )
        data = base64.encodestring(data).replace("\n", "")
        return "%s %s %s" % (self.ssh_type(), data, extra)
    
    def sign(self, data):
        """
        Sign data with key
        """
        if self.type() == "RSA":
            digest = pkcs1_digest(data, self.key.size()/8)
            signature = self.key.sign(digest, '')[0]
            return NS(self.ssh_type())+NS(long_to_bytes(signature))
        elif self.type() == "DSA":
            digest = sha1(data).digest()
            r = secure_random(19)
            sig = self.key.sign(digest, r)
            return NS(self.ssh_type())+NS(long_to_bytes(sig[0], 20) + long_to_bytes(sig[1], 20))
        elif self.type() == "ECDSA":
            # @todo:
            raise NotImplementedError()

##
## Generate RSA key pair
## And save to files path and path.pub
##
def generate_pair(path, bits=1024):
    k=Key.generate("RSA", bits)
    safe_rewrite(path, k.to_string())
    safe_rewrite(path+".pub", k.public().to_string())


## ECDSA curves
ECDSA_CURVES = {
    "nistp256": curves.NIST256p,
    "nistp384": curves.NIST384p,
    "nistp521": curves.NIST521p
}
