##
## Vendor: MikroTik
## OS:     RouterOS
## Compatible: 2.8, 2.9
##
import noc.sa.profiles
from noc.sa.protocols.sae_pb2 import TELNET,SSH

class Profile(noc.sa.profiles.Profile):
    name="MikroTik.RouterOS"
    supported_schemes=[TELNET,SSH]
    command_submit="\r"
    pattern_prompt=r"^\[.+?@.+?\] >"
    command_pull_config=["export"]
    config_volatile=["^#.*?$"]