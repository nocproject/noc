##
## Abstract Profile
##
class BaseProfile(object):
    pattern_username="[Uu]sername:"
    pattern_password="[Pp]assword:"
    pattern_prompt=r"^\S*[>#]"
    pattern_more="^---MORE---"
    command_submit="\n"
    command_more="\n"
    rogue_chars=["\r"]

def get_profile_class(name):
    module=__import__("noc.sa.profile."+name,globals(),locals(),["Profile"])
    return getattr(module,"Profile")