import noc.sa.script
import re

rx_ver=re.compile(r"^Cisco IOS Software, (?P<platform>[^ ]+) Software \((?P<featureset>[^)]+)\), Version (?P<version>[^,]+),",re.MULTILINE|re.DOTALL)

class Script(noc.sa.script.Script):
    name="Cisco.IOS.get_version"
    def execute(self):
        self.cli("terminal length 0")
        v=self.cli("show version")
        match=rx_ver.search(v)
        return {
            "platform"  : match.group("platform"),
            "featureset": match.group("featureset"),
            "version"   : match.group("version"),
        }