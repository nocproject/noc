# -*- coding: utf-8 -*-
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