# -*- coding: utf-8 -*-
##----------------------------------------------------------------------
## SSH Probe
##----------------------------------------------------------------------
## Copyright (C) 2007-2009 The NOC Project
## See LICENSE for details
##----------------------------------------------------------------------
"""
"""
from noc.pm.probes.tcp import *
import re
##
## Check "SSH" string returned by server
##
class SSHProbeSocket(TCPProbeSocket):
    DEFAULT_PORT=22
    RESPONSE_RE=re.compile("SSH")
    WAIT_UNTIL_CLOSE=False
##
## SSH Probe
##
class SSHProbe(TCPProbe):
    name="ssh"
    socket_class=SSHProbeSocket
