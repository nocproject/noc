# -*- coding: utf-8 -*-
##----------------------------------------------------------------------
## Network Probe
##----------------------------------------------------------------------
## Copyright (C) 2007-2009 The NOC Project
## See LICENSE for details
##----------------------------------------------------------------------
"""
"""
from noc.pm.probes.tcp import *
import re
##
## Check 220 returned by server
##
class SMTPProbeSocket(TCPProbeSocket):
    DEFAULT_PORT=25
    RESPONSE_RE=re.compile("^220 ")
    WAIT_UNTIL_CLOSE=False
##
## SMTP server probe
##
class SMTPProbe(TCPProbe):
    name="smtp"
    socket_class=SMTPProbeSocket
