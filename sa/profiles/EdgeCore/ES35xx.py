##
## Vendor: EdgeCore
## OS:     ES35xx
## Compatible with: ES3526S
##
import noc.sa.profiles
from noc.sa.protocols.sae_pb2 import TELNET,SSH

class Profile(noc.sa.profiles.Profile):
    name="EdgeCore.ES35xx"
    supported_schemes=[TELNET,SSH]
    pattern_more="^---More---.*?$"
    command_more=" "
    rogue_chars=["\r","\x08"]
    command_pull_config=["show running-config"]

