# -*- coding: utf-8 -*-
<<<<<<< HEAD
# ---------------------------------------------------------------------
# Tangram.GT21.get_config
# ---------------------------------------------------------------------
# Copyright (C) 2007-2018 The NOC Project
# See LICENSE for details
# ---------------------------------------------------------------------
# Python modules
import re
from xml.dom.minidom import parseString
# NOC modules
from noc.core.script.base import BaseScript
from noc.sa.interfaces.igetconfig import IGetConfig


class Script(BaseScript):
    name = "Tangram.GT21.get_config"
    interface = IGetConfig

    rx_html = re.compile(
        r"""<html>.+</html>""",
        re.VERBOSE | re.MULTILINE | re.DOTALL)
    rx_xml = re.compile(
        r"""<?xml.+><settings.+></settings>""",
        re.VERBOSE | re.MULTILINE | re.DOTALL)

    def execute(self):
        config = self.http.get("/um/backup.binc")
        match_xml = self.rx_xml.search(config)
        if match_xml:
            if config.find("&lt;") != -1:
                config = config.replace("&lt;", "<")
            if config.find("&gt;") != -1:
                config = config.replace("&gt;", ">")
            parsing = parseString(config)
            return parsing.toprettyxml()

        return self.cleaned_config(config)
=======
__author__ = 'boris'
import noc.sa.script
from noc.sa.interfaces import IGetConfig
from xml.dom.minidom import *

class Script(noc.sa.script.Script):
    name = "Tangram.GT21.get_config"
    implements = [IGetConfig]

    def execute(self):
        config = self.http.get("/um/backup.binc")
        parsing = parseString(config)        
        return parsing.toprettyxml()     
>>>>>>> 2ab0ab7718bb7116da2c3953efd466757e11d9ce
