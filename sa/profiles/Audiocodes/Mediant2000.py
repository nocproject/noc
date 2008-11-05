##
## Vendor: Audiocodes
## OS:     Mediant2000
##
import noc.sa.profiles

class Profile(noc.sa.profiles.Profile):
    name="Audiocodes.Mediant2000"
    pattern_more="^ -- More --"
    command_pull_config=["conf","cf get"]
    method_pull_config="GET"
    path_pull_config="/FS/BOARD.ini"
    file_pull_config="BOARD.ini"
    config_skip_head=0
    rogue_chars=None

