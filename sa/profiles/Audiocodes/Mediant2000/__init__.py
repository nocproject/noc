##
## Vendor: Audiocodes
## OS:     Mediant2000
##
import noc.sa.profiles
from noc.sa.protocols.sae_pb2 import TELNET,SSH,HTTP

class Profile(noc.sa.profiles.Profile):
    name="Audiocodes.Mediant2000"
    supported_schemes=[TELNET,SSH,HTTP]
    pattern_more="^ -- More --"
    method_pull_config="GET"
    path_pull_config="/FS/BOARD.ini"
    file_pull_config="BOARD.ini"
    config_skip_head=0

