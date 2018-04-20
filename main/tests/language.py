# -*- coding: utf-8 -*-
<<<<<<< HEAD
# ---------------------------------------------------------------------
# Language model test
# ---------------------------------------------------------------------
# Copyright (C) 2007-2011 The NOC Project
# See LICENSE for details
# ---------------------------------------------------------------------

# NOC modules
from noc.lib.test import ModelTestCase
from noc.main.models.language import Language
=======
##----------------------------------------------------------------------
## Language model test
##----------------------------------------------------------------------
## Copyright (C) 2007-2011 The NOC Project
## See LICENSE for details
##----------------------------------------------------------------------

## NOC modules
from noc.lib.test import ModelTestCase
from noc.main.models import Language
>>>>>>> 2ab0ab7718bb7116da2c3953efd466757e11d9ce


class LanguageModelTestCase(ModelTestCase):
    model = Language

    data = [
        {"name": "Tengwar", "native_name": "Quenya", "is_active": False},
        {"name": "Klingon", "native_name": "Klingon", "is_active": True}
    ]
