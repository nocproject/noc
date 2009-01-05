import noc.sa.script

class Script(noc.sa.script.Script):
    name="DLink.DES35xx.get_config"
    def execute(self):
        config=self.cli("show config current_config")
        return self.cleaned_config(config)
