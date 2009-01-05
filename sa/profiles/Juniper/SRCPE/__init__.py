##
## Vendor: Juniper
## OS:     SRC-PE
##
import noc.sa.profiles
from noc.sa.protocols.sae_pb2 import TELNET,SSH

class Profile(noc.sa.profiles.Profile):
    name="Juniper.SRCPE"
    supported_schemes=[TELNET,SSH]
    pattern_prompt="^\S*>"
    pattern_more=r"^ -- MORE -- "
    command_more=" "
    rogue_chars=[]
