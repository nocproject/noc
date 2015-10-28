# -*- coding: utf-8 -*-
__author__ = 'boris'

#NOC modules
from noc.core.script.base import BaseScript
from noc.sa.interfaces.igetconfig import IGetConfig
#Python modules
import re
from xml.dom.minidom import parseString

rx_config = re.compile(r"=====begin=====\n"
                       r"(?P<path>\[.*?\])(?P<part>\[\d*\])\n"
                       r"(?P<xml>.*?)\n"
                       r"=====end====="
                       ,re.DOTALL | re.MULTILINE)

head_str = """<?xml version="1.0" encoding="UTF-8" standalone="yes" ?>
<!DOCTYPE boost_serialization>
<boost_serialization signature="serialization::archive" version="8">
"""
bottom_str = """</boost_serialization>"""

class Script(BaseScript):
    name = "Cisco.DCM.get_config"
    interface = IGetConfig
    TIMEOUT = 240
    CLI_TIMEOUT = 240

    def execute(self):
        config = self.cli("python /app/zabbix/config_fetcher.py")
        config = self.strip_first_lines(config, 1)
        result = head_str

        for match in rx_config.finditer(config):
            xml = match.group("xml")
            parsing = parseString(xml)
            tree = parsing.toprettyxml()
            result += self.strip_first_lines(tree, 1)

        result += bottom_str
        return result
