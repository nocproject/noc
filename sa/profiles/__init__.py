from noc.lib.ip import bits_to_netmask
from noc.lib.registry import Registry
import re
##
##
##
class ProfileRegistry(Registry):
    name="ProfileRegistry"
    subdir="profiles"
    classname="Profile"
profile_registry=ProfileRegistry()

##
##
##
class ProfileBase(type):
    def __new__(cls,name,bases,attrs):
        m=type.__new__(cls,name,bases,attrs)
        profile_registry.register(m.name,m)
        return m

##
## Abstract Profile
##
class Profile(object):
    __metaclass__=ProfileBase
    # Profile name
    name=None
    #
    # Device capabilities
    #
    
    #
    # A list of supported access schemes.
    # Access schemes constants are defined
    # in noc.sa.protocols.sae_pb2
    # (TELNET, SSH, HTTP, etc)
    #
    supported_schemes=[]
    # Regular expression to catch user name prompt
    # (Usually during telnet sessions)
    pattern_username="([Uu]sername|[Ll]ogin):"
    # Regulal expression to catch password prompt
    # (Telnet/SSH sessions)
    pattern_password="[Pp]assword:"
    # Regular expression to catch command prompt
    # (CLI Sessions)
    pattern_prompt=r"^\S*[>#]"
    # Regular expression to catch unpriveleged mode command prompt
    # (CLI Session)
    pattern_unpriveleged_prompt=None
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
    # Sequence to enable priveleged mode
    #
    command_super=None
    # List of chars to be stripped out of input stream
    # before checking any regular expressions
    # (For CLI action only)
    rogue_chars=["\r"]
    # Strip ANSI Escape Sequences out of input stream
    # before checking any regular expressions
    strip_ansi_escapes=True
    
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
    #
    # A list of commands to pull config via CLI
    # Should be a list of commands or None if not supported
    #
    command_pull_config=None
    #
    # Volatile strings:
    # A list of strings can be changed over time, which
    # can be sweeped out of config safely or None
    # Strings are regexpes, compuled with re.DOTALL|re.MULTILINE
    #
    config_volatile=None
    #
    # Skip first N lines of config output. None - skip no lines
    #
    config_skip_head=1
    ##
    ## HTTP Access
    ##
    
    #
    # HTTP Request Method to get config ("GET" or "POST")
    #
    method_pull_config=None
    #
    # HTTP Request path to get config (used with method_pull_config)
    #
    path_pull_config=None
    #
    # Config file name
    #
    file_pull_config=None
    #
    # Clean up config
    #
    def cleaned_config(self,cfg):
        if self.config_skip_head:
            # Wipe out first N lines
            cl=cfg.split("\n")
            if len(cl)>self.config_skip_head:
                cfg="\n".join(cl[self.config_skip_head:])
        if self.config_volatile:
            # Wipe out volatile strings before returning result
            for r in self.config_volatile:
                rx=re.compile(r,re.DOTALL|re.MULTILINE)
                cfg=rx.sub("",cfg)
        return cfg
