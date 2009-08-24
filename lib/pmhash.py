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
    s=("%s@%s"%(ip,secret))+"@".join([str(t) for t in tslist])
    return sha1(s).hexdigest()
