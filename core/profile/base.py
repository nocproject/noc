# -*- coding: utf-8 -*-
# ---------------------------------------------------------------------
# SA Profile Base
# ---------------------------------------------------------------------
# Copyright (C) 2007-2018 The NOC Project
# See LICENSE for details
# ---------------------------------------------------------------------

# Python modules
import re
import functools
# Third-party modules
import tornado.gen
# NOC modules
from noc.core.ip import IPv4
from noc.sa.interfaces.base import InterfaceTypeError
from noc.core.ecma48 import strip_control_sequences


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
    pattern_username = "([Uu]ser ?[Nn]ame|[Ll]ogin): ?"
    # Regulal expression to catch password prompt
    # (Telnet/SSH sessions)
    pattern_password = "[Pp]ass[Ww]ord: ?"
    # Regular expression to catch implicit super password prompt
    # (Telnet/SSH sessions)
    pattern_super_password = None
    # Regular expression to catch command prompt
    # (CLI Sessions)
    pattern_prompt = r"^\S*[>#]"
    # Regular expression to catch unpriveleged mode command prompt
    # (CLI Session)
    pattern_unprivileged_prompt = None
    # Regular expression to catch pager
    # (Used in command results)
    # If pattern_more is string, send command_more
    # If pattern_more is a list of (pattern,command)
    # send appropriate command
    pattern_more = "^---MORE---"
    # Regular expression to catch the syntax errors in cli output.
    # If CLI output matches pattern_syntax_error,
    # then CLISyntaxError exception raised
    pattern_syntax_error = None
    # Regular expression to catch the CLI commands errors in cli output.
    # If CLI output matches pattern_syntax_error and not matches
    # pattern_syntax_error, then CLIOperationError exception raised
    pattern_operation_error = None
    # Reqular expression to start setup sequence
    # defined in setup_sequence list
    pattern_start_setup = None
    # String or list of string to recognize continued multi-line commands
    # Multi-line commands must be sent at whole, as the prompt will be
    # not available until end of command
    # NB: Sending logic is implemented in *commands* script
    # Examples:
    # "^.+\\" -- treat trailing backspace as continuation
    # "banner\s+login\s+(\S+)" -- continue until matched group
    pattern_multiline_commands = None
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
    # Sequence to submit username. Use "\n" if None
    username_submit = None
    # Sequence to submit password. Use "\n" if None
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
    # String or callable to send on syntax error to perform cleanup
    # Callable accepts three arguments
    # * cli instance
    # * command that caused syntax error
    # * error response.
    # Coroutines are also accepted.
    # SyntaxError exception will be raised after cleanup procedure
    send_on_syntax_error = None
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
    telnet_naws = "\x00\x80\x00\x80"
    # List of strings containing setup sequence
    # Setup sequence is initialized on pattern_start_setup during
    # startup phase
    # Strings sending one-by-one, waiting for response after
    # each string, excluding last one
    setup_sequence = None
    # Does the equipment supports bitlength netmasks
    # or netmask should be converted to traditional formats
    requires_netmask_conversion = False
    # Upper concurrent scripts limit, if set
    max_scripts = None
    # Default config parser name. Full path to BaseParser subclass
    # i.e noc.cm.parsers.Cisco.IOS.switch.IOSSwitchParser
    # Can be overriden in get_parser method
    default_parser = None
    # CLI timeouts
    # Timeout between connection established and login prompt
    cli_timeout_start = 60
    # Timeout after user name provided
    cli_timeout_user = 30
    # Timeout after password provided
    cli_timeout_password = 30
    # Timeout after submitting *command_super*
    cli_timeout_super = 10
    # Timeout waiting next setup sequence response
    cli_timeout_setup = 10
    # Aggregate up to *snmp_metrics_get_chunk* oids
    # to one SNMP GET request
    snmp_metrics_get_chunk = 15
    # Timeout for snmp GET request
    snmp_metrics_get_timeout = 3
    # Allow CLI sessions by default
    enable_cli_session = True
    # True - Send multiline command at once
    # False - Send multiline command line by line
    batch_send_multiline = True
    # Matchers are helper expressions to calculate and fill
    # script's is_XXX properties
    matchers = {}

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

    def convert_mac_to_huawei(self, mac):
        """
        Convert 00:11:22:33:44:55 style MAC-address to 0011.2233.4455
        """
        v = mac.replace(":", "").lower()
        return "%s-%s-%s" % (v[:4], v[4:8], v[8:])

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
        r"^(?P<type>[a-z]{2})[a-z\-]*\s*"
        r"(?P<number>\d+(/\d+(/\d+)?)?(\.\d+(/\d+)*(\.\d+)?)?(:\d+(\.\d+)*)?(/[a-z]+\d+(\.\d+)?)?(A|B)?)$",
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

    # Cisco-like translation
    rx_num1 = re.compile(
        r"^[a-z]{2}[\- ](?P<number>\d+)/\d+/\d+([\:\.]\S+)?$", re.IGNORECASE)
    # D-Link-like translation
    rx_num2 = re.compile(r"^(?P<number>\d+)[\:\/]\d+$")

    def get_stack_number(self, interface_name):
        """
        Returns stack number related to interface
        >>> Profile().get_stack_number("Gi 1/4/15")
        1
        >>> Profile().get_stack_number("Lo")
        >>> Profile().get_stack_number("Te 2/0/1.5")
        2
        >>> Profile().get_stack_number("Se 0/1/0:0.10")
        0
        >>> Profile().get_stack_number("3:2")
        3
        >>> Profile().get_stack_number("3/2")
        3
        """
        match = self.rx_num1.match(interface_name)
        if match:
            return int(match.group("number"))
        else:
            match = self.rx_num2.match(interface_name)
            if match:
                return int(match.group("number"))
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
    # Strings are regexpes, compiled with re.DOTALL|re.MULTILINE
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
    def cmp_version(cls, v1, v2):
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
        p1 = [int(x) for x in v1.split(".")]
        p2 = [int(x) for x in v2.split(".")]
        # cmp-like semantic
        return (p1 > p2) - (p1 < p2)

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

    @classmethod
    def initialize(cls):
        """
        Called once by profile loader
        """
        if cls.pattern_syntax_error:
            cls.rx_pattern_syntax_error = re.compile(cls.pattern_syntax_error)
        else:
            cls.rx_pattern_syntax_error = None
        if cls.pattern_operation_error:
            cls.rx_pattern_operation_error = re.compile(cls.pattern_operation_error)
        else:
            cls.rx_pattern_operation_error = None

    @classmethod
    def get_telnet_naws(cls):
        return cls.telnet_naws

    @classmethod
    def allow_cli_session(cls, platform, version):
        return cls.enable_cli_session

    @classmethod
    @tornado.gen.coroutine
    def send_backspaces(cls, cli, command, error_text):
        # Send backspaces to clean up previous command
        yield cli.iostream.write("\x08" * len(command))
        # Send command_submit to force prompt
        yield cli.iostream.write(cls.command_submit)
        # Wait until prompt
        yield cli.read_until_prompt()
