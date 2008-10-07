##
## Vendor: Juniper
## OS:     JUNOSe
##
import noc.sa.profiles

class Profile(noc.sa.profiles.Profile):
    name="Juniper.JUNOSe"
    pattern_prompt="^\S*>"
    pattern_more=r"^ --More-- "
    command_more=" "
    #pattern_lg_as_path_list=r"(?<=AS path: )(\d+(?: \d+)*)"
    #pattern_lg_best_path=r"^(\s+[+*].+?\s+Router ID: \S+)"
    command_pull_config=["show configuration"]
    
