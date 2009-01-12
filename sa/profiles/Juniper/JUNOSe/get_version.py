import noc.sa.script
from noc.sa.interfaces import IGetVersion
import re

rx=re.compile(r"Juniper\s+(?P<platform>.+?)$.+Version\s+(?P<version>.+?)\s*\[",re.MULTILINE|re.DOTALL)

class Script(noc.sa.script.Script):
    name="Juniper.JUNOSe.get_version"
    implements=[IGetVersion]
    def execute(self):
        self.cli("terminal length 0")
        v=self.cli("show version")
        match=rx.search(v.replace(":",""))
        return {
            "vendor"    : "Juniper",
            "platform"  : match.group("platform"),
            "version"   : match.group("version"),
        }