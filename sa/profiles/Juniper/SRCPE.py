##
## Vendor: Juniper
## OS:     SRC-PE
##
import noc.sa.profiles
from noc.sa.protocols.sae_pb2 import TELNET,SSH

class Profile(noc.sa.profiles.Profile):
    name="Juniper.SRC-PE"
    supported_schemes=[TELNET,SSH]
    pattern_prompt="^\S*>"
    pattern_more=r"^ -- MORE -- "
    command_more=" "
    rogue_chars=[]
    command_pull_config=["show configuration"]
