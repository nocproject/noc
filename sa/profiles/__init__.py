# -*- coding: utf-8 -*-
##----------------------------------------------------------------------
## Copyright (C) 2007-2009 The NOC Project
## See LICENSE for details
##----------------------------------------------------------------------
"""
"""
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
    apps=["noc.sa"]
    exclude=["highlight"]
profile_registry=ProfileRegistry()

##
##
##
class ProfileBase(type):
    def __new__(cls,name,bases,attrs):
        m=type.__new__(cls,name,bases,attrs)
        m.scripts={}
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
    # Regular expression to catch first pager occurence.
    # (If differ from pattern_more)
    pattern_more_start=None
    # Regular expression to catch last pager occurence.
    # (If differ from pattern_more)
    pattern_more_end=None
    # Sequence to be send at the end of all CLI commands
    #
    command_submit="\n"
    # Sequence to be send to list forward pager
    #
    command_more="\n"
    # Sequence to be send to list pager at first occurence.
    # (If set to None command_more used)
    command_more_start=None
    # Sequence to be send to quit pager when paged to the end
    # (If set to None command_more used)
    command_more_end=None
    # Sequence to gracefully close session
    #
    command_exit="exit"
    # Sequence to enable priveleged mode
    #
    command_super=None
    # Sequence to enter configuration mode
    #
    command_enter_config=None
    # Sequence to leave configuration mode
    #
    command_leave_config=None
    # Sequence to save configuration
    #
    command_save_config=None
    # List of chars to be stripped out of input stream
    # before checking any regular expressions
    # (when Action.CLEAN_INPUT==True)
    rogue_chars=["\r"]
    ##
    ## Looking glass hilighting support
    ##
    
    # match.group(1) contains AS list <!> Deprecated
    pattern_lg_as_path_list=None
    # match.group(1) containts Best Path <!> Deprecated
    pattern_lg_best_path=None
    # Does the equipment supports bitlength netmasks
    # or netmask should be converted to traditional formats
    requires_netmask_conversion=False
    
    #
    # AS Path hilighting
    # Deprecated <!>
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
    # Leave 00:11:22:33:44:55 style MAC-address untouched
    #
    def convert_mac_to_colon(self,mac):
        return mac
    #
    # Convert 00:11:22:33:44:55 style MAC-address to 0011.2233.4455
    #
    def convert_mac_to_cisco(self,mac):
        v=mac.replace(":","").lower()
        return "%s.%s.%s"%(v[:4],v[4:8],v[8:])
    #
    # Convert 00:11:22:33:44:55 style MAC-address to 00-11-22-33-44-55
    #
    def convert_mac_to_dashed(self,mac):
        v=mac.replace(":","").lower()
        return "%s-%s-%s-%s-%s-%s"%(v[:2],v[2:4],v[4:6],v[6:8],v[8:10],v[10:])
    #
    # Convert 00:11:22:33:44:55 style MAC-address to local format
    # Can be changed in derived classes
    #
    convert_mac=convert_mac_to_colon
    
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
    # Volatile strings:
    # A list of strings can be changed over time, which
    # can be sweeped out of config safely or None
    # Strings are regexpes, compuled with re.DOTALL|re.MULTILINE
    #
    config_volatile=None
    #
    # Clean up config
    #
    def cleaned_config(self,cfg):
        if self.config_volatile:
            # Wipe out volatile strings before returning result
            for r in self.config_volatile:
                rx=re.compile(r,re.DOTALL|re.MULTILINE)
                cfg=rx.sub("",cfg)
        return unicode(cfg,"utf8","ignore").encode("utf8") # Prevent serialization errors
    #
    # Highligh config
    # Try to include profile's highlight module and use its ConfigLexer
    # Returns escaped HTML
    #
    def highlight_config(self,cfg):
        # Check for pygments available
        try:
            from pygments import highlight
        except ImportError:
            # No pygments, no highlighting. Return escaped HTML
            from django.utils.html import escape
            return "<pre><!--no pygments-->%s</pre>"%escape(cfg).replace("\n","<br/>")
        # Check for lexer available
        from pygments.lexers import TextLexer
        from noc.lib.highlight import NOCHtmlFormatter
        
        lexer=None
        for l in ["local.",""]: # Try to import local/ version first
            h_mod="noc.%ssa.profiles.%s.highlight"%(l,self.name)
            try:
                m=__import__(h_mod,{},{},"ConfigLexer")
                lexer=m.ConfigLexer
                break
            except ImportError:
                continue
            except AttributeError:
                continue
        if not lexer:
            lexer=TextLexer
        # Return highlighted text
        return highlight(cfg, lexer(), NOCHtmlFormatter())
