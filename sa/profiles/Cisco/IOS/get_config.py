import noc.sa.script
from noc.sa.interfaces import IGetConfig

class Script(noc.sa.script.Script):
    name="Cisco.IOS.get_config"
    implements=[IGetConfig]
    def execute(self):
        self.cli("terminal length 0")
        config=self.cli("show running-config")
        return self.cleaned_config(config)
