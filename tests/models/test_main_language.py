# -*- coding: utf-8 -*-
# ----------------------------------------------------------------------
# main.Language tests
# ----------------------------------------------------------------------
# Copyright (C) 2007-2018 The NOC Project
# See LICENSE for details
# ----------------------------------------------------------------------

# Python modules
from __future__ import absolute_import
# NOC modules
from .base import BaseModelTest
from noc.main.models.language import Language


class TestTestMainLanguage(BaseModelTest):
    model = Language

    def test_default_languages(self):
        """
        Check migration filled languages
        :return:
        """
        en = Language.objects.get(name="English")
        assert en.name == "English"
        assert en.native_name == "English"
        ru = Language.objects.get(name="Russian")
        assert ru.name == "Russian"
        assert ru.native_name == "Русский"
