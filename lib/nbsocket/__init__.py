# -*- coding: utf-8 -*-
##----------------------------------------------------------------------
## Clean and lightweight non-blocking socket I/O implementation
##----------------------------------------------------------------------
## Copyright (C) 2007-2011 The NOC Project
## See LICENSE for details
##----------------------------------------------------------------------

## Try to load SSL module
try:
    import ssl
    HAS_SSL = True
except ImportError:
    HAS_SSL = False

from noc.lib.nbsocket.exceptions import *
from noc.lib.nbsocket.protocols import *
from noc.lib.nbsocket.basesocket import *
from noc.lib.nbsocket.udpsocket import *
from noc.lib.nbsocket.listenudpsocket import *
from noc.lib.nbsocket.tcpsocket import *
from noc.lib.nbsocket.listentcpsocket import *
from noc.lib.nbsocket.acceptedtcpsocket import *
from noc.lib.nbsocket.connectedtcpsocket import *
from noc.lib.nbsocket.socketfactory import *
if HAS_SSL:
    from noc.lib.nbsocket.connectedtcpsslsocket import *
    from noc.lib.nbsocket.acceptedtcpsslsocket import *
