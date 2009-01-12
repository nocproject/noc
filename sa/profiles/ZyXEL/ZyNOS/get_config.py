import noc.sa.script
from noc.sa.interfaces import IGetConfig

class Script(noc.sa.script.Script):
    name="Zyxel.ZyNOS.get_config"
    implements=[IGetConfig]
    def execute(self):
        config=self.cli("show running-config")
        config=self.strip_first_lines(config,4)
        return self.cleaned_config(config)
