# -*- coding: utf-8 -*-
##----------------------------------------------------------------------
## RIR model test
##----------------------------------------------------------------------
## Copyright (C) 2007-2011 The NOC Project
## See LICENSE for details
##----------------------------------------------------------------------

## NOC modules
from noc.lib.test import ModelTestCase
from noc.peer.models import RIR


class LanguageModelTestCase(ModelTestCase):
    model = RIR

    data = [
        {"name": "VIRTRIR", "whois": "whois.virtrir.net"}
    ]
