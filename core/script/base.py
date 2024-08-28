# ----------------------------------------------------------------------
# SA Script base
# ----------------------------------------------------------------------
# Copyright (C) 2007-2024 The NOC Project
# See LICENSE for details
# ----------------------------------------------------------------------

# Python modules
import re
import logging
import itertools
import operator
from functools import reduce
from collections import defaultdict
from time import perf_counter
from typing import Any, Optional, Set, Union, Callable, Optional, List
from functools import cached_property, partial

# Third-party modules
from atomicl import AtomicLong

# NOC modules
from noc.core.log import PrefixLoggerAdapter
from noc.core.validators import is_int
from noc.core.profile.loader import loader as profile_loader
from noc.core.handler import get_handler
from noc.core.mac import MAC
from noc.config import config
from noc.core.span import Span
from noc.core.matcher import match
from noc.core.comp import smart_bytes, smart_text
from .context import (
    ConfigurationContextManager,
    CacheContextManager,
    IgnoredExceptionsContextManager,
)
from .error import (
    ScriptError,
    CLISyntaxError,
    CLIOperationError,
    NotSupportedError,
    UnexpectedResultError,
)
from .snmp.base import SNMP
from .snmp.beef import BeefSNMP
from .http.base import HTTP
from .sessionstore import SessionStore


class BaseScriptMetaclass(type):
    """
    Process @match decorators
    """

    def __new__(mcs, name, bases, attrs):
        n = type.__new__(mcs, name, bases, attrs)
        n._execute_chain = sorted(
            (v for v in attrs.values() if hasattr(v, "_seq")), key=operator.attrgetter("_seq")
        )
        return n


class BaseScript(object, metaclass=BaseScriptMetaclass):
    """
    Service Activation script base class
    """

    # Script name in form of <vendor>.<system>.<name>
    name = None
    # Default script timeout
    TIMEOUT = config.script.timeout
    # Default session timeout
    SESSION_IDLE_TIMEOUT = config.script.session_idle_timeout
    # Default access preferene
    DEFAULT_ACCESS_PREFERENCE = "SC"
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
    # Sessions
    cli_session_store = SessionStore()
    mml_session_store = SessionStore()
    rtsp_session_store = SessionStore()
    # In session mode when active CLI session exists
    # * True -- reuse session
    # * False -- close session and run new without session context
    reuse_cli_session = True
    # In session mode:
    # Should we keep CLI session for reuse by next script
    # * True - keep CLI session for next script
    # * False - close CLI session
    keep_cli_session = True
    # Script-level matchers.
    # Override profile one
    matchers = {}

    # Error classes shortcuts
    ScriptError = ScriptError
    CLISyntaxError = CLISyntaxError
    CLIOperationError = CLIOperationError
    NotSupportedError = NotSupportedError
    UnexpectedResultError = UnexpectedResultError

    hexbin = {
        "0": "0000",
        "1": "0001",
        "2": "0010",
        "3": "0011",
        "4": "0100",
        "5": "0101",
        "6": "0110",
        "7": "0111",
        "8": "1000",
        "9": "1001",
        "a": "1010",
        "b": "1011",
        "c": "1100",
        "d": "1101",
        "e": "1110",
        "f": "1111",
    }

    cli_protocols = {
        "telnet": "noc.core.script.cli.telnet.TelnetCLI",
        "ssh": "noc.core.script.cli.ssh.SSHCLI",
        "beef": "noc.core.script.cli.beef.BeefCLI",
    }

    mml_protocols = {"telnet": "noc.core.script.mml.telnet.TelnetMML"}

    rtsp_protocols = {"tcp": "noc.core.script.rtsp.base.RTSPBase"}
    # Override access preferences for script
    # S - always try SNMP first
    # C - always try CLI first
    # None - use default preferences
    always_prefer = None

    def __init__(
        self,
        service,
        credentials,
        args=None,
        capabilities=None,
        version=None,
        parent=None,
        timeout=None,
        name=None,
        session=None,
        session_idle_timeout=None,
        streaming=None,
        controller=None,
        labels: Optional[Set[str]] = None,
    ):
        self.service = service
        self.tos = config.activator.tos
        self.pool = config.pool
        self.parent = parent
        name = name or self.name
        self.logger = PrefixLoggerAdapter(
            self.base_logger, "%s] [%s" % (self.name, credentials.get("address", "-"))
        )
        if self.parent:
            self.profile = self.parent.profile
        else:
            self.profile = profile_loader.get_profile(".".join(name.split(".")[:2]))()
        self.credentials = credentials or {}
        if self.is_beefed:
            self.credentials["snmp_ro"] = "public"  # For core.snmp.base check
        self.version = version or {}
        self.capabilities = capabilities or {}
        self.timeout = timeout or self.get_timeout()
        self.start_time = None
        self._interface = self.interface()
        self.args = self.clean_input(args) if args else {}
        self.mml_stream = None
        self.rtsp_stream = None
        self.scripts = ScriptsHub(self)
        # Store session id
        self.session = session
        self.session_idle_timeout = session_idle_timeout or self.SESSION_IDLE_TIMEOUT
        #
        self.streaming = streaming
        if self.parent:
            self.controller = self.parent.controller
        else:
            self.controller = controller
        self.labels = labels or set()
        # Cache CLI and SNMP calls, if set
        self.is_cached = False
        # Suitable only when self.parent is None.
        # Cached results for scripts marked with "cache"
        self.call_cache = {}
        # Suitable only when self.parent is None
        # Cached results of self.cli calls
        self.cli_cache = {}
        #
        self.http_cache = {}
        self.partial_result = None
        # @todo: Get native encoding from ManagedObject
        self.native_encoding = "utf8"
        # Tracking
        self.to_track = False
        self.cli_tracked_data = {}  # command -> [packets]
        self.cli_tracked_command = None
        # state -> [..]
        self.cli_fsm_tracked_data = {}
        #
        if not parent and version and not name.endswith(".get_version"):
            self.logger.debug("Filling get_version cache with %s", version)
            s = name.split(".")
            self.set_cache("%s.%s.get_version" % (s[0], s[1]), {}, version)
        if (
            self.is_beefed
            and not parent
            and not name.endswith(".get_capabilities")
            and not name.endswith(".get_version")
        ):
            self.capabilities = self.scripts.get_capabilities()
            self.logger.info("Filling capabilities with %s", self.capabilities)
        # Fill matchers
        if not self.name.endswith(".get_version"):
            self.apply_matchers()
        #
        if self.profile.setup_script:
            self.profile.setup_script(self)
        # Script perf metrics
        self.script_metrics = defaultdict(lambda: AtomicLong(0))
        # Cleanup handlers
        self._on_cleanup: Optional[List[Callable[[], None]]] = None

    def __call__(self, *args, **kwargs):
        self.args = kwargs
        return self.run()

    def on_cleanup(self, cb: Callable[[], None]) -> None:
        """
        Install handler which be called on script finalization.

        Intended to use with protocols.

        Args:
            cb: Callback which will be called on cleanup.
        """
        if self._on_cleanup is None:
            self._on_cleanup = [cb]
        else:
            self._on_cleanup.append(cb)

    @cached_property
    def _cli(self) -> CLI:
        if self.parent:
            return self.root._cli
        # Try to reuse session
        if self.session:
            cli = self.cli_session_store.get(self.session)
            if cli:
                if self.to_reuse_cli_session():
                    self.logger.debug("Using cached session's CLI")
                    cli.set_script(self)
                    return cli
                self.logger.debug("Script cannot reuse existing CLI session, starting new one")
                self.close_cli_stream()
        # Initialize
        protocol = self.credentials.get("cli_protocol", "telnet")
        self.logger.debug("Open %s CLI", protocol)
        cli = get_handler(self.cli_protocols[protocol])(self, tos=self.tos)
        # Store to the sessions
        cleaned = False
        if self.session:
            self.cli_session_store.put(self.session, cli)
            if self.to_keep_cli_session():
                # Schedule to return cli to pool
                self.on_cleanup(
                    partial(
                        self.cli_session_store.put, self.session, cli, self.session_idle_timeout
                    )
                )
                cleaned = True
        if not cleaned:
            # Schedule cleanup
            self.on_cleanup(cli.shutdown_session)
            self.on_cleanup(cli.close)
        cli.setup_session()
        # Disable pager when necessary
        if self.profile.command_disable_pager:
            self.logger.debug("Disable paging")
            if isinstance(self.profile.command_disable_pager, str):
                cli.push_prelude(self.profile.command_disable_pager, ignore_errors=True)
            elif isinstance(self.profile.command_disable_pager, list):
                for cmd in self.profile.command_disable_pager:
                    cli.push_prelude(cmd, ignore_errors=True)
            else:
                msg = "Invalid command_disable_pager"
                raise UnexpectedResultError(msg)
        return cli

    @cached_property
    def snmp(self) -> SNMP:
        if self.parent:
            return self.root.snmp
        if self.is_beefed:
            return BeefSNMP(self)
        snmp_rate_limit = self.credentials.get("snmp_rate_limit", None) or None
        if snmp_rate_limit is None:
            snmp_rate_limit = self.profile.get_snmp_rate_limit(self)
        snmp = SNMP(self, rate=snmp_rate_limit)
        self.on_cleanup(snmp.close)
        return snmp

    @cached_property
    def http(self) -> HTTP:
        if self.parent:
            return self.root.http
        http = HTTP(self)
        self.on_cleanup(http.close)
        return http

    def apply_matchers(self):
        """
        Process matchers and apply is_XXX properties
        :return:
        """

        def get_matchers(c, matchers):
            return {m: match(c, matchers[m]) for m in matchers}

        # Match context
        ctx = self.version or {}
        if self.capabilities:
            ctx["caps"] = self.capabilities
        # Calculate matches
        v = get_matchers(ctx, self.profile.matchers)
        v.update(get_matchers(ctx, self.matchers))
        #
        for k in v:
            self.logger.debug("%s = %s", k, v[k])
            setattr(self, k, v[k])

    def clean_input(self, args):
        """
        Cleanup input parameters against interface
        """
        return self._interface.script_clean_input(self.profile, **args)

    def clean_output(self, result):
        """
        Clean script result against interface
        """
        return self._interface.script_clean_result(self.profile, result)

    def clean_streaming_result(self, result):
        """
        :param result:
        :return:
        """
        if self.streaming.data and isinstance(result, dict):
            result.update(self.streaming.get_data())
        elif self.streaming.data and isinstance(result, list):
            data = self.streaming.get_data()
            for ss in result:
                ss.update(data)
        return result

    def run(self):
        """
        Run script
        """
        with Span(server="activator", service=self.name, in_label=self.credentials.get("address")):
            self.start_time = perf_counter()
            self.logger.debug("Running. Input arguments: %s, timeout %s", self.args, self.timeout)
            # Use cached result when available
            cache_hit = False
            if self.cache and self.parent:
                try:
                    result = self.get_cache(self.name, self.args)
                    self.logger.info("Using cached result")
                    cache_hit = True
                except KeyError:
                    pass
            # Execute script
            if not cache_hit:
                try:
                    result = self.execute(**self.args)
                    if self.cache and self.parent and result:
                        self.logger.info("Caching result")
                        self.set_cache(self.name, self.args, result)
                finally:
                    if self._on_cleanup:
                        for cb in self._on_cleanup:
                            cb()
                    if not self.parent:
                        # Close MML socket when necessary
                        self.close_mml_stream()
                        # Close RTSP socket when necessary
                        self.close_rtsp_stream()
            # Clean result
            result = self.clean_output(result)
            self.logger.debug("Result: %s", result)
            runtime = perf_counter() - self.start_time
            self.logger.info("Complete (%.2fms)", runtime * 1000)
            self.script_metrics["duration_ms"] = runtime * 1000
            if self.streaming:
                result = self.clean_streaming_result(result)
        return result

    @classmethod
    def compile_match_filter(cls, *args, **kwargs):
        # pylint: disable=undefined-variable
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
                c += [
                    lambda self, x, f=f, v=re.compile(v, re.IGNORECASE): v.search(x[f]) is not None
                ]
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
            ),  # pylint: disable=undefined-variable
            c,
            lambda self, x: True,
        )

    @classmethod
    def match(cls, *args, **kwargs):
        """
        execute method decorator
        """

        def wrap(f):
            # Append to the execute chain
            if hasattr(f, "_match"):
                old_filter = f._match
                # pylint: disable=undefined-variable
                f._match = lambda self, v, old_filter=old_filter, new_filter=new_filter: new_filter(
                    self, v
                ) or old_filter(self, v)
            else:
                f._match = new_filter
            f._seq = next(cls._x_seq)
            return f

        # Compile check function
        new_filter = cls.compile_match_filter(*args, **kwargs)
        # Return decorated function
        return wrap

    def match_version(self, *args, **kwargs):
        """
        inline version for BaseScript.match
        """
        if not self.version:
            self.version = self.scripts.get_version()
        return self.compile_match_filter(*args, **kwargs)(self, self.version)

    def execute(self, **kwargs):
        """
        Default script behavior:
        Pass through _execute_chain and call appropriate handler
        """
        if self._execute_chain and not self.name.endswith(".get_version"):
            # Deprecated @match chain
            self.logger.info(
                "WARNING: Using deprecated @BaseScript.match() decorator. "
                "Consider porting to the new matcher API"
            )
            # Get version information
            if not self.version:
                self.version = self.scripts.get_version()
            # Find and execute proper handler
            for f in self._execute_chain:
                if f._match(self, self.version):
                    return f(self, **kwargs)
                # Raise error
            raise self.NotSupportedError()
        else:
            # New SNMP/CLI API
            return self.call_method(
                cli_handler=self.execute_cli, snmp_handler=self.execute_snmp, **kwargs
            )

    def call_method(self, cli_handler=None, snmp_handler=None, fallback_handler=None, **kwargs):
        """
        Call function depending on access_preference
        :param cli_handler: String or callable to call on CLI access method
        :param snmp_handler: String or callable to call on SNMP access method
        :param fallback_handler: String or callable to call if no access method matched
        :param kwargs:
        :return:
        """
        # Select proper handler
        access_preference = self.get_access_preference() + "*"
        for m in access_preference:
            # Select proper handler
            if m == "C":
                handler = cli_handler
            elif m == "S":
                if self.has_snmp() or self.name.endswith(".get_version"):
                    handler = snmp_handler
                else:
                    self.logger.debug("SNMP is not enabled. Passing to next method")
                    continue
            elif m == "*":
                handler = fallback_handler
            else:
                raise self.NotSupportedError("Invalid access method '%s'" % m)
            # Resolve handler when necessary
            if isinstance(handler, str):
                handler = getattr(self, handler, None)
            if handler is None:
                self.logger.debug("No '%s' handler. Passing to next method" % m)
                continue
            # Call handler
            try:
                r = handler(**kwargs)
                if isinstance(r, PartialResult):
                    if self.partial_result:
                        self.partial_result.update(r.result)
                    else:
                        self.partial_result = r.result
                    self.logger.debug(
                        "Partial result: %r. Passing to next method", self.partial_result
                    )
                else:
                    return r
            except self.snmp.TimeOutError:
                self.logger.info("SNMP timeout. Passing to next method")
                if access_preference == "S*":
                    self.logger.info("Last S method break by timeout.")
                    raise self.snmp.TimeOutError
            except NotImplementedError:
                self.logger.debug(
                    "Access method '%s' is not implemented. Passing to next method", m
                )
        raise self.NotSupportedError(
            "Access preference '%s' is not supported" % access_preference[:-1]
        )

    def execute_cli(self, **kwargs):
        """
        Process script using CLI
        :param kwargs:
        :return:
        """
        raise NotImplementedError("execute_cli() is not implemented")

    def execute_snmp(self, **kwargs):
        """
        Process script using SNMP
        :param kwargs:
        :return:
        """
        raise NotImplementedError("execute_snmp() is not implemented")

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
                left, right = [int(y) for y in x.split("-")]
                if left > right:
                    x = right
                    right = left
                    left = x
                for i in range(left, right + 1):
                    result[i] = None
            else:
                result[int(x)] = None
        return sorted(result.keys())

    rx_detect_sep = re.compile(r"^(.*?)\d+$")

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
                start = int(f[len(prefix) :])
                if is_int(t):
                    stop = int(t)  # Just integer
                else:
                    if not t.startswith(prefix):
                        raise ValueError(x)
                    stop = int(t[len(prefix) :])  # Prefixed
                if start > stop:
                    raise ValueError(x)
                for i in range(start, stop + 1):
                    r.add(prefix + str(i))
            else:
                r.add(x)
        return sorted(r)

    def macs_to_ranges(self, macs):
        """
        Converts list of macs to rangea
        :param macs: Iterable yielding mac addresses
        :returns: [(from, to), ..]
        """
        r = []
        for m in sorted(MAC(x) for x in macs):
            if r:
                if r[-1][1].shift(1) == m:
                    # Expand last range
                    r[-1][1] = m
                else:
                    r += [[m, m]]
            else:
                r += [[m, m]]
        return [(str(x[0]), str(x[1])) for x in r]

    def hexstring_to_mac(self, s):
        """Convert a 6-octet string to MAC address"""
        return ":".join(["%02X" % ord(x) for x in s])

    @property
    def root(self):
        """Get root script"""
        if self.parent:
            return self.parent.root
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

    @cached_property
    def motd(self):
        """
        Return message of the day
        """
        return self._cli.get_motd()

    def re_search(self, rx, s, flags=0):
        """
        Match s against regular expression rx using re.search
        Raise UnexpectedResultError if regular expression is not matched.
        Returns match object.
        rx can be string or compiled regular expression
        """
        if isinstance(rx, str):
            rx = re.compile(rx, flags)
        match = rx.search(s)
        if match is None:
            raise UnexpectedResultError()
        return match

    def re_match(self, rx, s, flags=0):
        """
        Match s against regular expression rx using re.match
        Raise UnexpectedResultError if regular expression is not matched.
        Returns match object.
        rx can be string or compiled regular expression
        """
        if isinstance(rx, str):
            rx = re.compile(rx, flags)
        match = rx.match(s)
        if match is None:
            raise UnexpectedResultError()
        return match

    _match_lines_cache = {}

    @classmethod
    def match_lines(cls, rx, s):
        k = id(rx)
        if k not in cls._match_lines_cache:
            _rx = [re.compile(line, re.IGNORECASE) for line in rx]
            cls._match_lines_cache[k] = _rx
        else:
            _rx = cls._match_lines_cache[k]
        ctx = {}
        idx = 0
        r = _rx[0]
        for line in s.splitlines():
            line = line.strip()
            match = r.search(line)
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
        raise UnexpectedResultError()

    def hex_to_bin(self, s):
        """
        Convert hexadecimal string to boolean string.
        All non-hexadecimal characters are ignored
        :param s: Input string
        :return: Boolean string
        :rtype: str
        """
        return "".join(self.hexbin[c] for c in "".join("%02x" % ord(d) for d in s))

    def push_prompt_pattern(self, pattern):
        self._cli.push_prompt_pattern(pattern)

    def pop_prompt_pattern(self):
        self._cli.pop_prompt_pattern()

    def has_oid(self, oid):
        """
        Check object responses to oid
        """
        try:
            return bool(self.snmp.get(oid))
        except self.snmp.TimeOutError:
            return False

    def get_timeout(self):
        return self.TIMEOUT

    def cli(
        self,
        cmd: str,
        command_submit: Optional[bytes] = None,
        bulk_lines: Any = None,
        list_re: Any = None,
        cached: bool = False,
        file: Optional[str] = None,
        ignore_errors: Any = False,
        allow_empty_response: Any = True,
        nowait: Any = False,
        obj_parser: Any = None,
        cmd_next: Any = None,
        cmd_stop: Any = None,
        labels: Optional[Union[str, Set[str]]] = None,
        no_prelude: bool = False,
    ) -> str:
        """
        Execute CLI command and return result. Initiate cli session
        when necessary.

        if list_re is None, return a string
        if list_re is regular expression object, return a list of dicts (group name -> value),
            one dict per matched line

        :param cmd: CLI command to execute
        :param command_submit: Optional suffix to submit command. Profile's one used by default
        :param bulk_lines:
        :param list_re:
        :param cached: True if result of execution may be cached
        :param file: Path to the file containing debugging result
        :param ignore_errors:
        :param allow_empty_response: Allow empty output. If False - ignore prompt and wait output
        :param nowait:
        :param labels:
        """

        def format_result(result):
            if list_re:
                x = []
                for line in result.splitlines():
                    match = list_re.match(line.strip())
                    if match:
                        x.append(match.groupdict())
                return x
            return result

        # Execute collected prelude
        if not no_prelude:
            for prelude in self._cli.iter_prelude():
                self.cli(prelude.cmd, ignore_errors=prelude.ignore_errors, no_prelude=True)
        # Read from file
        if file:
            with open(file) as f:
                return format_result(f.read())
        # Cached result
        if cached:
            r = self.root.cli_cache.get(cmd)
            if r is not None:
                self.logger.debug("Use cached result")
                return format_result(r)
        # Effective command submit suffix
        if command_submit is None:
            command_submit = self.profile.command_submit
        # Encode submitted command
        submitted_cmd = smart_bytes(cmd, encoding=self.native_encoding) + command_submit
        # Run command
        if self.to_track:
            self.cli_tracked_command = cmd
        r = self._cli.execute(
            submitted_cmd,
            obj_parser=obj_parser,
            cmd_next=cmd_next,
            cmd_stop=cmd_stop,
            ignore_errors=ignore_errors,
            allow_empty_response=allow_empty_response,
            labels=labels,
        )
        if isinstance(r, bytes):
            r = smart_text(r, errors="ignore", encoding=self.native_encoding)
        if isinstance(r, str):
            # Check for syntax errors
            if not ignore_errors:
                # Then check for operation error
                if (
                    self.profile.rx_pattern_operation_error
                    and self.profile.rx_pattern_operation_error_str.search(r)
                ):
                    raise self.CLIOperationError(r)
            # Echo cancelation
            r = self.echo_cancelation(r, cmd)
            # Store cli cache when necessary
            if cached:
                self.root.cli_cache[cmd] = r
        return format_result(r)

    def echo_cancelation(self, r: str, cmd: str) -> str:
        """
        Adaptive echo cancelation

        :param r:
        :param cmd:
        :return:
        """
        if r[:4096].lstrip().startswith(cmd):
            r = r.lstrip()
            if r.startswith(cmd + "\n"):
                # Remove first line
                r = self.strip_first_lines(r.lstrip())
            else:
                # Some switches, like ProCurve do not send \n after the echo
                r = r[len(cmd) :]
        return r

    def mml(self, cmd, **kwargs):
        """
        Execute MML command and return result. Initiate MML session when necessary
        :param cmd:
        :param kwargs:
        :return:
        """
        stream = self.get_mml_stream()
        r = stream.execute(cmd, **kwargs)
        return r

    def get_mml_stream(self):
        if self.parent:
            return self.root.get_mml_stream()
        if not self.mml_stream and self.session:
            # Try to get cached session's CLI
            self.mml_stream = self.mml_session_store.get(self.session)
            if self.mml_stream:
                if self.to_reuse_cli_session():
                    self.logger.debug("Using cached session's MML")
                    self.mml_stream.set_script(self)
                else:
                    self.logger.debug("Script cannot reuse existing MML session, starting new one")
                    self.close_mml_stream()
        if not self.mml_stream:
            protocol = self.credentials.get("cli_protocol", "telnet")
            self.logger.debug("Open %s MML", protocol)
            self.mml_stream = get_handler(self.mml_protocols[protocol])(self, tos=self.tos)
            # Store to the sessions
            if self.session:
                self.mml_session_store.put(self.session, self.mml_stream)
        return self.mml_stream

    def close_mml_stream(self):
        if self.parent:
            return
        if self.mml_stream:
            if self.session and self.to_keep_cli_session():
                self.mml_session_store.put(self.session, self.mml_stream, self.session_idle_timeout)
            else:
                self.mml_stream.close()
            self.mml_stream = None

    def rtsp(self, method, path, **kwargs):
        """
        Execute RTSP command and return result. Initiate RTSP session when necessary
        :param method:
        :param path:
        :param kwargs:
        :return:
        """
        stream = self.get_rtsp_stream()
        r = stream.execute(path, method, **kwargs)
        return r

    def get_rtsp_stream(self):
        if self.parent:
            return self.root.get_rtsp_stream()
        if not self.rtsp_stream and self.session:
            # Try to get cached session's CLI
            self.rtsp_stream = self.rtsp_session_store.get(self.session)
            if self.rtsp_stream:
                if self.to_reuse_cli_session():
                    self.logger.debug("Using cached session's RTSP")
                    self.rtsp_stream.set_script(self)
                else:
                    self.logger.debug("Script cannot reuse existing RTSP session, starting new one")
                    self.close_rtsp_stream()
        if not self.rtsp_stream:
            protocol = "tcp"
            self.logger.debug("Open %s RTSP", protocol)
            self.rtsp_stream = get_handler(self.rtsp_protocols[protocol])(self, tos=self.tos)
            # Store to the sessions
            if self.session:
                self.rtsp_session_store.put(self.session, self.rtsp_stream)
        return self.rtsp_stream

    def close_rtsp_stream(self):
        if self.parent:
            return
        if self.rtsp_stream:
            if self.session and self.to_keep_cli_session():
                self.rtsp_session_store.put(
                    self.session, self.rtsp_stream, self.session_idle_timeout
                )
            else:
                self.rtsp_stream.close()
            self.cli_stream = None

    def close_current_session(self):
        if self.session:
            self.close_session(self.session)

    @classmethod
    def close_session(cls, session_id):
        """
        Explicit session closing
        :return:
        """
        cls.cli_session_store.remove(session_id, shutdown=True)
        cls.mml_session_store.remove(session_id, shutdown=True)
        cls.rtsp_session_store.remove(session_id, shutdown=True)

    def get_access_preference(self):
        preferred = self.get_always_preferred()
        r = self.credentials.get("access_preference", self.DEFAULT_ACCESS_PREFERENCE)
        if preferred and preferred in r:
            return preferred + "".join(x for x in r if x != preferred)
        return r

    def get_always_preferred(self):
        """
        Return always preferred access method
        :return:
        """
        return self.always_prefer

    def has_cli_access(self):
        return "C" in self.get_access_preference()

    def has_snmp_access(self):
        return "S" in self.get_access_preference() and self.has_snmp()

    def has_cli_only_access(self):
        return self.has_cli_access() and not self.has_snmp_access()

    def has_snmp_only_access(self):
        return not self.has_cli_access() and self.has_snmp_access()

    def has_snmp(self) -> bool:
        """
        Check whether equipment has SNMP enabled
        """
        # Check Credential
        snmp_version = self.credentials.get("snmp_version") or "v2c"
        if snmp_version != "v3" and not self.credentials.get("snmp_ro"):
            # V1,V2 credential check
            return False
        elif snmp_version == "v3" and not self.credentials.get("snmp_username"):
            # V3 credential check
            return False
        # Check Caps
        if "SNMP" not in self.capabilities:
            return True
        # If having SNMP caps
        return self.has_capability("SNMP")

    def has_snmp_v1(self):
        return self.has_capability("SNMP | v1")

    def has_snmp_v2c(self):
        return self.has_capability("SNMP | v2c")

    def has_snmp_v3(self):
        return self.has_capability("SNMP | v3")

    def has_snmp_bulk(self):
        """
        Check whether equipment supports SNMP BULK
        """
        return self.has_capability("SNMP | Bulk")

    def has_capability(self, capability, allow_zero=False):
        """
        Check whether equipment supports capability
        """
        if allow_zero:
            return self.capabilities.get(capability) is not None
        else:
            return bool(self.capabilities.get(capability))

    def ignored_exceptions(self, iterable):
        """
        Context manager to silently ignore specified exceptions
        """
        return IgnoredExceptionsContextManager(iterable)

    def iter_pairs(self, g, offset=0):
        """
        Convert iterable g to a pairs.

        i.e.
        [1, 2, 3, 4] -> [(1, 2), (3, 4)]

        Args:
            g: Iterable
            offset: Skip first records.
        """
        g = iter(g)
        if offset:
            for _ in range(offset):
                next(g)
        return zip(g, g)

    def to_reuse_cli_session(self) -> bool:
        return self.reuse_cli_session

    def to_keep_cli_session(self) -> bool:
        return self.keep_cli_session

    def start_tracking(self):
        self.logger.debug("Start tracking")
        self.to_track = True

    def stop_tracking(self):
        self.logger.debug("Stop tracking")
        self.to_track = False
        self.cli_tracked_data = {}

    def push_cli_tracking(self, r, state):
        if state == "prompt":
            if self.cli_tracked_command in self.cli_tracked_data:
                self.cli_tracked_data[self.cli_tracked_command] += [r]
            else:
                self.cli_tracked_data[self.cli_tracked_command] = [r]
        elif state in self.cli_fsm_tracked_data:
            self.cli_fsm_tracked_data[state] += [r]
        else:
            self.cli_fsm_tracked_data[state] = [r]

    def push_snmp_tracking(self, oid, tlv):
        self.logger.debug("PUSH SNMP %s: %r", oid, tlv)

    def iter_cli_tracking(self):
        """
        Yields command, packets for collected data
        :return:
        """
        for cmd in self.cli_tracked_data:
            self.logger.debug("Collecting %d tracked CLI items", len(self.cli_tracked_data[cmd]))
            yield cmd, self.cli_tracked_data[cmd]
        self.cli_tracked_data = {}

    def iter_cli_fsm_tracking(self):
        for state in self.cli_fsm_tracked_data:
            yield state, self.cli_fsm_tracked_data[state]

    def request_beef(self):
        """
        Download and return beef
        :return:
        """
        if not hasattr(self, "_beef"):
            self.logger.debug("Requesting beef")
            beef_storage_url = self.credentials.get("beef_storage_url")
            beef_path = self.credentials.get("beef_path")
            if not beef_storage_url:
                self.logger.debug("No storage URL")
                self._beef = None
                return None
            if not beef_path:
                self.logger.debug("No beef path")
                self._beef = None
                return None
            from .beef import Beef

            try:
                beef = Beef.load(beef_storage_url, beef_path)
            except IOError as e:
                self.logger.error("Beef load error: %s", e)
                return None
            self._beef = beef
        return self._beef

    @property
    def is_beefed(self):
        return self.credentials.get("cli_protocol") == "beef"

    def get_labels(self) -> Set[str]:
        return self.labels

    def add_label(self, label: str) -> None:
        self.labels.add(label)

    def delete_label(self, label: str) -> None:
        try:
            self.labels.remove(label)
        except KeyError:
            self.logger.warning("Can't remove a label '%s' from labels", label)

    def apply_metrics(self, d):
        """
        Apply metrics value to dictionary d
        :param d: Dictionary
        :return:
        """
        for k, v in self.script_metrics.items():
            if isinstance(v, AtomicLong):
                v = v.value
            d[k] = v
        return d


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
                timeout=self.parent.timeout,
            ).run()

    def __init__(self, script):
        self._script = script

    def __getattr__(self, item):
        if item.startswith("_"):
            return self.__dict__[item]
        from .loader import loader as script_loader

        sc = script_loader.get_script("%s.%s" % (self._script.profile.name, item))
        if sc:
            return self._CallWrapper(sc, self._script)
        raise AttributeError(item)

    def __contains__(self, item):
        """
        Check object has script name
        """
        from .loader import loader as script_loader

        if "." not in item:
            # Normalize to full name
            item = "%s.%s" % (self._script.profile.name, item)
        return script_loader.has_script(item)


class PartialResult(object):
    __slots__ = ["result"]

    def __int__(self, **kwargs):
        self.result = kwargs
