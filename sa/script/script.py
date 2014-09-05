# -*- coding: utf-8 -*-
##----------------------------------------------------------------------
## Service Activation Script classes
##----------------------------------------------------------------------
## Copyright (C) 2007-2012 The NOC Project
## See LICENSE for details
##----------------------------------------------------------------------

## Python modules
from __future__ import with_statement
import threading
import thread
import re
import logging
import time
import sys
import Queue
import cPickle
import ctypes
import datetime
## NOC modules
from noc.sa.protocols.sae_pb2 import TELNET, SSH, HTTP
from noc.lib.registry import Registry
from noc.sa.profiles import profile_registry
from noc.lib.debug import format_frames, get_traceback_frames
from noc.sa.script.exception import *
from noc.sa.script.context import *
from noc.sa.script.telnet import CLITelnetSocket
from noc.sa.script.ssh import CLISSHSocket
from noc.sa.script.http import HTTPProvider
from noc.sa.script.snmp import SNMPProvider
from noc.lib.validators import is_int

## Module constants
rx_nohex = re.compile("[^0-9a-f]+")  # non-hexadecimal
hexbin = {
    "0": "0000", "1": "0001", "2": "0010", "3": "0011",
    "4": "0100", "5": "0101", "6": "0110", "7": "0111",
    "8": "1000", "9": "1001", "a": "1010", "b": "1011",
    "c": "1100", "d": "1101", "e": "1110", "f": "1111"
}


class ScriptProxy(object):
    """
    Script.scripts proxy hub
    """

    def __init__(self, parent):
        """
        :param parent: Script instance
        """
        self._parent = parent

    def __getattr__(self, name):
        """Return ScriptCallProxy instance for script 'name'"""
        return ScriptCallProxy(self._parent, self._parent.profile.scripts[name])

    def has_script(self, name):
        """Check profile has script name"""
        return name in self._parent.profile.scripts

    def __contains__(self, name):
        """Check profile has script name"""
        return self.has_script(name)


class ScriptCallProxy(object):
    """
    Script call wrapper to mimic script run with simple function call
    """

    def __init__(self, parent, script):
        self.parent = parent
        self.script = script

    def __call__(self, **kwargs):
        """Call script"""
        s = self.script(self.parent.profile, self.parent.activator,
            self.parent.object_name, self.parent.access_profile,
            parent=self.parent, **kwargs)
        return s.guarded_run()


class ScriptRegistry(Registry):
    """Script registry"""
    name = "ScriptRegistry"
    subdir = "profiles"
    classname = "Script"
    apps = ["noc.sa"]
    exclude = ["highlight"]

    def register_generics(self):
        """Register generic scripts to all supporting profiles"""
        generics = []
        for c in [c for c in self.classes.values() if c.name and c.name.startswith("Generic.")]:
            g, name = c.name.split(".")
            for p in profile_registry.classes:
                s_name = p + "." + name
                # Do not register generic when specific exists
                if s_name in self.classes:
                    continue
                to_register = True
                for r_name, r_interface in c.requires:
                    rs_name = p + "." + r_name
                    if rs_name not in self.classes or not self.classes[rs_name].implements_interface(r_interface):
                        to_register = False
                        break
                if to_register:
                    self.classes[s_name] = c
                    profile_registry[p].scripts[name] = c
                    generics += [s_name]

    def register_all(self):
        """Register all scripts and generic scripts"""
        super(ScriptRegistry, self).register_all()
        self.register_generics()


script_registry = ScriptRegistry()
_execute_chain = []


class ScriptBase(type):
    """
    Script metaclass
    """
    def __new__(cls, name, bases, attrs):
        global _execute_chain
        m = type.__new__(cls, name, bases, attrs)
        m._execute_chain = _execute_chain
        _execute_chain = []
        m.implements = [c() for c in m.implements]
        script_registry.register(m.name, m)
        if m.name and not m.name.startswith("Generic."):
            pv, pos, sn = m.name.split(".", 2)
            profile_registry["%s.%s" % (pv, pos)].scripts[sn] = m
        return m


class Script(threading.Thread):
    """Service activation script"""
    __metaclass__ = ScriptBase
    name = None
    description = None
    # Enable call cache
    # If True, script result will be cached and reused
    # during lifetime of parent script
    cache = False
    # Interfaces list. Each element of list must be Interface subclass
    implements = []
    # Scripts required by generic script.
    # For common scripts - empty list
    # For generics - list of pairs (script_name, interface)
    requires = []
    #
    template = None  # Relative template path in sa/templates/
    # Constants
    TELNET = TELNET
    SSH = SSH
    HTTP = HTTP
    TIMEOUT = 120  # 2min by default
    CLI_TIMEOUT = None  # Optional timeout for telnet/ssh providers
    #
    LoginError = LoginError
    CLISyntaxError = CLISyntaxError
    CLIOperationError = CLIOperationError
    CLITransportError = CLITransportError
    CLIDisconnectedError = CLIDisconnectedError
    TimeOutError = TimeOutError
    NotSupportedError = NotSupportedError
    UnexpectedResultError = UnexpectedResultError
    #
    _execute_chain = []
    logger = logging.getLogger(name or "script")

    def __init__(self, profile, _activator, object_name, access_profile,
                 timeout=0, parent=None, **kwargs):
        self.start_time = time.time()
        self.parent = parent
        self.object_name = object_name
        self.access_profile = access_profile
        self.attrs = {}
        self._timeout = timeout if timeout else self.TIMEOUT
        if self.access_profile.address:
            p = self.access_profile.address
        elif self.access_profile.path:
            p = self.access_profile.path
        else:
            p = "<unknown>"
        self.debug_name = "%s(%s, %s)" % (self.name, self.object_name, p)
        self.encoding = None  # Device encoding. None if UTF8
        for a in access_profile.attrs:
            self.attrs[a.key] = a.value
            # Try to get encoding from attributes
            if a.key == "encoding":
                v = a.value.strip()
                # Test encoding
                try:
                    u"test".encode(v)
                    self.encoding = v
                    self.debug("Using '%s' encoding" % v)
                except LookupError:
                    self.error("Unknown encoding: '%s'" % v)
        super(Script, self).__init__(kwargs=kwargs)
        self.activator = _activator
        self.servers = _activator.servers
        self.profile = profile
        self.cli_provider = None
        self.http = HTTPProvider(self)
        self.snmp = SNMPProvider(self)
        self.status = False
        self.result = None
        self.call_cache = {}  # Suitable only when self.parent is None. Cached results for scripts marked with "cache"
        self.error_traceback = None
        self.login_error = None
        self.strip_echo = True
        self.kwargs = kwargs
        self.scripts = ScriptProxy(self)
        self.need_to_save = False
        self.to_disable_pager = not self.parent and self.profile.command_disable_pager
        self.log_cli_sessions_path = None  # Path to log CLI session
        self.is_cancelable = False  # Can script be cancelled
        self.is_cached = False   # Cache CLI and SNMP calls, if set
        self.cmd_cache = {}  # "(CLI|GET|GETNETX):key" -> value, suitable only for parent
        self.e_timeout = False  # Script terminated with timeout
        self.e_cancel = False  # Scrcipt cancelled
        self.e_disconnected = False  # CLI Disconnected error
        self.e_not_supported = False  # NotSupportedError risen
        self.e_http_error = False  # HTTPError risen
        self._thread_id = None  # Python 2.5 compatibility
        self.cli_wait = False
        # Set up CLI session logging
        if self.parent:
            self.log_cli_sessions_path = self.parent.log_cli_sessions_path
        elif self.activator.log_cli_sessions\
             and self.activator.log_cli_sessions_ip_re.search(self.access_profile.address)\
        and self.activator.log_cli_sessions_script_re.search(self.name):
            self.log_cli_sessions_path = self.activator.log_cli_sessions_path
            for k, v in [
                ("ip", self.access_profile.address),
                ("script", self.name),
                ("ts", datetime.datetime.now().strftime("%Y-%m-%d-%H-%M-%S"))]:
                self.log_cli_sessions_path = self.log_cli_sessions_path.replace("{{%s}}" % k, v)
            self.cli_debug("IP: %s SCRIPT: %s" % (self.access_profile.address, self.name), "!")
            # Finally call setup_script() for additional script tuning
        if profile.setup_script:
            profile.setup_script(self)

    @classmethod
    def template_clean_result(cls, result):
        """
        Clean result to render template
        """
        if self.implements:
            return cls.implements[0].template_clean_result(cls.profile, result)
        else:
            return result

    @classmethod
    def get_template(cls):
        """
        Get template path.
        
        :return: Template path or None
        :rtype: String or None
        """
        if cls.template:
            return cls.template
        if cls.implements and cls.implements[0].template:
            return cls.implements[0].template
        return None

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
        return reduce(lambda x, y: lambda self, v, x=x, y=y: x(self, v) and y(self, v), c, lambda self, x: True)

    @classmethod
    def match(cls, *args, **kwargs):
        """execute method decorator"""
        def decorate(f):
            global _execute_chain
            # Append to the execute chain
            _execute_chain += [(x, f)]
            return f

        # Compile check function
        x = cls.compile_match_filter(*args, **kwargs)
        # Return decorated function
        return decorate

    def match_version(self, *args, **kwargs):
        """inline version for Script.match"""
        return self.compile_match_filter(*args, **kwargs)(self, self.scripts.get_version())

    def cli_debug(self, msg, chars=None):
        if not self.log_cli_sessions_path:
            return
        m = datetime.datetime.now().strftime("[%Y-%m-%d %H:%M:%S] ")
        if chars:
            m += chars * 50
        m += "\n"
        m += str(msg) + "\n"
        with open(self.log_cli_sessions_path, "a") as f:
            f.write(m)

    def is_stale(self):
        """Checks script is stale and must be terminated"""
        return time.time() - self.start_time > self._timeout

    @classmethod
    def implements_interface(cls, interface):
        """Check script implements interface"""
        for i in cls.implements:
            if type(i) == interface:
                return True
        return False

    def debug(self, msg):
        """Debug log message"""
        if self.activator.use_canned_session:
            return
        self.logger.debug(u"[%s] %s" % (self.debug_name, unicode(str(msg), "utf8")))

    def error(self, msg):
        """Error log message"""
        self.logger.error(u"[%s] %s" % (self.debug_name, unicode(str(msg), "utf8")))

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

    def guarded_run(self):
        """Wrap around script call with all possible checkings"""
        # Enforce interface type checking
        for i in self.implements:
            self.kwargs = i.script_clean_input(self.profile, **self.kwargs)
        self.debug("Running script: %s (%r)" % (self.name, self.kwargs))
        # Use cached result when available
        if self.cache and self.parent is not None:
            try:
                result = self.get_cache(self.name, self.kwargs)
                self.debug("Script returns with cached result: %r" % result)
                return result
            except KeyError:
                self.debug("Not in call cache: %r, %r" % (self.name,
                                                          self.kwargs))
                pass
            # Calling script body
        self._thread_id = thread.get_ident()
        result = self.execute(**self.kwargs)
        # Enforce interface result checking
        for i in self.implements:
            result = i.script_clean_result(self.profile, result)
        # Cache result when required
        if self.cache and self.parent is not None:
            self.debug("Write to call cache: %s, %s, %r" % (self.name,
                                                            self.kwargs,
                                                            result))
            self.set_cache(self.name, self.kwargs, result)
        self.debug("Script returns with result: %r" % result)
        return result

    def serialize_result(self, result):
        """Serialize script results"""
        return cPickle.dumps(result)

    def run(self):
        """Script thread worker method"""
        self.debug("Running")
        result = None
        try:
            with self.cancelable():
                result = self.guarded_run()
        except self.TimeOutError:
            self.error("Timed out")
            self.e_timeout = True
        except CancelledError:
            self.error("Cancelled")
            self.e_cancel = True
        except self.NotSupportedError:
            self.e_not_supported = True
        except self.LoginError, why:
            self.login_error = why.args[0]
            self.error("Login failed: %s" % self.login_error)
        except self.http.HTTPError, e:
            self.error(str(e))
            self.e_http_error = str(e)
        except self.CLITransportError, why:
            self.error_traceback = why
        except self.CLIDisconnectedError:
            self.e_disconnected = True
        except:
            if self.e_cancel:
                # Race condition caught. Handle CancelledError
                self.error("Cancelled")
            else:
                self.error("Unhandled exception")
                t, v, tb = sys.exc_info()
                r = [str(t), str(v)]
                r += [format_frames(get_traceback_frames(tb))]
                self.error_traceback = "\n".join(r)
                self.debug("Script traceback:\n%s" % self.error_traceback)
                if self.activator.to_save_output:
                    # Save fake result
                    self.activator.save_result(self.error_traceback)
        else:
            # Shutdown session
            if (self.cli_provider and self.profile.shutdown_session and
                    not self.activator.use_canned_session):
                self.debug("Shutting down session")
                self.profile.shutdown_session(self)
                # Serialize result
            self.result = self.serialize_result(result)
            if self.parent is None and self.need_to_save and self.profile.command_save_config:
                self.debug("Saving config")
                self.cli(self.profile.command_save_config)
                # Exit sequence
            if self.parent is None and self.cli_provider is not None and self.profile.command_exit:
                self.debug("Exiting")
                self.cli_provider.submit(self.profile.command_exit)
        self.debug("Closing")
        if self.activator.to_save_output and result:
            self.activator.save_result(result, self.motd)
        if self.cli_provider:
            self.activator.request_call(self.cli_provider.close, flush=True)
        if self.snmp:
            self.snmp.close()
        self.activator.on_script_exit(self)

    def execute(self, **kwargs):
        """
        Default script behavior:
        Pass through _execute_chain and call appropriative handler
        """
        if self._execute_chain and not self.name.endswith(".get_version"):
            # Get version information
            v = self.scripts.get_version()
            # Find and execute proper handler
            for c, f in self._execute_chain:
                if c(self, v):
                    return f(self, **kwargs)
                # Raise error
            raise NotSupportedError()

    def cli_queue_get(self):
        """
        Request CLI provider's queue
        Handle cancel condition
        """
        self.cli_wait = True
        while True:
            try:
                r = self.cli_provider.queue.get(block=True, timeout=1)
                break
            except Queue.Empty:
                pass
            except thread.error:
                # Bug in python's Queue module:
                # Sometimes, tries to release unacquired lock
                self.error("Trying to release unacquired lock")
                time.sleep(1)
        self.cli_wait = False
        if isinstance(r, Exception):
            raise r
        return r

    def reset_cli_queue(self):
        """
        Remove all pending messages from CLI provider's queue
        :return:
        """
        while not self.cli_provider.queue.empty():
            self.cli_wait = True
            r = self.cli_provider.queue.get(block=False)
            self.cli_wait = False
            if isinstance(r, Exception):
                raise r

    def request_cli_provider(self):
        """Run CLI provider if not available"""
        if self.parent:
            self.cli_provider = self.parent.request_cli_provider()
        elif self.cli_provider is None:
            self.debug("Running new provider")
            if self.access_profile.scheme == self.TELNET:
                s_class = CLITelnetSocket
            elif self.access_profile.scheme == self.SSH:
                s_class = CLISSHSocket
            else:
                raise UnknownAccessScheme(self.access_profile.scheme)
            self.cli_provider = s_class(self)
            self.cli_queue_get()
            # Check provider has no flagged errors
            if self.cli_provider.error_traceback:
                raise CLITransportError(
                    self.cli_provider.error_traceback)
            if self.cli_provider.stale:
                raise self.TimeOutError()
            self.debug("CLI Provider is ready")
            # Set up session when necessary
            if (self.profile.setup_session and
                not self.activator.use_canned_session):
                self.debug("Setting up session")
                self.profile.setup_session(self)
            # Disable pager when necessary
            if self.to_disable_pager:
                self.debug("Disable paging")
                self.to_disable_pager = False
                self.cli(self.profile.command_disable_pager, ignore_errors=True)
        return self.cli_provider

    def cli(self, cmd, command_submit=None, bulk_lines=None, list_re=None,
            cached=False, file=None, ignore_errors=False, nowait=False):
        """
        Execute CLI command and return a result.
        if list_re is None, return a string
        if list_re is regular expression object, return a list of dicts (group name -> value),
            one dict per matched line
        """
        self.debug("cli(%s)" % cmd)
        from_cache = False
        self.cli_debug(cmd, ">")
        # Submit command
        command_submit = self.profile.command_submit if command_submit is None else command_submit
        if self.activator.use_canned_session:
            try:
                data = self.activator.cli(cmd)
            except KeyError:
                raise self.CLISyntaxError(cmd)
        else:
            # Check result is cached
            cc = "CLI:" + cmd  # Cache key
            cache = self.root.cmd_cache
            cached = cached or self.root.is_cached
            if cached and cc in cache:
                # Get result from cache
                data = cache[cc]
                from_cache = True
            elif file:
                # Read file instead of executing command
                with open(file) as f:
                    data = f.read()
            else:
                # Check CLI provider is ready
                self.request_cli_provider()
                # Execute command
                self.cli_provider.submit(cmd,
                    command_submit=command_submit,
                    bulk_lines=bulk_lines)
                if self.cli_provider.is_broken_pipe:
                    raise self.CLIDisconnectedError()
                if nowait:
                    data = ""
                else:
                    data = self.cli_queue_get()
                if data is None:
                    if self.cli_provider.error_traceback:
                        # Transport-level CLI error occured
                        raise self.CLITransportError(
                            self.cli_provider.error_traceback)
                    elif self.cli_provider.stale:
                        raise self.TimeOutError()
                if cached:
                    # Store back to cache
                    cache[cc] = data
        # Encode to UTF8 if requested
        if self.encoding and isinstance(data, basestring):
            data = unicode(data, self.encoding).encode("utf8")
        # Save canned output if requested
        if self.activator.to_save_output:
            self.activator.save_interaction("cli", cmd, data)
        if isinstance(data, Exception):
            # Exception captured
            raise data
        if not ignore_errors:
            # Check for syntax error
            if (self.profile.rx_pattern_syntax_error and
                self.profile.rx_pattern_syntax_error.search(data)):
                raise self.CLISyntaxError(data)
            # Then check for operaion error
            if (self.profile.rx_pattern_operation_error and
                self.profile.rx_pattern_operation_error.search(data)):
                raise self.CLIOperationError(data)
        # Echo cancelation
        if self.strip_echo and data.lstrip().startswith(cmd):
            data = data.lstrip()
            if data.startswith(cmd + "\n"):
                # Remove first line
                data = self.strip_first_lines(data.lstrip())
            else:
                # Some switches, like ProCurve do not send \n after the echo
                data = data[len(cmd):]
        # Convert to list when required
        if list_re:
            r = []
            for l in data.splitlines():
                match = list_re.match(l.strip())
                if match:
                    r += [match.groupdict()]
            data = r
        dm = ["cli(%s) returns%s:" % (cmd, " cached result" if from_cache else "")]
        l = "===[ %s ]" % cmd
        dm += [l + "=" * max(0, 72 - len(l))]
        dm += [repr(data)]
        dm += ["=" * 72]
        self.debug("\n".join(dm))
        self.cli_debug(data, "<")
        return data

    def cli_stream(self, cmd, command_submit=None):
        self.debug("cli_stream(%s)" % cmd)
        if command_submit is None:
            command_submit = self.profile.command_submit
        # Check CLI provider is ready
        self.request_cli_provider()
        # Run streaming
        self.cli_provider.submit(cmd,
            command_submit=command_submit, streaming=True)
        # Execute command
        while True:
            data = self.cli_queue_get()
            if data == True:
                break
            if data is not None:
                seq = (yield data)  # Get sequence to send
                if seq:
                    self.cli_provider.write(seq)
            else:
                break
        # Reset stream data
        self.reset_cli_queue()

    def cli_object_stream(self, cmd, command_submit=None,
                          parser=None, cmd_next=None, cmd_stop=None):
        """

        :param cmd:
        :param command_submit:
        :param parser: callable accepting buffer and returning
                       (key, data, rest) or None.
                       key - string with object distinguisher
                       data - dict containing attributes
                       rest -- unparsed rest of string
        :param cmd_next: Sequence to go to the next page
        :param cmd_stop: Sequence to stop
        :return:
        """
        stream = self.cli_stream(cmd, command_submit)
        objects = []
        seen = set()
        input = ""
        r_key = None
        nr = 0
        stop_sent = False
        for data in stream:
            # Check for syntax error
            if (self.profile.rx_pattern_syntax_error and
                    self.profile.rx_pattern_syntax_error.search(data)):
                raise self.CLISyntaxError(data)
            # Then check for operaion error
            if (self.profile.rx_pattern_operation_error and
                    self.profile.rx_pattern_operation_error.search(data)):
                raise self.CLIOperationError(data)
            input += data
            while input:
                r = parser(input)
                if r is None:
                    break  # No match
                key, obj, input = r
                if key not in seen:
                    seen.add(key)
                    objects += [obj]
                    nr = 0
                    r_key = None
                else:
                    if r_key:
                        if r_key == key:
                            nr += 1
                            if nr >= 3 and cmd_stop and not stop_sent:
                                # Stop loop at final page
                                # After 3 repeats
                                self.debug("Stopping stream. Sending %r" % cmd_stop)
                                try:
                                    stream.send(cmd_stop)
                                    stop_sent = True
                                except StopIteration:
                                    pass  # Ignore stopped generator
                    else:
                        r_key = key
                        if cmd_next:
                            self.debug("Next screen. Sending %r" % cmd_next)
                            stream.send(cmd_next)
        dm = ["cli_object_stream(%s) returns:" % cmd]
        l = "===[ %s ]" % cmd
        dm += [l + "=" * max(0, 72 - len(l))]
        dm += [repr(objects)]
        dm += ["=" * 72]
        self.debug("\n".join(dm))
        return objects

    def cleaned_config(self, config):
        """
        Clean up config from all unnecessary trash
        """
        return self.profile.cleaned_config(config)

    def strip_first_lines(self, text, lines=1):
        """Strip first lines"""
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

    def cancel_script(self):
        """
        Cancel script
        """
        # Can cancel only inside guarded_run
        if not self.is_cancelable:
            self.error("Cannot cancel non-cancelable script")
            return
        if not self.isAlive():
            self.error("Trying to kill already dead thread")
            return
        if not self._thread_id:
            self.error("Cannot cancel the script without thread_id")
            return
        # When stuck in CLI, send cancel message
        if self.cli_provider and self.cli_wait:
            self.error("Stuck in CLI. Cancelling")
            self.cli_provider.queue.put(CancelledError())
            return
        # As last resort
        # raise CancelledError in script's thread
        self.e_cancel = True
        r = ctypes.pythonapi.PyThreadState_SetAsyncExc(
            ctypes.c_long(self._thread_id),
            ctypes.py_object(CancelledError))
        if r == 1:
            self.debug("Cancel event sent")
            # Remote exception raised.
            if self.cli_provider:
                # Awake script thread if waiting for CLI
                self.cli_provider.queue.put(None)
                self.cli_provider.queue.put(None)
        elif r > 1:
            # Failed to raise exception
            # Revert back thread state
            ctypes.pythonapi.PyThreadState_SetAsyncExc(
                ctypes.c_long(self._thread_id), None)
            self.error("Failed to cancel script")

    def hang(self):
        """
        Debugging helper to hang the script
        """
        logging.debug("Hanging script")
        e = threading.Event()
        while True:
            e.wait(1)

    def configure(self):
        """Returns configuration context"""
        return ConfigurationContextManager(self)

    def cancelable(self):
        """Return cancelable context"""
        return CancellableContextManager(self)

    def ignored_exceptions(self, iterable):
        """Return ignorable exceptions context"""
        return IgnoredExceptionsContextManager(iterable)

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
        """Return message of the day"""
        if self.activator.use_canned_session:
            return self.activator.get_motd()
        if (not self.cli_provider and
            self.access_profile.scheme in (SSH, TELNET)):
            self.request_cli_provider()
            return self.cli_provider.motd
        return ""

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
            hexbin[c] for c in
            "".join("%02x" % ord(d) for d in s)
        )

    @classmethod
    def get_scheme_id(cls, scheme):
        """Return scheme id by string name"""
        try:
            return {
                "telnet": TELNET,
                "ssh": SSH,
                "http": HTTP,
                }[scheme]
        except KeyError:
            raise UnknownAccessScheme(scheme)

    def push_prompt_pattern(self, pattern):
        self.request_cli_provider()
        self.cli_provider.push_prompt_pattern(pattern)

    def pop_prompt_pattern(self):
        self.cli_provider.pop_prompt_pattern()
