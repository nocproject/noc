##
##
##
class Profile(object):
    pattern_username="[Uu]sername:"
    pattern_password="[Pp]assword:"
    pattern_prompt=r"^\S*[>#]"
    pattern_more="^---MORE---"
    command_submit="\n"
    command_more="\n"
    rogue_chars=["\r"]
    @classmethod
    def get_profile(self,name):
        if name not in PROFILES:
            raise Exception("Invalid profile: %s"%name)
        return PROFILES[name]
    
class CiscoIOSProfile(Profile): pass
    
class JuniperJUNOSProfile(Profile):
    pattern_prompt="^({master}\n)?\S*>"
    pattern_more=r"^---\(more.*?\)---"
    command_more=" "
    
#class JuniperJUNOSeProfile(Profile):
#    pattern_more="^ --More--"
    
PROFILES={
    "CISCO::IOS"     : CiscoIOSProfile(),
    "JUNIPER::JUNOS" : JuniperJUNOSProfile(),
}

#Profiles to be done
# JUNIPER::ScreenOS
# JUNIPER::JUNOSe
# JUNIPER::SRC-PE
# Alcatel::AOS
# EdgeCore::EdgeCore
# Zyxel::ZyOS
# CISCO::PIX::7
# CISCO::PIX::6
# Audiocodes::Mediant2000
# Audiocodes::nCite
# Huawei::VRP