##
## Vendor: Huawei
## OS:     VRP
## Compatible: 3.1
##
import noc.sa.profiles
from noc.sa.protocols.sae_pb2 import TELNET,SSH

class Profile(noc.sa.profiles.Profile):
    name="Huawei.VRP"
    supported_schemes=[TELNET,SSH]
    pattern_more="^  ---- More ----"
    pattern_prompt=r"^[<#]\S+?[>#]"
    command_more=" "
    config_volatile=["^%.*?$"]