# -*- coding: utf-8 -*-
##----------------------------------------------------------------------
## SA Script base
##----------------------------------------------------------------------
## Copyright (C) 2007-2015 The NOC Project
## See LICENSE for details
##----------------------------------------------------------------------

## Python modules
import re
import logging
import time
import itertools
import operator
## Third-party modules
from tornado.httpclient import HTTPClient, HTTPError
## NOC modules
from snmp.base import SNMP
from snmp.beef import BeefSNMP
from noc.lib.log import PrefixLoggerAdapter
from noc.lib.validators import is_int
from context import (ConfigurationContextManager, CacheContextManager,
                     IgnoredExceptionsContextManager)
from noc.core.profile.loader import loader as profile_loader
from noc.lib.solutions import get_solution


class BaseScript(object):
    """
    Service Activation script base class
    """
    class __metaclass__(type):
        """
        Process @match decorators
        """
        def __new__(mcs, name, bases, attrs):
            n = type.__new__(mcs, name, bases, attrs)
            n._execute_chain = sorted(
                (v for v in attrs.itervalues() if hasattr(v, "_seq")),
                key=operator.attrgetter("_seq")
            )
            return n

    # Script name in form of <vendor>.<system>.<name>
    name = None
    # Enable call cache
    # If True, script result will be cached and reused
    # during lifetime of parent script
    cache = False
    # Implemented interface
    interface = None
    # Scripts required by generic script.
    # For common scripts - empty list
    # For generics - list of pairs (script_name, interface)
    requires = []
    #
    base_logger = logging.getLogger(name or "script")
    #
    _x_seq = itertools.count()

    # Common errors
    class ScriptError(Exception):
        """Script error"""

    # LoginError = LoginError
    class CLISyntaxError(ScriptError):
        """Syntax error"""

    class CLIOperationError(ScriptError):
        """Operational CLI error"""
    # CLITransportError = CLITransportError
    # CLIDisconnectedError = CLIDisconnectedError
    # TimeOutError = TimeOutError

    class NotSupportedError(ScriptError):
        """Feature is not supported"""

    class UnexpectedResultError(ScriptError):
        """Unexpected result"""

    HTTPError = HTTPError

    hexbin = {
        "0": "0000", "1": "0001", "2": "0010", "3": "0011",
        "4": "0100", "5": "0101", "6": "0110", "7": "0111",
        "8": "1000", "9": "1001", "a": "1010", "b": "1011",
        "c": "1100", "d": "1101", "e": "1110", "f": "1111"
    }

    cli_protocols = {
        "telnet": "noc.core.script.cli.telnet.TelnetCLI",
        "ssh": "noc.core.script.cli.ssh.SSHCLI",
        "beef": "noc.core.script.cli.beef.BeefCLI"
    }

    def __init__(self, service, credentials,
                 args=None, capabilities=None,
                 version=None, parent=None, timeout=None,
                 name=None):
        self.service = service
        self.tos = self.service.config.tos
        self.pool = self.service.config.pool
        self.parent = parent
        name = name or self.name
        self.logger = PrefixLoggerAdapter(
            self.base_logger,
            "%s] [%s" % (self.name, credentials.get("address", "-"))
        )
        self.profile = profile_loader.get_profile(
            ".".join(name.split(".")[:2])
        )()
        self.credentials = credentials or {}
        self.version = version or {}
        self.capabilities = capabilities
        self.timeout = timeout or self.get_timeout()
        self.start_time = None
        self.args = self.clean_input(args or {})
        self.cli_stream = None
        if self.parent:
            self.snmp = self.root.snmp
        else:
            if self.credentials.get("beef"):
                self.snmp = BeefSNMP(self)
            else:
                self.snmp = SNMP(self)
        self.http = HTTPClient()
        self.to_disable_pager = not self.parent and self.profile.command_disable_pager
        self.to_shutdown_session = False
        self.scripts = ScriptsHub(self)
        self.is_cached = False  # Cache CLI and SNMP calls, if set
        # Suitable only when self.parent is None.
        # Cached results for scripts marked with "cache"
        self.call_cache = {}
        #
        if not parent and version and not name.endswith(".get_version"):
            self.logger.debug("Filling get_version cache with %s",
                              version)
            s = name.split(".")
            self.set_cache(
                "%s.%s.get_version" % (s[0], s[1]),
                {},
                version
            )

    def __call__(self, *args, **kwargs):
        self.args = kwargs
        return self.run()

    def clean_input(self, args):
        """
        Cleanup input parameters against interface
        """
        return self.interface().script_clean_input(self.profile, **args)

    def clean_output(self, result):
        """
        Clean script result against interface
        """
        return self.interface().script_clean_result(self.profile, result)

    def run(self):
        """
        Run script
        """
        self.start_time = time.time()
        self.logger.info("Running. Input arguments: %s, timeout %s",
                         self.args, self.timeout)
        # Use cached result when available
        cache_hit = False
        if self.cache and self.parent:
            try:
                result = self.get_cache(self.name, self.args)
                self.logger.debug("Cache hit")
                cache_hit = True
            except KeyError:
                pass
        # Execute script
        if not cache_hit:
            try:
                result = self.execute(**self.args)
            finally:
                if not self.parent:
                    # Close SNMP socket when necessary
                    self.snmp.close()
                    # Close CLI socket when necessary
                    self.close_cli_stream()
        # Clean result
        result = self.clean_output(result)
        self.logger.debug("Result: %s", result)
        runtime = time.time() - self.start_time
        self.logger.info("Complete (%.2fms)", runtime * 1000)
        return result

    @classmethod
    def compile_match_filter(cls, *args, **kwargs):
        """
        Compile arguments into version check function
        Returns callable accepting self and version hash arguments
        """
        c = [lambda self, x, g=f: g(x) for f in args]
        for k, v in kwargs.items():
            # Split to field name and lookup operator
            if "__" in k:
                f, o = k.split("__")
            else:
                f = k
                o = "exact"
                # Check field name
            if f not in ("vendor", "platform", "version", "image"):
                raise Exception("Invalid field '%s'" % f)
                # Compile lookup functions
            if o == "exact":
                c += [lambda self, x, f=f, v=v: x[f] == v]
            elif o == "iexact":
                c += [lambda self, x, f=f, v=v: x[f].lower() == v.lower()]
            elif o == "startswith":
                c += [lambda self, x, f=f, v=v: x[f].startswith(v)]
            elif o == "istartswith":
                c += [lambda self, x, f=f, v=v: x[f].lower().startswith(v.lower())]
            elif o == "endswith":
                c += [lambda self, x, f=f, v=v: x[f].endswith(v)]
            elif o == "iendswith":
                c += [lambda self, x, f=f, v=v: x[f].lower().endswith(v.lower())]
            elif o == "contains":
                c += [lambda self, x, f=f, v=v: v in x[f]]
            elif o == "icontains":
                c += [lambda self, x, f=f, v=v: v.lower() in x[f].lower()]
            elif o == "in":
                c += [lambda self, x, f=f, v=v: x[f] in v]
            elif o == "regex":
                c += [lambda self, x, f=f, v=re.compile(v): v.search(x[f]) is not None]
            elif o == "iregex":
                c += [lambda self, x, f=f, v=re.compile(v, re.IGNORECASE): v.search(x[f]) is not None]
            elif o == "isempty":  # Empty string or null
                c += [lambda self, x, f=f, v=v: not x[f] if v else x[f]]
            elif f == "version":
                if o == "lt":  # <
                    c += [lambda self, x, v=v: self.profile.cmp_version(x["version"], v) < 0]
                elif o == "lte":  # <=
                    c += [lambda self, x, v=v: self.profile.cmp_version(x["version"], v) <= 0]
                elif o == "gt":  # >
                    c += [lambda self, x, v=v: self.profile.cmp_version(x["version"], v) > 0]
                elif o == "gte":  # >=
                    c += [lambda self, x, v=v: self.profile.cmp_version(x["version"], v) >= 0]
                else:
                    raise Exception("Invalid lookup operation: %s" % o)
            else:
                raise Exception("Invalid lookup operation: %s" % o)
        # Combine expressions into single lambda
        return reduce(
            lambda x, y: lambda self, v, x=x, y=y: (
                x(self, v) and y(self, v)
            ),
            c,
            lambda self, x: True
        )

    @classmethod
    def match(cls, *args, **kwargs):
        """
        execute method decorator
        """
        def wrap(f):
            # Append to the execute chain
            f._match = x
            f._seq = cls._x_seq.next()
            return f

        # Compile check function
        x = cls.compile_match_filter(*args, **kwargs)
        # Return decorated function
        return wrap

    def match_version(self, *args, **kwargs):
        """
        inline version for BaseScript.match
        """
        return self.compile_match_filter(*args, **kwargs)(
            self,
            self.scripts.get_version()
        )

    def execute(self, **kwargs):
        """
        Default script behavior:
        Pass through _execute_chain and call appropriative handler
        """
        if self._execute_chain and not self.name.endswith(".get_version"):
            # Get version information
            v = self.scripts.get_version()
            # Find and execute proper handler
            for f in self._execute_chain:
                if f._match(self, v):
                    return f(self, **kwargs)
                # Raise error
            raise self.NotSupportedError()

    def cleaned_config(self, config):
        """
        Clean up config from all unnecessary trash
        """
        return self.profile.cleaned_config(config)

    def strip_first_lines(self, text, lines=1):
        """
        Strip first *lines*
        """
        t = text.split("\n")
        if len(t) <= lines:
            return ""
        else:
            return "\n".join(t[lines:])

    def expand_rangelist(self, s):
        """
        Expand expressions like "1,2,5-7" to [1, 2, 5, 6, 7]
        """
        result = {}
        for x in s.split(","):
            x = x.strip()
            if x == "":
                continue
            if "-" in x:
                l, r = [int(y) for y in x.split("-")]
                if l > r:
                    x = r
                    r = l
                    l = x
                for i in range(l, r + 1):
                    result[i] = None
            else:
                result[int(x)] = None
        return sorted(result.keys())

    rx_detect_sep = re.compile("^(.*?)\d+$")

    def expand_interface_range(self, s):
        """
        Convert interface range expression to a list
        of interfaces
        "Gi 1/1-3,Gi 1/7" -> ["Gi 1/1", "Gi 1/2", "Gi 1/3", "Gi 1/7"]
        "1:1-3" -> ["1:1", "1:2", "1:3"]
        "1:1-1:3" -> ["1:1", "1:2", "1:3"]
        :param s: Comma-separated list
        :return:
        """
        r = set()
        for x in s.split(","):
            x = x.strip()
            if not x:
                continue
            if "-" in x:
                # Expand range
                f, t = [y.strip() for y in x.split("-")]
                # Detect common prefix
                match = self.rx_detect_sep.match(f)
                if not match:
                    raise ValueError(x)
                prefix = match.group(1)
                # Detect range boundaries
                start = int(f[len(prefix):])
                if is_int(t):
                    stop = int(t)  # Just integer
                else:
                    if not t.startswith(prefix):
                        raise ValueError(x)
                    stop = int(t[len(prefix):])  # Prefixed
                if start > stop:
                    raise ValueError(x)
                for i in range(start, stop + 1):
                    r.add(prefix + str(i))
            else:
                r.add(x)
        return sorted(r)

    def hexstring_to_mac(self, s):
        """Convert a 6-octet string to MAC address"""
        return ":".join(["%02X" % ord(x) for x in s])

    @property
    def root(self):
        """Get root script"""
        if self.parent:
            return self.parent.root
        else:
            return self

    def get_cache(self, key1, key2):
        """Get cached result or raise KeyError"""
        s = self.root
        return s.call_cache[repr(key1)][repr(key2)]

    def set_cache(self, key1, key2, value):
        """Set cached result"""
        key1 = repr(key1)
        key2 = repr(key2)
        s = self.root
        if key1 not in s.call_cache:
            s.call_cache[key1] = {}
        s.call_cache[key1][key2] = value

    def configure(self):
        """Returns configuration context"""
        return ConfigurationContextManager(self)

    def cached(self):
        """
        Return cached context managed. All nested CLI and SNMP GET/GETNEXT
        calls will be cached.

        Usage:

        with self.cached():
            self.cli(".....)
            self.scripts.script()
        """
        return CacheContextManager(self)

    def enter_config(self):
        """Enter configuration mote"""
        if self.profile.command_enter_config:
            self.cli(self.profile.command_enter_config)

    def leave_config(self):
        """Leave configuration mode"""
        if self.profile.command_leave_config:
            self.cli(self.profile.command_leave_config)
            self.cli("")  # Guardian empty command to wait until configuration is finally written

    def save_config(self, immediately=False):
        """Save current config"""
        if immediately:
            if self.profile.command_save_config:
                self.cli(self.profile.command_save_config)
        else:
            self.schedule_to_save()

    def schedule_to_save(self):
        self.need_to_save = True
        if self.parent:
            self.parent.schedule_to_save()

    @property
    def motd(self):
        """
        Return message of the day
        """
        return self.get_cli_stream().get_motd()

    def re_search(self, rx, s, flags=0):
        """
        Match s against regular expression rx using re.search
        Raise UnexpectedResultError if regular expression is not matched.
        Returns match object.
        rx can be string or compiled regular expression
        """
        if isinstance(rx, basestring):
            rx = re.compile(rx, flags)
        match = rx.search(s)
        if match is None:
            raise self.UnexpectedResultError()
        return match

    def re_match(self, rx, s, flags=0):
        """
        Match s against regular expression rx using re.match
        Raise UnexpectedResultError if regular expression is not matched.
        Returns match object.
        rx can be string or compiled regular expression
        """
        if isinstance(rx, basestring):
            rx = re.compile(rx, flags)
        match = rx.match(s)
        if match is None:
            raise self.UnexpectedResultError()
        return match

    _match_lines_cache = {}

    @classmethod
    def match_lines(cls, rx, s):
        k = id(rx)
        if k not in cls._match_lines_cache:
            _rx = [re.compile(l, re.IGNORECASE) for l in rx]
            cls._match_lines_cache[k] = _rx
        else:
            _rx = cls._match_lines_cache[k]
        ctx = {}
        idx = 0
        r = _rx[0]
        for l in s.splitlines():
            l = l.strip()
            match = r.search(l)
            if match:
                ctx.update(match.groupdict())
                idx += 1
                if idx == len(_rx):
                    return ctx
                r = _rx[idx]
        return None

    def find_re(self, iter, s):
        """
        Find first matching regular expression
        or raise Unexpected result error
        """
        for r in iter:
            if r.search(s):
                return r
        raise self.UnexpectedResultError()

    def hex_to_bin(self, s):
        """
        Convert hexadecimal string to boolean string.
        All non-hexadecimal characters are ignored
        :param s: Input string
        :return: Boolean string
        :rtype: str
        """
        return "".join(
            self.hexbin[c] for c in
            "".join("%02x" % ord(d) for d in s)
        )

    def push_prompt_pattern(self, pattern):
        self.get_cli_stream().push_prompt_pattern(pattern)

    def pop_prompt_pattern(self):
        self.get_cli_stream().pop_prompt_pattern()

    def has_oid(self, oid):
        """
        Check object responses to oid
        """
        try:
            return bool(self.snmp.get(oid))
        except self.snmp.TimeOutError:
            return False

    @classmethod
    def get_timeout(cls):
        return 120

    def cli(self, cmd, command_submit=None, bulk_lines=None,
            list_re=None, cached=False, file=None, ignore_errors=False,
            nowait=False):
        """
        Execute CLI command and return result. Initiate cli session
        when necessary
        :param cmd: CLI command to execute
        :param command_submit:
        :param bulk_lines:
        :param list_re:
        :param cached:
        :param file:
        :param ignore_errors:
        :param nowait:

        Execute CLI command and return a result.
        if list_re is None, return a string
        if list_re is regular expression object, return a list of dicts (group name -> value),
            one dict per matched line
        """
        command_submit = command_submit or self.profile.command_submit
        stream = self.get_cli_stream()
        r = stream.execute(cmd + command_submit)
        # Check for syntax errors
        if not ignore_errors:
            # Check for syntax error
            if (self.profile.rx_pattern_syntax_error and
                    self.profile.rx_pattern_syntax_error.search(r)):
                raise self.CLISyntaxError(r)
            # Then check for operation error
            if (self.profile.rx_pattern_operation_error and
                    self.profile.rx_pattern_operation_error.search(r)):
                raise self.CLIOperationError(r)
        # Echo cancelation
        if r[:4096].lstrip().startswith(cmd):
            r = r.lstrip()
            if r.startswith(cmd + "\n"):
                # Remove first line
                r = self.strip_first_lines(r.lstrip())
            else:
                # Some switches, like ProCurve do not send \n after the echo
                r = r[len(cmd):]
        # Convert to list of dicts if list_re is defined
        if list_re:
            x = []
            for l in r.splitlines():
                match = list_re.match(l.strip())
                if match:
                    x += [match.groupdict()]
            r = x
        return r

    def get_cli_stream(self):
        if self.parent:
            return self.root.get_cli_stream()
        if not self.cli_stream:
            protocol = self.credentials.get("cli_protocol", "telnet")
            self.logger.debug("Open %s CLI", protocol)
            self.cli_stream = get_solution(
                self.cli_protocols[protocol]
            )(self, tos=self.tos)
            # Run session setup
            if self.profile.setup_session:
                self.logger.debug("Setup session")
                self.profile.setup_session(self)
            self.to_shutdown_session = bool(self.profile.shutdown_session)
            # Disable pager when nesessary
            if self.to_disable_pager:
                self.logger.debug("Disable paging")
                self.to_disable_pager = False
                self.cli(self.profile.command_disable_pager,
                         ignore_errors=True)
        return self.cli_stream

    def close_cli_stream(self):
        if self.parent:
            return
        if self.cli_stream:
            if self.to_shutdown_session:
                self.logger.debug("Shutdown session")
                self.profile.shutdown_session(self)
            self.cli_stream.close()
            self.cli_stream = None

    def has_snmp(self):
        """
        Check wherher equipment has SNMP enabled
        """
        return bool(self.credentials.get("snmp_ro"))

    def has_snmp_bulk(self):
        """
        Check wherher equipment supports SNMP BULK
        """
        return "SNMP | Bulk" in self.capabilities

    def ignored_exceptions(self, iterable):
        """
        Context manager to silently ignore specified exceptions
        """
        return IgnoredExceptionsContextManager(iterable)


class ScriptsHub(object):
    """
    Object representing Script.scripts structure.
    Returns initialized child script which can be used ans callable
    """
    class _CallWrapper(object):
        def __init__(self, script_class, parent):
            self.parent = parent
            self.script_class = script_class

        def __call__(self, **kwargs):
            return self.script_class(
                parent=self.parent,
                service=self.parent.service,
                args=kwargs,
                credentials=self.parent.credentials,
                capabilities=self.parent.capabilities,
                version=self.parent.version,
                timeout=self.parent.timeout
            ).run()

    def __init__(self, script):
        self._script = script

    def __getattr__(self, item):
        if item.startswith("_"):
            return self.__dict__[item]
        else:
            from loader import loader as script_loader

            sc = script_loader.get_script(
                "%s.%s" % (self._script.profile.name, item)
            )
            if sc:
                return self._CallWrapper(sc, self._script)
            else:
                raise AttributeError(item)

    def __contains__(self, item):
        """
        Check object has script name
        """
        from loader import loader as script_loader
        if "." not in item:
            # Normalize to full name
            item = "%s.%s" % (self._script.profile.name, item)
        return script_loader.has_script(item)
