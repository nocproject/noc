import noc.sa.script

class Script(noc.sa.script.Script):
    name="Juniper.JUNOS.get_config"
    def execute(self):
        self.cli("set cli screen-length 0")
        config=self.cli("show configuration")
        return self.cleaned_config(config)
