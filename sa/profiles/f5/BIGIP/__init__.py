# -*- coding: utf-8 -*-
##----------------------------------------------------------------------
## Vendor: f5
## OS:     BIG-IP
##----------------------------------------------------------------------
## Copyright (C) 2007-2009 The NOC Project
## See LICENSE for details
##----------------------------------------------------------------------
"""
"""
import noc.sa.profiles
from noc.sa.protocols.sae_pb2 import SSH


class Profile(noc.sa.profiles.Profile):
    name = "f5.BIGIP"
    supported_schemes = [SSH]
    pattern_username = "^([Uu]sername|[Ll]ogin):"
    pattern_prompt = r"^(\[(?P<hostprompt>[^\]]+)\]\s\S+\s#\s)|(.+?\(tmos\)# )"
    pattern_more = [
            (r"^(/var/tmp/shell\.out\.\S+|:)", " "),
            (r"^\(END\) ", "q"),
            (r"^Display all \d+ items\? \(y/n\)\s+", "y"),
            (r"^---\(less \d+%\)---", " "),
            (r"^\(END\)", "q"),
            ]

    def cleaned_input(self, input):
        input = input.replace("\x1b[24;1H\x1b[K", "\n")
        return super(Profile, self).cleaned_input(input)

    def setup_script(self, script):
        self.add_script_method(script, "tmsh", lambda: TMSHContextManager(script))


class TMSHContextManager(object):
    """
    Switch to tmsh.
    Usage:
    with self.tmsh():
        self.cli(....)
    """
    def __init__(self, script):
        self.script = script

    ##
    ## Entering context
    ##
    def __enter__(self):
        """
        Run tmsh and disable pager
        """
        self.script.debug("Entering tmsh")
        self.script.cli("tmsh")
        self.script.cli("modify /cli preference pager disabled")
    
    ##
    ## Leaving context
    ##
    def __exit__(self, exc_type, exc_val, exc_tb):
        """
        Leave tmsh
        """
        self.script.debug("Leaving tmsh")
        self.script.cli("quit")
        if exc_type:
            raise exc_type, exc_val
