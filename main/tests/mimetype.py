# -*- coding: utf-8 -*-
##----------------------------------------------------------------------
## MIMEType model test
##----------------------------------------------------------------------
## Copyright (C) 2007-2011 The NOC Project
## See LICENSE for details
##----------------------------------------------------------------------

## Python modules
from __future__ import with_statement
## NOC modules
from noc.lib.test import ModelTestCase
from noc.main.models import MIMEType
from noc.lib.validators import ValidationError


class MIMETypeModelTestCase(ModelTestCase):
    model = MIMEType

    data = [
        {"extension": ".noc", "mime_type": "application/noc"},
        {"extension": ".nocx", "mime_type": "application/noc-x"}
    ]

    def test_unique(self):
        m1 = MIMEType(extension=".noc", mime_type="application/test")
        m1.save()
        with self.assertRaises(Exception):  # IntegrityError
            m2 = MIMEType(extension=".noc", mime_type="application/test")
            m2.save()

    def test_validators(self):
        m1 = MIMEType(extension="noc", mime_type="application/test")
        with self.assertRaises(ValidationError):
            m1.full_clean()
        m2 = MIMEType(extension=".noc", mime_type="application")
        with self.assertRaises(ValidationError):
            m2.full_clean()
        m3 = MIMEType(extension=".noc", mime_type="application/test")
        m3.full_clean()
