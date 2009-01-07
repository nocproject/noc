import noc.sa.script
from noc.sa.interfaces import IGetConfig

class Script(noc.sa.script.Script):
    name="MikroTik.RouterOS.get_config"
    implements=[IGetConfig]
    def execute(self):
        config=self.cli("export")
        return self.cleaned_config(config)
