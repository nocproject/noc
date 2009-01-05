import noc.sa.script

class Script(noc.sa.script.Script):
    name="Zebra.Zebra.get_config"
    def execute(self):
        self.cli("terminal length 0")
        config=self.cli("show running-config")
        return self.cleaned_config(config)
