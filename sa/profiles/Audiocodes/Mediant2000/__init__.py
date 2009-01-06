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

