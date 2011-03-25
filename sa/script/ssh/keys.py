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
from hashlib import sha1
## Third-party modules
from Crypto.PublicKey import RSA, DSA
## NOC modules
from noc.sa.script.ssh.util import *
from noc.lib.fileutils import read_file, safe_rewrite

##
##
##
class Key(object):
    def __init__(self, key):
        self.key=key
    
    ##
    ## Return new generated key
    ##
    @classmethod
    def generate(cls, type, bits):
        if type=="RSA":
            k=RSA
        elif type=="DSA":
            k=DSA
        else:
            raise ValueError("Invalid key type")
        return cls(k.generate(bits, secure_random))
    
    ##
    ## Load key from file. Returns Key instance
    ##
    @classmethod
    def from_file(cls, path):
        return cls.from_string(read_file(path))
    
    ##
    ## Try to guess key type. Returns string with key type or None
    ##
    @classmethod
    def guess_key_type(cls, data):
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
    
    ##
    ## Create key instance from string
    ##
    @classmethod
    def from_string(cls, data, type=None):
        if type is None:
            type=cls.guess_key_type(data)
        if type is None:
            raise RuntimeError("Cannot guess key type for: %r"%data)
        method=getattr(cls, "from_string_%s"%type.lower(), None)
        if method is None:
            raise ValueError("Key type '%s' is not supported"%type)
        return method(data)
    
    ##
    ## Parse blob string key
    ##
    @classmethod
    def from_string_blob(cls, data):
        key_type, rest = get_NS(data, 1)
        if key_type == "ssh-rsa":
            e, n, rest = get_MP(rest, 2)
            return cls(RSA.construct((n, e)))
        elif key_type == "ssh-dss":
            p, q, g, y, rest = get_MP(rest, 4)
            return cls(DSA.construct((y, g, p, q)))
        else:
            raise Exception("unknown blob type: %s" % key_type)
    
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
            dsakey =  Class(DSA.construct((y, g, p, q, x)))
            return dsakey
        else:
            raise ValueError('unknown blob type: %s' % key_type)
        
    ##
    ## Parse openSSH-style keys
    ##
    @classmethod
    def from_string_public_openssh(cls, data):
        blob = base64.decodestring(data.split()[1])
        return cls.from_string_blob(blob)
    
    ##
    ##
    ##
    @classmethod
    def from_string_private_noc(cls, data):
        blob = base64.decodestring(data.split()[1])
        return cls.from_string_private_blob(blob)
    
    ##
    ## Verify data signature
    ##
    def verify(self, signature, data):
        signature_type, signature = get_NS(signature)
        if signature_type != self.ssh_type():
            return False
        if self.type() == "RSA":
            numbers = list(get_MP(signature))
            digest = pkcs1_digest(data, self.key.size() / 8)
        elif self.type() == "DSA":
            signature, rest = get_NS(signature)
            numbers = [bytes_to_long(n) for n in signature[:20], signature[20:]]
            digest = sha1(data).digest()
        return self.key.verify(digest, numbers)
    
    ##
    ## Detects key's ssh type
    ##
    def ssh_type(self):
        return {"RSA":"ssh-rsa", "DSA":"ssh-dss"}[self.type()]
    
    ##
    ## Return key type (RSA/DSA)
    ##
    def type(self):
        # the class is Crypto.PublicKey.<type>.<stuff we don"t care about>
        c = str(self.key.__class__)
        if c.startswith("Crypto.PublicKey"):
            type = c.split(".")[2]
        else:
            raise RuntimeError("unknown type of object: %r" % self.keyObject)
        if type in ("RSA", "DSA"):
            return type
        else:
            raise RuntimeError("unknown type of key: %s" % type)
    
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
                NS("ssh-dss")+
                common.MP(self.key.p)+
                common.MP(self.key.q)+ 
                common.MP(self.key.g)+
                common.MP(self.key.y)
            )
        
    
    ##
    ## Returns only public part of key
    ##
    def public(self):
        return Key(self.key.publickey())
    
    ##
    ## Returns true if key is public key
    ##
    def is_public(self):
        return not self.key.has_private()
    
    ##
    ## Convert key to string
    ##
    def to_string(self):
        extra = "noc@%s"%os.uname()[1]
        if self.is_public():
            data = self.blob()
        else:
            key_type=self.ssh_type()
            if key_type == "ssh-rsa":
                data=(
                    NS("ssh-rsa")+
                    MP(self.key.n)+
                    MP(self.key.e)+
                    MP(self.key.d)+
                    MP(self.key.u)+
                    MP(self.key.p)+
                    MP(self.key.q)
                )
            elif key_type == "ssh-dss":
                data=(
                    NS("ssh-dss")+
                    MP(self.key.p)+
                    MP(self.key.q)+
                    MP(self.key.g)+
                    MP(self.key.y)+
                    MP(self.key.x)
                )
        data = base64.encodestring(data).replace("\n", "")
        return "%s %s %s"%(self.ssh_type(), data, extra)
    
    ##
    ## Sign data with key
    ##
    def sign(self, data):
        if self.type() == "RSA":
            digest = pkcs1_digest(data, self.key.size()/8)
            signature = self.key.sign(digest, '')[0]
            return NS(self.ssh_type())+NS(long_to_bytes(signature))
        elif self.type() == "DSA":
            digest = sha1(data).digest()
            r = secure_random(19)
            sig = self.key.sign(digest, r)
            return NS(self.ssh_type())+NS(long_to_bytes(sig[0], 20)+long_to_bytes(sig[1], 20))
    

##
## Generate RSA key pair
## And save to files path and path.pub
##
def generate_pair(path, bits=1024):
    k=Key.generate("RSA", bits)
    safe_rewrite(path, k.to_string())
    safe_rewrite(path+".pub", k.public().to_string())
