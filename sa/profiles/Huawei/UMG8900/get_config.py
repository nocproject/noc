import noc.sa.script

class Script(noc.sa.script.Script):
    name="Huawei.UMG8900.get_config"
    def execute(self):
        config=self.cli("dsp cfg;")
        return self.cleaned_config(config)
