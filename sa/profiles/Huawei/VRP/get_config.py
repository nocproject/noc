import noc.sa.script
from noc.sa.interfaces import IGetConfig

class Script(noc.sa.script.Script):
    name="Huawei.VRP.get_config"
    implements=[IGetConfig]
    def execute(self):
        config=self.cli("display current-configuration")
        return self.cleaned_config(config)
