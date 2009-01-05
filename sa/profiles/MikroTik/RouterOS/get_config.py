import noc.sa.script

class Script(noc.sa.script.Script):
    name="MikroTik.RouterOS.get_config"
    def execute(self):
        config=self.cli("export")
        return self.cleaned_config(config)
