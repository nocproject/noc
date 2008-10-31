##
## Vendor: Huawei
## OS:     VRP
## Compatible: 3.1
##
import noc.sa.profiles

class Profile(noc.sa.profiles.Profile):
    name="Huawei.VRP"
    pattern_more="^  ---- More ----"
    pattern_prompt=r"^[<#]\S+?[>#]"
    command_more=" "
    command_pull_config=["display current-configuration"]
    config_volatile=["^%.*?$"]