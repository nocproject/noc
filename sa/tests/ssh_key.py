# -*- coding: utf-8 -*-
##----------------------------------------------------------------------
## ssh key tests
##----------------------------------------------------------------------
## Copyright (C) 2007-2011 The NOC Project
## See LICENSE for details
##----------------------------------------------------------------------
## Python modules
from unittest import TestCase
## NOC modules
from noc.sa.script.ssh.keys import *

K=Key.generate(1024)
DATA="foobar"

class SSHKeyTestCase(TestCase):
    def test_sign_verify(self):
        signature=K.sign(DATA)
        self.assertEquals(K.verify(signature, DATA), True)
    
    def test_sign_pk_verify(self):
        signature=K.sign(DATA)
        self.assertEquals(K.public().verify(signature, DATA), True)
    
    def test_serialization(self):
        k=K
        pk=k.public()
        # Convert to string
        s_k=k.to_string()
        s_pk=pk.to_string()
        # Convert back
        k1=Key.from_string_private_noc(s_k)
        pk1=Key.from_string(s_pk)
        
        # Check cross and mutual signatures
        self.assertEquals(pk.verify(k.sign(DATA), DATA), True)
        self.assertEquals(pk.verify(k1.sign(DATA), DATA), True)
        self.assertEquals(pk1.verify(k.sign(DATA), DATA), True)
        self.assertEquals(pk1.verify(k1.sign(DATA), DATA), True)
    
