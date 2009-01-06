import noc.sa.script
from noc.sa.protocols.sae_pb2 import TELNET,HTTP

class Script(noc.sa.script.Script):
    name="ZTE.ZXDSL531.get_config"
    def execute(self):
        if self.access_profile.scheme==self.TELNET:
            config=self.cli("dumpcfg")
        elif self.access_profile.scheme==self.HTTP:
            config=self.http.post("/psiBackupInfo.cgi")
        else:
            raise Exception("Unsupported access scheme")
        return self.cleaned_config(config)
