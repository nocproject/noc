# ---------------------------------------------------------------------
# SA Profile Base
# ---------------------------------------------------------------------
# Copyright (C) 2007-2020 The NOC Project
# See LICENSE for details
# ---------------------------------------------------------------------

# Python modules
import re
import functools
import warnings
from itertools import product

# Third-party modules
from typing import Dict, Callable, Union, Optional, List, Tuple

# NOC modules
from noc.core.ip import IPv4
from noc.sa.interfaces.base import InterfaceTypeError
from noc.core.confdb.collator.typing import PortItem
from noc.core.ecma48 import strip_control_sequences
from noc.core.handler import get_handler
from noc.core.comp import smart_text, smart_bytes
from noc.core.deprecations import RemovedInNOC2003Warning
from noc.core.text import alnum_key


class BaseProfileMetaclass(type):
    BINARY_ATTRS = (
        "command_submit",
        "pattern_username",
        "pattern_password",
        "pattern_super_password",
        "pattern_prompt",
        "pattern_unprivileged_prompt",
        "pattern_syntax_error",
        "pattern_operation_error",
        "username_submit",
        "password_submit",
        "command_super",
    )

    def __new__(mcs, name, bases, attrs):
        n = type.__new__(mcs, name, bases, attrs)
        n.rogue_char_cleaners = n._get_rogue_chars_cleaners()
        #
        if n.command_more:
            warnings.warn(
                "%s: 'command_more' is deprecated and will be removed in NOC 20.3" % n.name,
                RemovedInNOC2003Warning,
            )
        if isinstance(n.pattern_more, (str, bytes)):
            warnings.warn(
                "%s: 'command_more' must be a list of (pattern, command). "
                "Support for textual 'command_more' will be removed in NOC 20.3" % n.name,
                RemovedInNOC2003Warning,
            )
            n.pattern_more = [(n.pattern_more, n.command_more)]
            n.command_more = None
        # Fix binary attributes
        for attr in mcs.BINARY_ATTRS:
            v = getattr(n, attr, None)
            if v is not None and isinstance(v, str):
                warnings.warn(
                    "%s: '%s' must be of binary type. Support for text values will be removed in NOC 20.3"
                    % (n.name, attr),
                    RemovedInNOC2003Warning,
                )
                setattr(n, attr, smart_bytes(v))
        # Fix command_more
        pattern_more = []
        for pattern, cmd in n.pattern_more:
            if not isinstance(pattern, bytes):
                warnings.warn(
                    "%s: 'pattern_more' %r pattern must be of binary type. "
                    "Support for text values will be removed in NOC 20.2" % (n.name, pattern)
                )
                pattern = smart_bytes(pattern)
            if isinstance(cmd, str):
                warnings.warn(
                    "%s: 'pattern_more' %r command must be of binary type. "
                    "Support for text values will be removed in NOC 20.2" % (n.name, cmd)
                )
                cmd = smart_bytes(cmd)
            pattern_more += [(pattern, cmd)]
        n.pattern_more = pattern_more
        # Build patterns
        n.patterns = n._get_patterns()
        # Build effective snmp_display_hints for subclasses
        if n.name:
            snmp_display_hints = {}
            for b in bases:
                if issubclass(b, BaseProfile):
                    snmp_display_hints.update(b.snmp_display_hints)
            snmp_display_hints.update(attrs.get("snmp_display_hints", {}))
            n.snmp_display_hints = {
                k: snmp_display_hints[k] for k in snmp_display_hints if snmp_display_hints[k]
            }
        return n


class BaseProfile(object, metaclass=BaseProfileMetaclass):
    """
    Equipment profile. Contains all equipment personality and specific
    """

    name = None
    """
    Profile name in form <vendor>.<system>
    """
    #
    # Device capabilities
    #

    supported_schemes = []  # @todo: Deprecated
    """
    A list of supported access schemes.
    Access schemes constants are defined
    in noc.sa.protocols.sae_pb2
    (TELNET, SSH, HTTP, etc)
    Deprecated
    """

    pattern_username = rb"([Uu]ser ?[Nn]ame|[Ll]ogin): ?"
    """
    List[str]: Regular expression to catch user name prompt. Usually during telnet sessions)
    """

    pattern_password = rb"[Pp]ass[Ww]ord: ?"
    """
    Optional[regexp]: Regulal expression to catch password prompt (Telnet/SSH sessions)
    """

    pattern_super_password = None
    """
    Optional[regexp]: Regular expression to catch implicit super password prompt
    (Telnet/SSH sessions)
    """

    pattern_prompt = rb"^\S*[>#]"
    """
    Optional[regexp]: Regular expression to catch command prompt (CLI Sessions)
    """

    pattern_unprivileged_prompt = None
    """
    Optional[regexp]: Regular expression to catch unpriveleged mode command prompt
    (CLI Session)
    """

    pattern_more = rb"^---MORE---"
    """
    Optional[regexp]: Regular expression to catch pager
    (Used in command results)
    If pattern_more is string, send command_more
    If pattern_more is a list of (pattern,command) send appropriate command
    """

    pattern_syntax_error = None
    """
    Optional[regexp]: Regular expression (string or compiled) to catch the syntax errors in cli output.
    If CLI output matches pattern_syntax_error, then CLISyntaxError exception raised
    """

    pattern_operation_error = None
    """
    Optional[regexp]: Regular expression (string or compiled) to catch the CLI commands errors in cli output.
    If CLI output matches pattern_syntax_error and not matches
    pattern_syntax_error, then CLIOperationError exception raised
    """

    pattern_start_setup = None
    """
    Optional[regexp]: Regular expression to start setup sequence
    defined in setup_sequence list
    """

    pattern_multiline_commands = None
    """
    String or list of string to recognize continued multi-line commands
    Multi-line commands must be sent at whole, as the prompt will be
    not available until end of command
    NB: Sending logic is implemented in *commands* script

    Examples:
    r"^.+\\" -- treat trailing backspace as continuation
    r"banner\\s+login\\s+(\\S+)" -- continue until matched group   # noqa: W605
    """

    pattern_mml_end = None
    """
    MML end of block pattern
    """

    pattern_mml_continue = None
    """
    MML continue pattern
    """

    can_strip_hostname_to = None
    """
    Device can strip long hostname in various modes i.e
    my.very.long.hostname# converts to
    my.very.long.hos(config)#
    In this case set `can_strip_hostname_to` = 16
    None by default
    """

    command_more = b"\n"
    """
    bytes: Sequence to be send to list forward pager
    If pattern_more is string and is matched
    """

    command_submit = b"\n"
    """
    bytes: Sequence to be send at the end of all CLI commands
    """

    username_submit = None
    """
    Sequence to submit username. Use "\n" if None
    """

    password_submit = None
    """
    Sequence to submit password. Use "\n" if None
    """

    setup_script = None
    """
    Callable accepting script instance
    to set up additional script attributes
    and methods. Use Profile.add_script_method()
    to add methods
    """

    setup_session = None
    """
    Callable accepting script instance to set up session.
    """

    shutdown_session = None
    """
    Callable accepting script instance
    to finaly close session
    """

    setup_http_session = None
    """
    Callable accepting script instance to set up http session
    """

    http_request_middleware = None
    """
    List of middleware names to be applied to each HTTP request
    Refer to core.script.http.middleware for details
    Middleware may be set as
      * name
      * handler, leading to BaseMiddleware instance
      * (name, config)
      * (handler, config)
    Where config is dict of middleware's constructor parameters
    """

    shutdown_http_session = None
    """
    Callable acceptings script instance to finaly close http session
    """

    command_disable_pager = None
    """
    Sequence to disable pager
    """

    command_exit = None
    """
    Sequence to gracefully close session
    """

    command_super = None
    """
    Sequence to enable priveleged mode
    """

    command_enter_config = None
    """
    Sequence to enter configuration mode
    """

    command_leave_config = None
    """
    Sequence to leave configuration mode
    """

    command_save_config = None
    """
    Sequence to save configuration
    """

    send_on_syntax_error = None
    """
    String or callable to send on syntax error to perform cleanup
    Callable accepts three arguments:
      * cli instance
      * command that caused syntax error
      * error response.
    Coroutines are also accepted.
    SyntaxError exception will be raised after cleanup procedure

    """

    rogue_chars = [b"\r"]
    """
    List of chars to be stripped out of input stream
    before checking any regular expressions
    (when Action.CLEAN_INPUT==True)
    """

    telnet_send_on_connect = None
    """
    String to send just after telnet connect is established
    """

    telnet_slow_send_password = False
    """
    Password sending mode for telnet
      False - send password at once
      True - send password by characters
    """

    telnet_naws = b"\x00\x80\x00\x80"
    """
    Telnet NAWS negotiation
    """

    setup_sequence = None
    """
    List of strings containing setup sequence
    Setup sequence is initialized on pattern_start_setup during
    startup phase
    Strings sending one-by-one, waiting for response after
    each string, excluding last one
    """

    requires_netmask_conversion = False
    """
    Does the equipment supports bitlength netmasks
    or netmask should be converted to traditional formats
    """

    max_scripts = None
    """
    Upper concurrent scripts limit, if set
    """

    cli_timeout_start = 50
    """
    CLI timeouts
    Timeout between connection established and login prompt
    """

    cli_timeout_user = 30
    """
    Timeout after user name provided
    """

    cli_timeout_password = 30
    """
    Timeout after password provided
    """

    cli_timeout_super = 10
    """
    Timeout after submitting *command_super*
    """

    cli_timeout_setup = 10
    """
    Timeout waiting next setup sequence response
    """

    cli_timeout_prompt = 3600
    """
    Timeout until next prompt
    """

    cli_retries_super_password = 1
    """
    Amount of retries for enable passwords
    Increase if box asks for enable password twice
    """

    cli_retries_unprivileged_mode = 1
    """
    Amount of retries for unprivileged prompt
    Increase if box send unprivileged prompt twice
    """

    snmp_display_hints: Dict[str, Optional[Callable[[str, bytes], Union[str, bytes]]]] = {}
    """
    Additional hints for snmp binary OctetString data processing
    Contains mapping of
    oid -> render_callable
    if render_callable is None, translation is disabled and binary data processed by default way
    Otherwise it must be a callable, accepting (oid, raw_data) parameter
    where oid is varbind's oid value, while raw_data is raw binary data of varbind value.
    Callable should return str
    It is possible to return bytes in very rare specific cases,
    when you have intention to process binary output in script directly
    """

    snmp_metrics_get_chunk = 15
    """
    Aggregate up to *snmp_metrics_get_chunk* oids
    to one SNMP GET request
    """

    snmp_metrics_get_timeout = 3
    """
    Timeout for snmp GET request
    """

    snmp_ifstatus_get_chunk = 15
    """
    Aggregate up to *snmp_ifstatus_get_chunk* oids
    to one SNMP GET request for get_interface_status_ex
    """

    snmp_ifstatus_get_timeout = 2
    """
    Timeout for snmp GET request for get_interface_status_ex
    """

    snmp_response_parser: Optional[Callable] = None
    """
    _ResponseParser for customized SNMP response processing.
    Broken SNMP implementations are urged to use `parse_get_response_strict`
    """

    snmp_rate_limit: Dict[str, Optional[float]] = {}
    """
    matcher_name -> snmp rate limit
    for default get_snmp_rate_limit() implementation
    """

    enable_cli_session = True
    """
    Allow CLI sessions by default
    """

    batch_send_multiline = True
    """
    True - Send multiline command at once
    False - Send multiline command line by line
    """

    mml_header_separator = "\r\n\r\n"
    """
    String to separate MML response header from body
    """

    mml_always_quote = False
    """
    Always enclose MML command arguments with quotes
    False - pass integers as unquoted
    """

    config_tokenizer = None
    """
    Config tokenizer name, from noc.core.confdb.tokenizer.*
    """

    config_tokenizer_settings = {}
    """
    Configuration for config tokenizer
    """

    config_normalizer = None
    """
    Config normalizer handler
    """

    config_normalizer_settings = {}
    """
    Config normalizer settings
    """

    confdb_defaults = None
    """
    List of confdb default tokens
    To be appended on every confdb initiation
    """

    config_applicators = None
    """
    Config applicators
    List of (<applicator handler>, <applicator settings>) or <applicator handler>
    """

    default_config_applicators = [
        "noc.core.confdb.applicator.rebase.RebaseApplicator",
        "noc.core.confdb.applicator.interfacetype.InterfaceTypeApplicator",
        "noc.core.confdb.applicator.adminstatus.DefaultAdminStatusApplicator",
        "noc.core.confdb.applicator.fitype.DefaultForwardingInstanceTypeApplicator",
        "noc.core.confdb.applicator.lldpstatus.DefaultLLDPStatusApplicator",
        "noc.core.confdb.applicator.loopdetectstatus.DefaultLoopDetectStatusApplicator",
        "noc.core.confdb.applicator.stpstatus.DefaultSTPStatusApplicator",
        "noc.core.confdb.applicator.stppriority.DefaultSTPPriorityApplicator",
        "noc.core.confdb.applicator.cdpstatus.DefaultCDPStatusApplicator",
        "noc.core.confdb.applicator.ntp.DefaultNTPModeApplicator",
        "noc.core.confdb.applicator.ntp.DefaultNTPVersionApplicator",
        "noc.core.confdb.applicator.systemaaaservicelocal.DefaultSystemAAAServiceLocalApplicator",
        "noc.core.confdb.applicator.systemaaaorder.DefaultSystemAAAOrderApplicator",
        "noc.core.confdb.applicator.systemuserclass.DefaultUserClassApplicator",
        "noc.core.confdb.applicator.systemaaasourceaddresslookup.DefaultAAASourceAddressLookupApplicator",
        # Finally apply meta
        "noc.core.confdb.applicator.meta.MetaApplicator",
    ]
    """
    List of default applicators
    Activated by ConfDB `hints` section
    """

    collators = [
        "noc.core.confdb.collator.profile.ProfileCollator",
        "noc.core.confdb.collator.ifname.IfNameCollator",
    ]

    """
    Collators
    List of (<collator handler>, <collator settings>) or <collator_handler>
    """

    matchers = {}
    """
    Matchers are helper expressions to calculate and fill
    script's is_XXX properties
    """

    patterns = {}
    """
    Filled by metaclass
    """

    def convert_prefix(self, prefix):
        """
        Convert ip prefix to the format accepted by router's CLI

        ```python
        >>> BaseProfile().convert_prefix("192.168.2.0/24")
        '192.168.2.0/24'

        >>> BaseProfile().convert_prefix("192.168.2.0 255.255.255.0")
        '192.168.2.0 255.255.255.0'
        ```
        :param str prefix: IP Prefix
        :return: IP MASK notation
        :rtype: str
        """
        if "/" in prefix and self.requires_netmask_conversion:
            prefix = IPv4(prefix)
            return "%s %s" % (prefix.address, prefix.netmask.address)
        return prefix

    def convert_mac_to_colon(self, mac):
        """
        Leave 00:11:22:33:44:55 style MAC-address untouched

        ```python
        >>> BaseProfile().convert_mac_to_colon("00:11:22:33:44:55")
        '00:11:22:33:44:55'

        >>> BaseProfile().convert_mac_to_colon("00:11:22:33:44:55")
        '0011:2233:4455'
        ```
        :param str mac:
        :return: MAC-address HH:HH:HH:HH:HH:HH
        :rtype: str
        """
        return mac

    def convert_mac_to_cisco(self, mac):
        """
        Convert 00:11:22:33:44:55 style MAC-address to 0011.2233.4455

        ```python
        >>> BaseProfile().convert_mac_to_cisco("00:11:22:33:44:55")
        '0011.2233.4455'
        ```
        :param str mac: HH:HH:HH:HH:HH:HH

        :return: MAC-address HHHH.HHHH.HHHH
        :rtype: str
        """
        v = mac.replace(":", "").lower()
        return "%s.%s.%s" % (v[:4], v[4:8], v[8:])

    def convert_mac_to_huawei(self, mac):
        """
        Convert 00:11:22:33:44:55 style MAC-address to 0011-2233-4455

        ```python
        >>> BaseProfile().convert_mac_to_huawei("00:11:22:33:44:55")
        '0011-2233-4455'
        ```
        :return: MAC-address HHHH-HHHH-HHHH
        :rtype: str
        """
        v = mac.replace(":", "").lower()
        return "%s-%s-%s" % (v[:4], v[4:8], v[8:])

    def convert_mac_to_dashed(self, mac):
        """
        Convert 00:11:22:33:44:55 style MAC-address to 00-11-22-33-44-55

        ```python
        >>> BaseProfile().convert_mac_to_dashed("00:11:22:33:44:55")
        '00-11-22-33-44-55'
        ```
        :param str mac: MAC-address HH:HH:HH:HH:HH:HH
        :return: MAC-address HH-HH-HH-HH-HH-HH
        :rtype: str
        """
        v = mac.replace(":", "").lower()
        return "%s-%s-%s-%s-%s-%s" % (v[:2], v[2:4], v[4:6], v[6:8], v[8:10], v[10:])

    convert_mac = convert_mac_to_colon
    """
    Convert 00:11:22:33:44:55 style MAC-address to local format
    Can be changed in derived classes
    """

    def convert_interface_name(self, s):
        """
        Normalize interface name

        :param str s: Interface Name

        :return: Normalize interface name
        :rtype: str
        """
        return s

    # Cisco-like translation
    rx_cisco_interface_name = re.compile(
        r"^(?P<type>[a-z]{2})[a-z\-]*\s*"
        r"(?P<number>\d+(/\d+(/\d+(/\d+)?)?)?(\.\d+(/\d+)*(\.\d+)?)?(:\d+(\.\d+)*)?(/[a-z]+\d+(\.\d+)?)?(A|B)?)$",
        re.IGNORECASE,
    )

    def convert_interface_name_cisco(self, s):
        """
        ```python
        >>> BaseProfile().convert_interface_name_cisco("Gi0")
        'Gi 0'
        >>> BaseProfile().convert_interface_name_cisco("GigabitEthernet0")
        'Gi 0'
        >>> BaseProfile().convert_interface_name_cisco("Gi 0")
        'Gi 0'
        >>> BaseProfile().convert_interface_name_cisco("tengigabitethernet 1/0/1")
        'Te 1/0/1'
        >>> BaseProfile().convert_interface_name_cisco("tengigabitethernet 1/0/1.5")
        'Te 1/0/1.5'
        >>> BaseProfile().convert_interface_name_cisco("Se 0/1/0:0")
        'Se 0/1/0:0'
        >>> BaseProfile().convert_interface_name_cisco("Se 0/1/0:0.10")
        'Se 0/1/0:0.10'
        >>> BaseProfile().convert_interface_name_cisco("ATM1/1/ima0")
        'At 1/1/ima0'
        >>> BaseProfile().convert_interface_name_cisco("Port-channel5B")
        'Po 5B'
        ```
        """
        match = self.rx_cisco_interface_name.match(s)
        if not match:
            raise InterfaceTypeError("Invalid interface '%s'" % s)
        return "%s %s" % (match.group("type").capitalize(), match.group("number"))

    def root_interface(self, name):
        """
        Returns root interface

        ```python
        >>> BaseProfile().root_interface("Gi 0/1")
        'Gi 0/1'
        >>> BaseProfile().root_interface("Gi 0/1.15")
        'Gi 0/1'
        ```
        """
        name = name.split(".")[0]
        name = name.split(":")[0]
        return name

    def get_interface_names(self, name):
        """
        Return possible alternative interface names,
        i.e. for LLDP discovery *Local* method
        Can be overriden to achieve desired behavior

        :param str name: Interface Name

        :return: List Alternative interface names
        :rtype: list
        """
        return []

    def get_linecard(self, interface_name):
        """
        Returns linecard number related to interface

        ```python
        >>> BaseProfile().get_linecard("Gi 4/15")
        4
        >>> BaseProfile().get_linecard("Lo")
        >>> BaseProfile().get_linecard("ge-1/1/0")
        1
        ```
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
        r"^[a-z]{2}[\- ](?P<number>\d+)(/\d+)?/\d+/\d+([\:\.]\S+)?$", re.IGNORECASE
    )
    # D-Link-like translation
    rx_num2 = re.compile(r"^(?P<number>\d+)[\:\/]\d+$")

    def get_stack_number(self, interface_name):
        """
        Returns stack number related to interface

        ```python
        >>> BaseProfile().get_stack_number("Gi 1/4/15")
        1
        >>> BaseProfile().get_stack_number("Lo")
        >>> BaseProfile().get_stack_number("Te 2/0/1.5")
        2
        >>> BaseProfile().get_stack_number("Se 0/1/0:0.10")
        0
        >>> BaseProfile().get_stack_number("3:2")
        3
        >>> BaseProfile().get_stack_number("3/2")
        3
        ```
        """
        match = self.rx_num1.match(interface_name)
        if match:
            return int(match.group("number"))
        else:
            match = self.rx_num2.match(interface_name)
            if match:
                return int(match.group("number"))
        return None

    rx_connection_path = re.compile(r".*?(\d+|\d+/\d+)(_\w+|\.\d+)?$")

    def get_connection_path(self, name: str) -> str:
        """
        Return interface path by Inventory connection name

        ```python
        >>> BaseProfile().get_stack_number("Gi 1/4/15")
        1
        >>> BaseProfile().get_stack_number("Lo")
        >>> BaseProfile().get_stack_number("Te 2/0/1.5")
        1
        >>> BaseProfile().get_stack_number("Se 0/1/0:0.10")
        0
        >>> BaseProfile().get_stack_number("3:2")
        2
        >>> BaseProfile().get_stack_number("3/2")
        2
        >>> BaseProfile().get_stack_number("GigabitEthernet X/0/1")
        0/1
        >>> BaseProfile().get_stack_number("GigabitEthernet1_sfp")
        1
        >>> BaseProfile().get_stack_number("Gi1_sfp")
        1
        >>> BaseProfile().get_stack_number("sfp 9")
        9
        ```
        :param name: Connection Name
        :return:
        """
        if name.isdigit():
            return name
        match = self.rx_connection_path.match(name)
        if match:
            return match.group(1)
        return name

    proto_prefixes = {
        "TransEth40G": ["Fo"],
        "10GBASE": ["Te", "Xg"],
        "TransEth10G": ["Te", "Xg", "XGigabitEthernet"],
        "TransEth1G": ["Gi", "Ge", "GigabitEthernet"],
        "1000BASE": ["Gi", "Ge", "GigabitEthernet"],
        "100BASE": ["Fa"],
        "TransEth100M": ["Fa"],
        "10BASE": ["Eth", "Ethernet"],
    }

    port_splitter = " "

    def get_protocol_prefixes(self, protocols: List[str]) -> List[str]:
        """
        Return interface prefix by Protocol
        :param protocols: Protocols code list
        :return:
        """
        for pp in self.proto_prefixes:
            for p in protocols:
                if p.startswith(pp):
                    return self.proto_prefixes[pp]
        return []

    def get_interfaces_by_port(self, port: PortItem) -> List[str]:
        """
        1. If device is not stackable and not module (len path) - return slot num
        2. Append num from last path element
        3. If device supported stack - add first stack_member or 0
        4. Reverse path
        5. Product all variants with protocol prefix
        :param port:
        :return:
        """
        if len(port.path) <= 1 and port.stack_num is None:
            return [port.name]
        r: List[str] = []
        x = []
        for p in reversed(port.path):
            x.insert(0, self.get_connection_path(p.c_name))
        r.append("/".join(x))
        if port.stack_num is not None:
            r.append("/".join([str(port.stack_num)] + x))
        protocol_prefixes = self.get_protocol_prefixes(port.protocols)
        if not protocol_prefixes:
            return r
        return [self.port_splitter.join(p) for p in product(protocol_prefixes, r, repeat=1)]

    def generate_prefix_list(self, name, pl):
        """
        Generate prefix list:

        :param str name: name of prefix list
        :param List[str] pl: is a list of (prefix, min_len, max_len)

        Strict - should tested prefix be exactly matched
        or should be more specific as well
        Can be override to achieve desired behavior

        Not implemented in Base Class
        """
        raise NotImplementedError()

    config_volatile = None
    """
    Volatile strings:
    A list of strings can be changed over time, which
    can be sweeped out of config safely or None
    Strings are regexpes, compiled with re.DOTALL|re.MULTILINE
    """

    def cleaned_input(self, input: bytes) -> bytes:
        """
        Preprocessor to clean up and normalize input from device.
        Delete ASCII sequences by default.
        Can be overriden to achieve desired behavior

        > *ECMA-48 control sequences processing*
        > ::: noc.core.ecma48.strip_control_sequences
            rendering:
                show_category_heading: false
                show_root_toc_entry: false
                show_source: false
        :param input: Input text for clean

        :return: Text with strip control Sequences
        """
        return strip_control_sequences(input)

    def clean_rogue_chars(self, s: bytes) -> bytes:
        """
        Clean up config. Wipe out volatile strings before returning result

        :param s: Configuration

        :return: Clean up configuration
        """
        if self.rogue_chars:
            for cleaner in self.rogue_char_cleaners:
                s = cleaner(s)
        return s

    def cleaned_config(self, cfg):
        """
        Clean up config. Wipe out volatile strings before returning result

        :param str cfg: Configuration

        :return: Clean up configuration
        :rtype: str
        """
        if self.config_volatile:
            # Wipe out volatile strings before returning result
            for r in self.config_volatile:
                rx = re.compile(r, re.DOTALL | re.MULTILINE)
                cfg = rx.sub("", cfg)
        # Prevent serialization errors
        return smart_text(cfg, errors="ignore")

    def clean_lldp_neighbor(self, obj, neighbor):
        """
        Normalize and rewrite IGetLLDPNeighbors.neighbors structure
        in LLDP topology discovery.
        Remote object profile's .clean_lldp_neighbor() used

        :param obj: Managed Object reference
        :param neighbor: `IGetLLDPNeighbors.neighbors` item
        :return: IGetLLDPNeighbors.neighbors item
        """
        return neighbor

    def get_lacp_port_by_id(self, port_id: int) -> Optional[str]:
        """
        Return possible port aliases by LACP Port id,
        i.e. for LACP discovery method without script support
        Can be overriden to achieve desired behavior
        """
        return None

    @staticmethod
    def add_script_method(script, name, method):
        f = functools.partial(method, script)
        if not hasattr(f, "__name__"):
            setattr(f, "__name__", name)
        setattr(script, name, f)

    @classmethod
    def cmp_version(cls, v1, v2) -> Optional[int]:
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

        p1, p2 = alnum_key(v1), alnum_key(v2)
        # cmp-like semantic
        return (p1 > p2) - (p1 < p2)

    @classmethod
    def get_interface_type(cls, name):
        """
        Return IGetInterface-compatible interface type

        :param str name: Normalized interface name

        :return: Optional[str]
        """
        return None

    @classmethod
    def initialize(cls):
        """
        Called once by profile loader
        """

        def compile(pattern):
            if not pattern:
                return None
            if isinstance(pattern, str):
                return re.compile(pattern)
            if isinstance(pattern, bytes):
                return re.compile(pattern)
            return pattern

        cls.rx_pattern_syntax_error = compile(cls.pattern_syntax_error)
        cls.rx_pattern_operation_error = compile(cls.pattern_operation_error)
        cls.rx_pattern_operation_error_str = compile(smart_text(cls.pattern_operation_error))

    @classmethod
    def get_telnet_naws(cls) -> bytes:
        return cls.telnet_naws

    @classmethod
    def allow_allow_asymmetric_link(cls, method: str) -> bool:
        """Allow create asymmetric link for method"""
        return False

    @classmethod
    def allow_cli_session(cls, platform, version):
        return cls.enable_cli_session

    @classmethod
    async def send_backspaces(cls, cli, command, error_text):
        # Send backspaces to clean up previous command
        await cli.stream.write(b"\x08" * len(command))
        # Send command_submit to force prompt
        await cli.stream.write(cls.command_submit)
        # Wait until prompt
        await cli.read_until_prompt()

    def get_mml_login(self, script):
        """
        Generate MML login command. .get_mml_command may be used for formatting
        :param script: BaseScript instance
        :return: Login command
        """
        raise NotImplementedError()

    def get_mml_command(self, cmd, **kwargs):
        """
        Generate MML command
        :param cmd:
        :param kwargs:
        :return:
        """

        def qi(s):
            return '"%s"' % s

        def nqi(s):
            if isinstance(s, str):
                return '"%s"' % s
            else:
                return str(s)

        if ";" in cmd:
            return "%s\r\n" % cmd
        r = [cmd, ":"]
        if kwargs:
            if self.mml_always_quote:
                q = qi
            else:
                q = nqi
            r += [", ".join("%s=%s" % (k, q(kwargs[k])) for k in kwargs)]
        r += [";", "\r\n"]
        return "".join(r)

    def parse_mml_header(self, header):
        """
        Parse MML response header
        :param header: Response header
        :return: error code, error message
        """
        raise NotImplementedError()

    @classmethod
    def get_config_tokenizer(cls, object):
        """
        Returns config tokenizer name and settings.
        object.matchers.XXXX can be used
        :param object: ManagedObject instance
        :return: config tokenizer name, config tokenizer settings
        """
        return cls.config_tokenizer, cls.config_tokenizer_settings

    @classmethod
    def get_config_normalizer(cls, object):
        """
        Returns config normalizer name and settings
        :param object: ManagedObject instance
        :return:
        """
        return cls.config_normalizer, cls.config_normalizer_settings

    @classmethod
    def get_confdb_defaults(cls, object):
        """
        Returns a list of confdb defaults to be inserted on every ConfDB creation
        :param object:
        :return:
        """
        return cls.confdb_defaults

    @classmethod
    def iter_config_applicators(cls, object, confdb):
        """
        Returns config applicators and settings
        :param object: Managed Object instance
        :param confdb: ConfDB Engine instance
        :return: Iterate active config applicators (BaseApplicator instances)
        """

        def get_applicator(cfg):
            if isinstance(cfg, str):
                a_handler, a_cfg = cfg, {}
            else:
                a_handler, a_cfg = cfg
            if not a_handler.startswith("noc."):
                a_handler = "noc.sa.profiles.%s.confdb.applicator.%s" % (profile_name, a_handler)
            a_cls = get_handler(a_handler)
            assert a_cls, "Invalid applicator %s" % a_handler
            applicator = a_cls(object, confdb, **a_cfg)
            if applicator.can_apply():
                return applicator
            return None

        profile_name = object.get_profile().name
        # Apply default applicators
        if cls.default_config_applicators:
            for acfg in cls.default_config_applicators:
                a = get_applicator(acfg)
                if a:
                    yield a
        # Apply profile local applicators
        if cls.config_applicators:
            for acfg in cls.config_applicators:
                a = get_applicator(acfg)
                if a:
                    yield a

    @classmethod
    def iter_collators(cls, obj):
        def get_collator(cfg):
            if isinstance(cfg, str):
                c_handler, c_cfg = cfg, {"profile": obj.get_profile()}
            else:
                c_handler, c_cfg = cfg
            if not c_handler.startswith("noc."):
                c_handler = f"noc.sa.profiles.{profile_name}.confdb.collator.{c_handler}"
            c_cls = get_handler(c_handler)
            assert c_cls, "Invalid collator %s" % c_handler
            return c_cls(**c_cfg)

        profile_name = obj.get_profile().name
        if cls.collators:
            for c_cfg in cls.collators:
                c = get_collator(c_cfg)
                if c:
                    yield c

    @classmethod
    def get_http_request_middleware(cls, script):
        """
        Returns list of http_request_middleware.
        matchers.XXXX can be used?
        :param script: Script instance
        :return:
        """
        return cls.http_request_middleware

    @classmethod
    def get_snmp_display_hints(cls, script):
        """
        Returns a dict of snmp display_hints mapping.
        matchers.XXXX can be used
        :param script: Script instance
        :return:
        """
        return cls.snmp_display_hints

    @classmethod
    def get_snmp_response_parser(cls, script) -> Optional[Callable]:
        return cls.snmp_response_parser

    @classmethod
    def has_confdb_support(cls, object):
        tcls, _ = cls.get_config_tokenizer(object)
        if not tcls:
            return False
        ncls, _ = cls.get_config_normalizer(object)
        if not ncls:
            return False
        return True

    @classmethod
    def _get_patterns(cls):
        """
        Return dict of compiled regular expressions
        """

        def get_commands(pattern_more) -> List[Union[bytes, Dict[Tuple[str, ...], str]]]:
            commands = []
            for x in pattern_more:
                c = x[1]
                if isinstance(c, bytes):
                    commands += [c]
                elif isinstance(c, dict):
                    cnew = {}
                    for ck, cv in c.items():
                        if isinstance(ck, str):
                            cnew[(ck,)] = cv
                        elif isinstance(ck, tuple):
                            cnew[ck] = cv
                        elif ck is None:
                            cnew[None] = cv
                    commands += [cnew]
            return commands

        patterns = {
            "username": re.compile(cls.pattern_username, re.DOTALL | re.MULTILINE),
            "password": re.compile(cls.pattern_password, re.DOTALL | re.MULTILINE),
            "prompt": re.compile(cls.pattern_prompt, re.DOTALL | re.MULTILINE),
        }
        if cls.pattern_unprivileged_prompt:
            patterns["unprivileged_prompt"] = re.compile(
                cls.pattern_unprivileged_prompt, re.DOTALL | re.MULTILINE
            )
        if cls.pattern_super_password:
            patterns["super_password"] = re.compile(
                cls.pattern_super_password, re.DOTALL | re.MULTILINE
            )
        if cls.pattern_start_setup:
            patterns["setup"] = re.compile(cls.pattern_start_setup, re.DOTALL | re.MULTILINE)
        # .more_patterns is a list of (pattern, command)
        more_patterns = [x[0] for x in cls.pattern_more]
        patterns["more_commands"] = get_commands(cls.pattern_more)
        # Merge pager patterns
        patterns["pager"] = re.compile(
            b"|".join(b"(%s)" % p for p in more_patterns), re.DOTALL | re.MULTILINE
        )
        patterns["more_patterns"] = [re.compile(p, re.MULTILINE | re.DOTALL) for p in more_patterns]
        patterns["more_patterns_commands"] = list(
            zip(patterns["more_patterns"], patterns["more_commands"])
        )
        return patterns

    @classmethod
    def _get_rogue_chars_cleaners(cls):
        def get_bytes_cleaner(s):
            def _inner(x):
                return x.replace(s, b"")

            return _inner

        def get_re_cleaner(s):
            def _inner(x):
                return s.sub(b"", x)

            return _inner

        chain = []
        if cls.rogue_chars:
            for rc in cls.rogue_chars:
                if isinstance(rc, str):
                    warnings.warn(
                        "%s: 'rogue_char' %r pattern must be of binary type. "
                        "Support for text values will be removed in NOC 20.2" % (cls.name, rc)
                    )
                    chain += [get_bytes_cleaner(smart_bytes(rc))]
                elif isinstance(rc, bytes):
                    chain += [get_bytes_cleaner(rc)]
                elif hasattr(rc, "sub"):
                    if not isinstance(rc.pattern, bytes):
                        # Recompile as binary re
                        warnings.warn(
                            "%s: 'rogue_char' %r pattern must be of binary type. "
                            "Support for text values will be removed in NOC 20.2"
                            % (cls.name, rc.pattern)
                        )
                        # Remove re.UNICODE flag
                        flags = rc.flags
                        if flags & re.UNICODE:
                            warnings.warn(
                                "%s: 'rogue_char' %r pattern cannot be compiled with re.UNICODE flag."
                                % (cls.name, rc.pattern)
                            )
                            flags &= ~re.UNICODE
                        rc = re.compile(smart_bytes(rc.pattern), flags)
                    chain += [get_re_cleaner(rc)]
                else:
                    raise ValueError("Invalid rogue char expression: %r" % rc)
        return chain

    def get_snmp_rate_limit(self, script) -> Optional[float]:
        if not self.snmp_rate_limit:
            return None
        limits = [
            v
            for k, v in self.snmp_rate_limit.items()
            if v is not None and getattr(script, k, False)
        ]
        if limits:
            return min(limits)
        return None
