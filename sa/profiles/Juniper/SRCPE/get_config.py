import noc.sa.script
from noc.sa.interfaces import IGetConfig

class Script(noc.sa.script.Script):
    name="Juniper.SRCPE.get_config"
    implements=[IGetConfig]
    def execute(self):
        config=self.cli("show configuration")
        return self.cleaned_config(config)
