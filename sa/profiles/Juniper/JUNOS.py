##
## Vendor: Juniper
## OS:     JUNOS
##
from noc.sa.profiles import BaseProfile

class Profile(BaseProfile):
    pattern_prompt="^({master}\n)?\S*>"
    pattern_more=r"^---\(more.*?\)---"
    command_more=" "
    pattern_lg_as_path_list=r"(?<=AS path: )(\d+(?: \d+)*)"
    pattern_lg_best_path=r"^(\s+[+*].+?\s+Router ID: \S+)"