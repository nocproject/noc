##
## Vendor: Zyxel
## OS:     ZyNOS
## Compatible: 3124
##
import noc.sa.profiles
from noc.sa.protocols.sae_pb2 import TELNET,SSH

class Profile(noc.sa.profiles.Profile):
    name="Zyxel.ZyNOS"
    supported_schemes=[TELNET,SSH]
    pattern_username="User name:"
    command_more=" "
    command_pull_config=["show running-config"]