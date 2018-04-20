# -*- coding: utf-8 -*-
<<<<<<< HEAD
# ---------------------------------------------------------------------
# RIR model test
# ---------------------------------------------------------------------
# Copyright (C) 2007-2011 The NOC Project
# See LICENSE for details
# ---------------------------------------------------------------------

# NOC modules
from noc.lib.test import ModelTestCase
from noc.peer.models.rir import RIR
=======
##----------------------------------------------------------------------
## RIR model test
##----------------------------------------------------------------------
## Copyright (C) 2007-2011 The NOC Project
## See LICENSE for details
##----------------------------------------------------------------------

## NOC modules
from noc.lib.test import ModelTestCase
from noc.peer.models import RIR
>>>>>>> 2ab0ab7718bb7116da2c3953efd466757e11d9ce


class LanguageModelTestCase(ModelTestCase):
    model = RIR

    data = [
        {"name": "VIRTRIR", "whois": "whois.virtrir.net"}
    ]
