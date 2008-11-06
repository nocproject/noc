##
## Vendor: Juniper
## OS:     SRC-PE
##
import noc.sa.profiles

class Profile(noc.sa.profiles.Profile):
    name="Juniper.SRC-PE"
    pattern_prompt="^\S*>"
    pattern_more=r"^ -- MORE -- "
    command_more=" "
    rogue_chars=[]
    command_pull_config=["show configuration"]
