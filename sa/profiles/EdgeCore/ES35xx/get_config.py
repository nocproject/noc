import noc.sa.script
from noc.sa.interfaces import IGetConfig

class Script(noc.sa.script.Script):
    name="EdgeCore.ES35xx.get_config"
    implements=[IGetConfig]
    def execute(self):
        config=self.cli("show running-config")
        return self.cleaned_config(config)
