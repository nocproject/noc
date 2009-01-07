import noc.sa.script
from noc.sa.interfaces import IGetConfig

class Script(noc.sa.script.Script):
    name="Protei.ITG.get_config"
    implements=[IGetConfig]
    def execute(self):
        self.cli("cd /usr/protei/CLI/Client")
        self.cli("./clip")
        self.cli("show-recursive")
        config=self.cli("")
        return self.cleaned_config(config)
