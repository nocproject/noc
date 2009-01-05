import noc.sa.script

class Script(noc.sa.script.Script):
    name="Audiocodes.Mediant2000.get_config"
    def execute(self):
        self.cli("conf")
        config=self.cli("cf get")
        return self.cleaned_config(config)
