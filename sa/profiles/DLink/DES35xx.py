##
## Vendor: D-Link
## OS:     DES-35xx
## Compatible:
##
import noc.sa.profiles
from noc.sa.protocols.sae_pb2 import TELNET,SSH

class Profile(noc.sa.profiles.Profile):
    name="DLink.DES35xx"
    supported_schemes=[TELNET,SSH]
    pattern_more="^CTRL\+C.+?a All"
    pattern_prompt=r"^\S+?#"
    command_more="a"
    command_pull_config=["show config current_config"]
    config_volatile=["^%.*?$"]