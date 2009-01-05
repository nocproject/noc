import noc.sa.script

class Script(noc.sa.script.Script):
    name="Protei.ITG.get_config"
    def execute(self):
        self.cli("cd /usr/protei/CLI/Client")
        self.cli("./clip")
        self.cli("show-recursive")
        config=self.cli("")
        return self.cleaned_config(config)
