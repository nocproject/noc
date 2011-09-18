# -*- coding: utf-8 -*-
##----------------------------------------------------------------------
## Language model test
##----------------------------------------------------------------------
## Copyright (C) 2007-2011 The NOC Project
## See LICENSE for details
##----------------------------------------------------------------------

## NOC modules
from noc.lib.test import ModelTestCase
from noc.main.models import Language


class LanguageModelTestCase(ModelTestCase):
    model = Language

    data = [
        {"name": "Tengwar", "native_name": "Quenya", "is_active": False},
        {"name": "Klingon", "native_name": "Klingon", "is_active": True}
    ]
