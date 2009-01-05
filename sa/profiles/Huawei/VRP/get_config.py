import noc.sa.script

class Script(noc.sa.script.Script):
    name="Huawei.VRP.get_config"
    def execute(self):
        config=self.cli("display current-configuration")
        return self.cleaned_config(config)
