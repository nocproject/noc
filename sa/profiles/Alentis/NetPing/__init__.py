# -*- coding: utf-8 -*-
##----------------------------------------------------------------------
## Vendor: Alentis
## OS:     NetPing
##----------------------------------------------------------------------
## Copyright (C) 2007-2014 The NOC Project
## See LICENSE for details
##----------------------------------------------------------------------

## Python modules
import json
import re
## NOC modules
from noc.sa.profiles import Profile as NOCProfile
from noc.sa.protocols.sae_pb2 import HTTP


class Profile(NOCProfile):
    name = "Alentis.NetPing"
    supported_schemes = [NOCProfile.HTTP]

    rx_data = re.compile(
        r"^var data\s*=\s*(?P<var_data>{.+})",
        re.MULTILINE | re.DOTALL)

    def var_data(self, script, url):
        try:
            data = script.http.get(url)
        except:
            data = ''
        match = self.rx_data.search(data)
        if match:
            var = match.group("var_data")
            var = var.replace("'", '"')
            var = var.replace("{", '{"')
            var = var.replace(",", ',"')
            m = var.split(",")
            for i in range(len(m)):
                m[i] = m[i].replace(":", '":', 1)
            return json.loads(','.join(m))
        else:
            return {}
