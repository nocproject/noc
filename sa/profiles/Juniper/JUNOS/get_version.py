import noc.sa.script
from noc.sa.interfaces import IGetVersion
import re

rx_ver=re.compile(r"Model:\s+(?P<platform>\S+).+JUNOS Base OS Software Suite \[(?P<version>[^\]]+)\]",re.MULTILINE|re.DOTALL)

class Script(noc.sa.script.Script):
    name="Juniper.JUNOS.get_version"
    implements=[IGetVersion]
    def execute(self):
        self.cli("set cli screen-length 0")
        v=self.cli("show version")
        print v
        match=rx_ver.search(v)
        return {
            "vendor"    : "Juniper",
            "platform"  : match.group("platform"),
            "version"   : match.group("version"),
        }
