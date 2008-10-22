##
## Vendor: Alcatel
## OS:     AOS
## Compatible: OS LS6224
##
import noc.sa.profiles

class Profile(noc.sa.profiles.Profile):
    name="Alcatel.AOS"
    pattern_username="User Name:"
    pattern_more="^More: "
    command_more=" "
    command_pull_config=["show running-config"]