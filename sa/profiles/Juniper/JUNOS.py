##
## Vendor: Juniper
## OS:     JUNOS
##
from noc.sa.profiles import BaseProfile

class Profile(BaseProfile):
    name="Juniper.JUNOS"
    pattern_prompt="^({master}\n)?\S*>"
    pattern_more=r"^---\(more.*?\)---"
    command_more=" "
    pattern_lg_as_path_list=r"(?<=AS path: )(\d+(?: \d+)*)"
    pattern_lg_best_path=r"^(\s+[+*].+?\s+Router ID: \S+)"
    command_pull_config=["show configuration"]
    
    def generate_prefix_list(self,name,pl,strict=True):
        if strict:
            p="        route-filter %s exact;"
        else:
            p="        route-filter %s orlonger;"
        out=["term pass {","    from {"]+[p%x for x in pl]+["    }","    then next policy;"]
        out+=["term reject {","    then reject;","}"]
        return "\n".join(out)