# -*- coding: utf-8 -*-
##----------------------------------------------------------------------
## SA Profile Base
##----------------------------------------------------------------------
## Copyright (C) 2007-2015 The NOC Project
## See LICENSE for details
##----------------------------------------------------------------------

## Python modules
import re
## NOC modules
from noc.lib.ip import IPv4
from noc.sa.interfaces.base import InterfaceTypeError
from noc.lib.ecma48 import strip_control_sequences
import functools


class BaseProfile(object):
    """
    Equipment profile. Contains all equipment personality and specific
    """
    # Profile name in form <vendor>.<system>
    name = None
    #
    # Device capabilities
    #

    #
    # A list of supported access schemes.
    # Access schemes constants are defined
    # in noc.sa.protocols.sae_pb2
    # (TELNET, SSH, HTTP, etc)
    # @todo: Deprecated
    #
    supported_schemes = []
    # Regular expression to catch user name prompt
    # (Usually during telnet sessions)
    pattern_username = "([Uu]sername|[Ll]ogin):"
    # Regulal expression to catch password prompt
    # (Telnet/SSH sessions)
    pattern_password = "[Pp]assword:"
    # Regular expression to catch command prompt
    # (CLI Sessions)
    pattern_prompt = r"^\S*[>#]"
    # Regular expression to catch unpriveleged mode command prompt
    # (CLI Session)
    pattern_unpriveleged_prompt = None
    # Regular expression to catch pager
    # (Used in command results)
    # If pattern_more is string, send command_more
    # If pattern_more is a list of (pattern,command)
    # send appropriative command
    pattern_more = "^---MORE---"
    # Regular expression to catch the syntax errors in cli output.
    # If CLI output matches pattern_syntax_error,
    # then CLISyntaxError exception raised
    pattern_syntax_error = None
    # Regular expression to catch the CLI commands errors in cli output.
    # If CLI output matches pattern_syntax_error and not matches
    # pattern_syntax_error, then CLIOperationError exception raised
    pattern_operation_error = None
    # Device can strip long hostname in various modes
    # i.e
    # my.very.long.hostname# converts to
    # my.very.long.hos(config)#
    # In this case set can_strip_hostname_to = 16
    # None by default
    can_strip_hostname_to = None
    # Sequence to be send to list forward pager
    # If pattern_more is string and is matched
    command_more = "\n"
    # Sequence to be send at the end of all CLI commands
    command_submit = "\n"
    # Sequence to submit username. Use command_submit if None
    username_submit = None
    # Sequence to submit password. Use command_submit if None
    password_submit = None
    # Callable accepting script instance
    # to set up additional script attributes
    # and methods. Use Profile.add_script_method()
    # to add methods
    setup_script = None
    # Callable accepting script instance
    # to set up session.
    setup_session = None
    # Callable accepting script instance
    # to finaly close session
    shutdown_session = None
    # Sequence to disable pager
    #
    command_disable_pager = None
    # Sequence to gracefully close session
    #
    command_exit = None
    # Sequence to enable priveleged mode
    #
    command_super = None
    # Sequence to enter configuration mode
    #
    command_enter_config = None
    # Sequence to leave configuration mode
    #
    command_leave_config = None
    # Sequence to save configuration
    #
    command_save_config = None
    # List of chars to be stripped out of input stream
    # before checking any regular expressions
    # (when Action.CLEAN_INPUT==True)
    rogue_chars = ["\r"]
    # String to send just after telnet connect is established
    telnet_send_on_connect = None
    # Password sending mode for telnet
    # False - send password at once
    # True - send password by characters
    telnet_slow_send_password = False
    # Telnet NAWS negotiation
    telnet_naws = "\xff\xff\xff\xff"
    # Does the equipment supports bitlength netmasks
    # or netmask should be converted to traditional formats
    requires_netmask_conversion = False
    # Upper concurrent scripts limit, if set
    max_scripts = None
    # Default config parser name. Full path to BaseParser subclass
    # i.e noc.cm.parsers.Cisco.IOS.switch.IOSSwitchParser
    # Can be overriden in get_parser method
    default_parser = None

    def convert_prefix(self, prefix):
        """
        Convert ip prefix to the format accepted by router's CLI
        """
        if "/" in prefix and self.requires_netmask_conversion:
            prefix = IPv4(prefix)
            return "%s %s" % (prefix.address, prefix.netmask.address)
        return prefix

    def convert_mac_to_colon(self, mac):
        """
        Leave 00:11:22:33:44:55 style MAC-address untouched
        """
        return mac

    def convert_mac_to_cisco(self, mac):
        """
        Convert 00:11:22:33:44:55 style MAC-address to 0011.2233.4455
        """
        v = mac.replace(":", "").lower()
        return "%s.%s.%s" % (v[:4], v[4:8], v[8:])

    def convert_mac_to_dashed(self, mac):
        """
        Convert 00:11:22:33:44:55 style MAC-address to 00-11-22-33-44-55
        """
        v = mac.replace(":", "").lower()
        return "%s-%s-%s-%s-%s-%s" % (v[:2], v[2:4], v[4:6],
                                      v[6:8], v[8:10], v[10:])

    #
    # Convert 00:11:22:33:44:55 style MAC-address to local format
    # Can be changed in derived classes
    #
    convert_mac = convert_mac_to_colon

    def convert_interface_name(self, s):
        """
        Normalize interface name
        """
        return s

    # Cisco-like translation
    rx_cisco_interface_name = re.compile(
        r"^(?P<type>[a-z]{2})[a-z\-]*\s*(?P<number>\d+(/\d+(/\d+)?)?(\.\d+(/\d+)*(\.\d+)?)?(:\d+(\.\d+)*)?(/[a-z]+\d+(\.\d+)?)?(A|B)?)$",
        re.IGNORECASE
    )

    def convert_interface_name_cisco(self, s):
        """
        >>> Profile().convert_interface_name_cisco("Gi0")
        'Gi 0'
        >>> Profile().convert_interface_name_cisco("GigabitEthernet0")
        'Gi 0'
        >>> Profile().convert_interface_name_cisco("Gi 0")
        'Gi 0'
        >>> Profile().convert_interface_name_cisco("tengigabitethernet 1/0/1")
        'Te 1/0/1'
        >>> Profile().convert_interface_name_cisco("tengigabitethernet 1/0/1.5")
        'Te 1/0/1.5'
        >>> Profile().convert_interface_name_cisco("Se 0/1/0:0")
        'Se 0/1/0:0'
        >>> Profile().convert_interface_name_cisco("Se 0/1/0:0.10")
        'Se 0/1/0:0.10'
        >>> Profile().convert_interface_name_cisco("ATM1/1/ima0")
        'At 1/1/ima0'
        >>> Profile().convert_interface_name_cisco("Port-channel5B")
        'Po 5B'
        """
        match = self.rx_cisco_interface_name.match(s)
        if not match:
            raise InterfaceTypeError("Invalid interface '%s'" % s)
        return "%s %s" % (match.group("type").capitalize(),
                          match.group("number"))

    def root_interface(self, name):
        """
        Returns root interface
        >>> Profile().root_interface("Gi 0/1")
        'Gi 0/1'
        >>> Profile().root_interface("Gi 0/1.15")
        'Gi 0/1'
        """
        name = name.split(".")[0]
        name = name.split(":")[0]
        return name

    def get_interface_names(self, name):
        """
        Return possible alternative interface names,
        i.e. for LLDP discovery *Local* method
        """
        return []

    def get_linecard(self, interface_name):
        """
        Returns linecard number related to interface
        >>> Profile().get_linecard("Gi 4/15")
        4
        >>> Profile().get_linecard("Lo")
        >>> Profile().get_linecard("ge-1/1/0")
        1
        """
        if " " in interface_name:
            l, r = interface_name.split(" ")
        elif "-" in interface_name:
            l, r = interface_name.split("-")
        else:
            return None
        if "/" in r:
            return int(r.split("/", 1)[0])
        else:
            return None

    def generate_prefix_list(self, name, pl):
        """
        Generate prefix list:
        name - name of prefix list
        pl -  is a list of (prefix, min_len, max_len)
        Strict - should tested prefix be exactly matched
        or should be more specific as well
        """
        raise NotImplementedError()
    #
    # Volatile strings:
    # A list of strings can be changed over time, which
    # can be sweeped out of config safely or None
    # Strings are regexpes, compuled with re.DOTALL|re.MULTILINE
    #
    config_volatile = None

    def cleaned_input(self, input):
        """
        Preprocessor to clean up and normalize input from device.
        Delete ASCII sequences by default.
        Can be overriden to achieve desired behavior
        """
        return strip_control_sequences(input)

    def cleaned_config(self, cfg):
        """
        Clean up config
        """
        if self.config_volatile:
            # Wipe out volatile strings before returning result
            for r in self.config_volatile:
                rx = re.compile(r, re.DOTALL | re.MULTILINE)
                cfg = rx.sub("", cfg)
        # Prevent serialization errors
        return unicode(cfg, "utf8", "ignore").encode("utf8")

    def add_script_method(self, script, name, method):
        f = functools.partial(method, script)
        if not hasattr(f, "__name__"):
            setattr(f, "__name__", name)
        setattr(script, name, f)

    @classmethod
    def cmp_version(self, v1, v2):
        """
        Compare two versions.
        Must return:
           <0 , if v1<v2
            0 , if v1==v2
           >0 , if v1>v2
         None , if v1 and v2 cannot be compared

        Default implementation compares a versions in format
        N1. .. .NM
        """
        return cmp([int(x) for x in v1.split(".")],
                   [int(x) for x in v2.split(".")])

    @classmethod
    def get_parser(cls, vendor, platform, version):
        """
        Returns full path to BaseParser instance to be used
        as config parser. None means no parser for particular platform
        """
        return cls.default_parser

    @classmethod
    def get_interface_type(cls, name):
        """
        Return IGetInterface-compatible interface type
        :param Name: Normalized interface name
        """
        return None
