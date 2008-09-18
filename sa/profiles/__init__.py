from noc.lib.ip import bits_to_netmask
##
## Abstract Profile
##
class BaseProfile(object):
    # Regular expression to catch user name prompt
    # (Usually during telnet sessions)
    pattern_username="[Uu]sername:"
    # Regulal expression to catch password prompt
    # (Telnet/SSH sessions)
    pattern_password="[Pp]assword:"
    # Regular expression to catch command prompt
    # (CLI Sessions)
    pattern_prompt=r"^\S*[>#]"
    # Regular expression to catch pager
    # (Used in command results)
    pattern_more="^---MORE---"
    # Sequence to be send at the end of all CLI commands
    #
    command_submit="\n"
    # Sequence to be send to list forward pager
    #
    command_more="\n"
    # Sequence to gracefully close session
    #
    command_exit="exit"
    # List of chars to be stripped out of input stream
    # before checking any regular expressions
    rogue_chars=["\r"]
    
    ##
    ## Looking glass hilighting support
    ##
    
    # match.group(1) contains AS list
    pattern_lg_as_path_list=None
    # match.group(1) containts Best Path
    pattern_lg_best_path=None
    # Does the equipment supports bitlength netmasks
    # or netmask should be converted to traditional formats
    requires_netmask_conversion=False
    
    #
    # AS Path hilighting
    #
    def lg_as_path(self,m):
        def whois_formatter(q):
            return "<A HREF='http://www.db.ripe.net/whois?AS%s'>%s</A>"%(q,q)
        as_list=m.group(1).split()
        return " ".join([whois_formatter(x) for x in as_list])
    #
    # Converts ipv4 prefix to the format acceptable by router
    #
    def convert_prefix(self,prefix):
        if "/" in prefix and self.requires_netmask_conversion:
            net,mask=prefix.split("/")
            mask=bits_to_netmask(mask)
            return "%s %s"%(net,mask)
        return prefix
    #
    # Configuration generators
    #
    
    # Generate prefix list:
    # name - name of prefix list
    # pl -  is a list of prefixes
    # Strict - should tested prefix be exactly matched
    # or should be more specific as well
    #
    def generate_prefix_list(self,name,pl,strict=True):
        raise Excepton("Not implemented")
    

def get_profile_class(name):
    module=__import__("noc.sa.profiles."+name,globals(),locals(),["Profile"])
    return getattr(module,"Profile")