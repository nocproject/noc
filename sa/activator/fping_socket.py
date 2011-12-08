# -*- coding: utf-8 -*-
##----------------------------------------------------------------------
## FPing probe socket
##----------------------------------------------------------------------
## Copyright (C) 2007-2011 The NOC Project
## See LICENSE for details
##----------------------------------------------------------------------

## Python modules
import os
import tempfile
## NOC modules
from noc.lib.nbsocket.ptysocket import PTYSocket


class FPingProbeSocket(PTYSocket):
    """
    External fping process.
    Runs fping against supplied list of hosts.
    Returns a list of unreachable hosts
    """
    def __init__(self, factory, fping_path, addresses, callback):
        self.result = ""
        # Write hosts list to temporary file
        h, self.tmp_path = tempfile.mkstemp()
        f = os.fdopen(h, "w")
        f.write("\n".join(addresses) + "\n")
        f.close()
        self.callback = callback
        # Fping requires root to read hosts from file. Run it through the wrapper
        PTYSocket.__init__(self, factory,
                           ["./scripts/stdin-wrapper", self.tmp_path,
                            fping_path, "-A", "-u"])

    def on_close(self):
        os.unlink(self.tmp_path)
        # fping issues duplicated addresses sometimes.
        # Remove duplicates
        r = set([x.strip() for x in self.result.split("\n") if x.strip()])
        self.callback(r)

    def on_read(self, data):
        self.result += data
