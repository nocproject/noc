##
## Vendor: Zyxel
## OS:     ZyNOS
## Compatible: 3124
##
import noc.sa.profiles

class Profile(noc.sa.profiles.Profile):
    name="Zyxel.ZyNOS"
    pattern_username="User name:"
    command_more=" "
    command_pull_config=["show running-config"]