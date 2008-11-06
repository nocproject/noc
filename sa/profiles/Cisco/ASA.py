##
## Vendor: Cisco
## OS:     ASA
## Compatible: 7.0
##
import noc.sa.profiles

class Profile(noc.sa.profiles.Profile):
    name="Cisco.ASA"
    pattern_more="^<--- More --->"
    pattern_unpriveleged_prompt=r"^\S+?>"
    command_super="enable"
    pattern_prompt=r"^\S+?#"
    command_more=" "
    command_pull_config=["show running-config"]
