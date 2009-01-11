##
## Vendor: Protei
## OS:     MAK
##
import noc.sa.profiles
from noc.sa.protocols.sae_pb2 import TELNET,SSH

class Profile(noc.sa.profiles.Profile):
    name="Protei.MAK"
    supported_schemes=[TELNET,SSH]
    command_submit="\r"
    pattern_prompt="(^\S+\$|MAK>)"
