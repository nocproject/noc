# -*- coding: utf-8 -*-
##----------------------------------------------------------------------
## PM Security scheme
##----------------------------------------------------------------------
## Copyright (C) 2007-2009 The NOC Project
## See LICENSE for details
##----------------------------------------------------------------------
from hashlib import sha1
##
## Calculate PM Hash
##
def pmhash(ip,secret,tslist=[]):
    """
    >>> pmhash('127.0.0.1','the secret')
    '443a7892894f2ee0a7a1beee724b284988dc4a8b'
    >>> pmhash('127.0.0.1','the secret',['ts1','ts2'])
    '9c89ae8790169ed1c55c103607ab1c960fb6d541'
    """
    s=("%s@%s"%(ip,secret))+"@".join([str(t) for t in tslist])
    return sha1(s).hexdigest()
