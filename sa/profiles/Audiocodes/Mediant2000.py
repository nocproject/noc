##
## Vendor: Audiocodes
## OS:     Mediant2000
##
import noc.sa.profiles

class Profile(noc.sa.profiles.Profile):
    name="Audiocodes.Mediant2000"
    pattern_more="^ -- More --"
    command_pull_config=["conf","cf get"]

