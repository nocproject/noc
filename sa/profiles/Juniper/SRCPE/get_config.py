import noc.sa.script

class Script(noc.sa.script.Script):
    name="Juniper.SRCPE.get_config"
    def execute(self):
        config=self.cli("show configuration")
        return self.cleaned_config(config)
