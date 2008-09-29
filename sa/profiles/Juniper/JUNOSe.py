##
## Vendor: Juniper
## OS:     JUNOSe
##
from noc.sa.profiles import BaseProfile

class Profile(BaseProfile):
    name="Juniper.JUNOSe"
    pattern_prompt="^\S*>"
    pattern_more=r"^ --More-- "
    command_more=" "
    #pattern_lg_as_path_list=r"(?<=AS path: )(\d+(?: \d+)*)"
    #pattern_lg_best_path=r"^(\s+[+*].+?\s+Router ID: \S+)"
    command_pull_config=["show configuration"]
    
