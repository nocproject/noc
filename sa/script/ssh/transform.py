# -*- coding: utf-8 -*-
##----------------------------------------------------------------------
## SSH Crypto Transformations
## Based upon twisted.conch.ssh code
##----------------------------------------------------------------------
## Copyright (C) 2007-2011 The NOC Project
## See LICENSE for details
##----------------------------------------------------------------------

## Python modules
import array
import struct
from hashlib import sha1, md5
## Third-party modules
from Crypto.Util.number import long_to_bytes
from Crypto.Cipher import XOR
## NOC modules
from noc.sa.script.ssh.util import get_MP

##
## Dumb passthrough cypher
##
class DummyCipher(object):
    block_size=8
    
    def encrypt(self, x):
        return x
    
    def decrypt(self, x):
        return x

##
## SSH Crypto Transformations
##
class SSHTransform(object):
    CIPHER_MAP = {
        '3des-cbc'     : ('DES3', 24, 0),
        'blowfish-cbc' : ('Blowfish', 16,0 ),
        'aes256-cbc'   : ('AES', 32, 0),
        'aes192-cbc'   : ('AES', 24, 0),
        'aes128-cbc'   : ('AES', 16, 0),
        'cast128-cbc'  : ('CAST', 16, 0),
        'aes128-ctr'   : ('AES', 16, 1),
        'aes192-ctr'   : ('AES', 24, 1),
        'aes256-ctr'   : ('AES', 32, 1),
        '3des-ctr'     : ('DES3', 24, 1),
        'blowfish-ctr' : ('Blowfish', 16, 1),
        'cast128-ctr'  : ('CAST', 16, 1),
        'none'         : (None, 0, 0),
    }
    
    MAC_MAP = {
        'hmac-sha1' : sha1,
        'hmac-md5'  : md5,
        'none'      : None
     }
    
    def __init__(self, transport, out_cipher, in_cipher, out_mac, in_mac):
        self.transport=transport
        self.out_cipher_type=out_cipher
        self.in_cipher_type=in_cipher
        self.out_mac_type=out_mac
        self.in_mac_type=in_mac
        self.enc_block_size=0
        self.dec_block_size=0
        self.debug("Setting SSH transforms to: in=%s %s, out=%s %s"%(in_cipher, in_mac, out_cipher, out_mac))
    
    def debug(self, msg):
        self.transport.debug(msg)
    
    def get_cipher(self, cipher, IV, key):
        m_name, key_size, counter_mode=self.CIPHER_MAP[cipher]
        if m_name is None:
            return DummyCipher()
        m=__import__("Crypto.Cipher.%s"%m_name, {}, {}, "x")
        if counter_mode:
            return m.new(key[:key_size], m.MODE_CTR, IV[:m.block_size], counter=Counter(IV, m.block_size))
        else:
            return m.new(key[:key_size], m.MODE_CBC, IV[:m.block_size])
    
    def get_mac(self, mac, key):
        m = self.MAC_MAP[mac]
        if not m:
            return (None, "", "", 0)
        ds=m().digest_size
        key=key[:ds]+"\x00"*(64-ds)
        i=XOR.new("\x36").encrypt(key)
        o=XOR.new("\x5c").encrypt(key)
        return m, i, o, ds
    
    def set_keys(self, out_IV, out_key, in_IV, in_key, out_int, in_int):
        self.debug("Setting SSH transform keys")
        c=self.get_cipher(self.out_cipher_type, out_IV, out_key)
        self.encrypt=c.encrypt
        self.enc_block_size=c.block_size
        c=self.get_cipher(self.in_cipher_type,  in_IV,  in_key)
        self.decrypt=c.decrypt
        self.dec_block_size=c.block_size
        self.out_mac=self.get_mac(self.out_mac_type, out_int)
        self.in_mac =self.get_mac(self.in_mac_type, in_int)
        if self.in_mac:
            self.verify_digest_size = self.in_mac[3]
    
    def make_MAC(self, seq_id, data):
        if not self.out_mac[0]:
            return ""
        data=struct.pack('>L',seq_id)+data
        mod, i, o, ds = self.out_mac
        inner = mod(i + data)
        outer = mod(o + inner.digest())
        return outer.digest()
    
    def encrypt(self, data):
        raise Error("Cipher not set for encryption")
    
    def decrypt(self, data):
        raise Error("Cipher not set for decryption")
    
    def verify(self, seq_id, data, mac):
        if not self.in_mac[0]:
            return mac == ""
        data = struct.pack(">L", seq_id) + data
        mod, i, o, ds = self.in_mac
        inner = mod(i + data)
        outer = mod(o + inner.digest())
        return mac == outer.digest()
    

##
##
##
class Counter(object):
    def __init__(self, IV, block_size):
        IV = IV[:block_size]
        self.count, rest = get_MP('\xff\xff\xff\xff' + IV)
        self.block_size = block_size
        self.count = long_to_bytes(self.count - 1)
        self.count = '\x00' * (self.block_size - len(self.count)) + self.count
        self.count = array.array('c', self.count)
        self.len = len(self.count) - 1
    
    def __call__(self):
        i = self.len
        while i > -1:
            self.count[i] = n = chr((ord(self.count[i]) + 1) % 256)
            if n == '\x00':
                i -= 1
            else:
                return self.count.tostring()
        self.count = array.array('c', '\x00' * self.block_size)
        return self.count.tostring()
