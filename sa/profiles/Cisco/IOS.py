##
## Vendor: Cisco
## OS:     IOS
##
import noc.sa.profiles

class Profile(noc.sa.profiles.Profile):
    name="Cisco.IOS"
    pattern_more="^ --More--"
    pattern_lg_as_path_list=r"^(\s+\d+(?: \d+)*),"
    pattern_lg_best_path=r"(<A HREF.+?>.+?best)"
    requires_netmask_conversion=True
    config_volatile=["^ntp clock-period .*?^"]
    command_pull_config=["terminal length 0","show running-config"]
    config_skip_head=5
    
    def generate_prefix_list(self,name,pl,strict=True):
        p="ip prefix-list %s permit %%s"%name
        if not strict:
            p+=" le 32"
        return "no ip prefix-list %s\n"%name+"\n".join([p%x for x in pl])
    