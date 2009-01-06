##
## Vendor: ZTE
## OS:     ZXDSL531
## Compatible:
##
import noc.sa.profiles
from noc.sa.protocols.sae_pb2 import TELNET,HTTP

class Profile(noc.sa.profiles.Profile):
    name="ZTE.ZXDSL531"
    supported_schemes=[TELNET,HTTP]
    pattern_username="Login name:"
    pattern_password="Password:"
    pattern_prompt="^>"
    method_pull_config="POST"
    path_pull_config="/psiBackupInfo.cgi"
    file_pull_config="backupsettings.xml"
    config_skip_head=0
    config_volatile=["<entry1 sessionID=.+?/>"]
    