__author__ = 'FeNikS'
# -*- coding: utf-8 -*-

# ---------------------------------------------------------------------
# Bradbury.HighVideo.get_version
# ---------------------------------------------------------------------
# Copyright (C) 2007-2015 The NOC Project
# See LICENSE for details
# ---------------------------------------------------------------------

from noc.sa.interfaces import IGetVersion
# Python modules
# NOC modules
from noc.sa.script import Script as NOCScript


class Script(NOCScript):
    name = "Bradbury.HighVideo.get_version"
    implements = [IGetVersion]

    def execute(self):
        version = ''

        return {
            "vendor": "Bradbury",
            "platform": "HighVideo",
            "version": version if version else "Unknown"
        }
