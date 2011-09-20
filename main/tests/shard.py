# -*- coding: utf-8 -*-
##----------------------------------------------------------------------
## Shard model test
##----------------------------------------------------------------------
## Copyright (C) 2007-2011 The NOC Project
## See LICENSE for details
##----------------------------------------------------------------------

## NOC modules
from noc.lib.test import ModelTestCase
from noc.main.models import Shard


class LanguageModelTestCase(ModelTestCase):
    model = Shard

    data = [
        {"name": "Test", "is_active": True, "description": "Testing shard"}
    ]
