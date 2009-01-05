##
## Vendor: Juniper
## OS:     ScreenOS
##
import noc.sa.profiles
from noc.sa.protocols.sae_pb2 import TELNET,SSH

class Profile(noc.sa.profiles.Profile):
    name="Juniper.ScreenOS"
    supported_schemes=[TELNET,SSH]
    pattern_prompt=r"^\s*\S*-> "
    pattern_more=r"^--- more ---"
    command_more=" "
    #pattern_lg_as_path_list=r"(?<=AS path: )(\d+(?: \d+)*)"
    #pattern_lg_best_path=r"^(\s+[+*].+?\s+Router ID: \S+)"
    
    