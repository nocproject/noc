##
## Vendor: Juniper
## OS:     JUNOSe
##
import noc.sa.profiles
from noc.sa.protocols.sae_pb2 import TELNET,SSH

class Profile(noc.sa.profiles.Profile):
    name="Juniper.JUNOSe"
    supported_schemes=[TELNET,SSH]
    pattern_unpriveleged_prompt=r"^\S+?>"
    command_super="enable"
    pattern_prompt=r"^\S+?#"
    pattern_more=r"^ --More-- "
    command_more=" "
    #pattern_lg_as_path_list=r"(?<=AS path: )(\d+(?: \d+)*)"
    #pattern_lg_best_path=r"^(\s+[+*].+?\s+Router ID: \S+)"
    command_pull_config=["terminal length 0","show configuration"]
    config_volatile=["^! Configuration script being generated on.*?^"]
    
