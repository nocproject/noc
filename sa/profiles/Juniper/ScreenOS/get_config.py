import noc.sa.script

class Script(noc.sa.script.Script):
    name="Juniper.ScreenOS.get_config"
    def execute(self):
        config=self.cli("get config")
        return self.cleaned_config(config)
