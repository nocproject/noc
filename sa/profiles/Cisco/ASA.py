##
## Vendor: Cisco
## OS:     ASA
## Compatible: 7.0
##
import noc.sa.profiles
from noc.sa.protocols.sae_pb2 import TELNET,SSH

class Profile(noc.sa.profiles.Profile):
    name="Cisco.ASA"
    supported_schemes=[TELNET,SSH]
    pattern_more="^<--- More --->"
    pattern_unpriveleged_prompt=r"^\S+?>"
    command_super="enable"
    pattern_prompt=r"^\S+?#"
    command_more=" "
    command_pull_config=["show running-config"]
