__author__ = "FeNikS"
# -*- coding: utf-8 -*-

# ---------------------------------------------------------------------
# Bradbury.HighVideo.get_version
# ---------------------------------------------------------------------
# Copyright (C) 2007-2018 The NOC Project
# See LICENSE for details
# ---------------------------------------------------------------------

# NOC modules
from noc.core.script.base import BaseScript
from noc.sa.interfaces.igetversion import IGetVersion


class Script(BaseScript):
    name = "Bradbury.HighVideo.get_version"
    interface = IGetVersion

    def execute(self):
        version = ""

        return {
            "vendor": "Bradbury",
            "platform": "HighVideo",
            "version": version if version else "Unknown",
        }
