# -*- coding: utf-8 -*-
##----------------------------------------------------------------------
## CLI FSM
##----------------------------------------------------------------------
## Copyright (C) 2007-2015 The NOC Project
## See LICENSE for details
##----------------------------------------------------------------------

## Python modules
import socket
import re
import functools
## Third-party modules
import tornado.gen
import tornado.ioloop
import tornado.iostream
## NOC modules
from noc.lib.log import PrefixLoggerAdapter
from noc.lib.text import replace_re_group


class CLI(object):
    name = "cli"
    default_port = None
    iostream_class = None
    BUFFER_SIZE = 1048576
    MATCH_TAIL = 256
    # Retries on immediate disconnect
    CONNECT_RETRIES = 3
    # Timeout after immediate disconnect
    CONNECT_TIMEOUT = 3

    class CLIError(Exception):
        pass

    class InvalidPagerPattern(Exception):
        pass

    def __init__(self, script, tos=None):
        self.script = script
        self.profile = script.profile
        self.logger = PrefixLoggerAdapter(self.script.logger, self.name)
        self.iostream = None
        self.motd = ""
        self.ioloop = None
        self.command = None
        self.more_patterns = []
        self.more_commands = []
        self.prompt_stack = []
        self.patterns = self.build_patterns()
        self.buffer = ""
        self.is_started = False
        self.result = None
        self.error = None
        self.pattern_table = None
        self.collected_data = []
        self.tos = tos

    def close(self):
        if self.iostream:
            self.iostream.close()
        if self.ioloop:
            self.logger.debug("Closing IOLoop")
            self.ioloop.close(all_fds=True)
            self.ioloop = None

    def create_iostream(self):
        s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        if self.tos:
            s.setsockopt(
                socket.IPPROTO_IP, socket.IP_TOS, self.tos
            )
        return self.iostream_class(s, self)

    def execute(self, cmd, obj_parser=None, cmd_next=None, cmd_stop=None):
        self.buffer = ""
        self.command = cmd
        if not self.ioloop:
            self.logger.debug("Creating IOLoop")
            self.ioloop = tornado.ioloop.IOLoop()
        if obj_parser:
            parser = functools.partial(
                self.parse_object_stream,
                obj_parser, cmd_next, cmd_stop
            )
        else:
            parser = self.read_until_prompt
        self.ioloop.run_sync(functools.partial(self.submit, parser))
        if self.error:
            raise self.error
        else:
            return self.result

    @tornado.gen.coroutine
    def submit(self, parser=None):
        # Create iostream and connect, when necessary
        if not self.iostream:
            self.iostream = self.create_iostream()
            address = (
                self.script.credentials.get("address"),
                self.script.credentials.get("cli_port", self.default_port)
            )
            self.logger.debug("Connecting %s", address)
            try:
                yield self.iostream.connect(address)
            except tornado.iostream.StreamClosedError:
                self.logger.debug("Connection refused")
                self.error = self.CLIError("Connection refused")
                raise tornado.gen.Return(None)
            self.logger.debug("Connected")
            yield self.iostream.startup()
        # Perform all necessary login procedures
        if not self.is_started:
            self.on_start()
            self.motd = yield self.read_until_prompt()
            self.script.set_motd(self.motd)
            self.is_started = True
        # Send command
        # @todo: encode to object's encoding
        self.send(self.command)
        parser = parser or self.read_until_prompt
        self.result = yield parser()
        self.logger.debug("Command: %s\n%s",
                          self.command.strip(), self.result)
        raise tornado.gen.Return(self.result)

    def cleaned_input(self, s):
        """
        Clean up received input and wipe out control sequences
        and rogue chars
        """
        # Wipe out rogue chars
        if self.profile.rogue_chars:
            for rc in self.profile.rogue_chars:
                try:
                    s = rc.sub("", s)  # rc is compiled regular expression
                except AttributeError:
                    s = s.replace(rc, "")  # rc is a string
        # Clean control sequences
        return self.profile.cleaned_input(s)

    @tornado.gen.coroutine
    def send(self, cmd):
        # @todo: Apply encoding
        cmd = str(cmd)
        self.logger.debug("Send: %r", cmd)
        yield self.iostream.write(cmd)

    @tornado.gen.coroutine
    def read_until_prompt(self):
        connect_retries = self.CONNECT_RETRIES
        while True:
            try:
                r = yield self.iostream.read_bytes(self.BUFFER_SIZE,
                                                   partial=True)
            except tornado.iostream.StreamClosedError:
                # Check if remote end closes connection just
                # after connection established
                if not self.is_started and connect_retries:
                    self.logger.info(
                        "Connection reset. %d retries left. Waiting %d seconds",
                        connect_retries, self.CONNECT_TIMEOUT
                    )
                    while connect_retries:
                        yield tornado.gen.sleep(self.CONNECT_TIMEOUT)
                        connect_retries -= 1
                        self.iostream = self.create_iostream()
                        address = (
                            self.script.credentials.get("address"),
                            self.script.credentials.get("cli_port", self.default_port)
                        )
                        self.logger.debug("Connecting %s", address)
                        try:
                            yield self.iostream.connect(address)
                            yield self.iostream.startup()
                            break
                        except tornado.iostream.StreamClosedError:
                            if not connect_retries:
                                raise tornado.iostream.StreamClosedError()
                    continue
                else:
                    raise tornado.iostream.StreamClosedError()
            self.logger.debug("Received: %r", r)
            # Clean input
            self.buffer += self.cleaned_input(r)
            # Try to find matched pattern
            offset = max(0, len(self.buffer) - self.MATCH_TAIL)
            for rx, handler in self.pattern_table.iteritems():
                match = rx.search(self.buffer, offset)
                if match:
                    self.logger.debug("Match: %s", rx.pattern)
                    matched = self.buffer[:match.start()]
                    self.buffer = self.buffer[match.end():]
                    r = handler(matched, match)
                    if r is not None:
                        raise tornado.gen.Return(r)

    @tornado.gen.coroutine
    def parse_object_stream(self, parser=None,
                            cmd_next=None, cmd_stop=None):
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
        self.logger.debug("Parsing object stream")
        objects = []
        seen = set()
        buffer = ""
        repeats = 0
        r_key = None
        stop_sent = False
        done = False
        while not done:
            r = yield self.iostream.read_bytes(self.BUFFER_SIZE,
                                               partial=True)
            self.logger.debug("Received: %r", r)
            buffer = self.cleaned_input(buffer + r)
            # Check for syntax error
            if (self.profile.rx_pattern_syntax_error and
                    self.profile.rx_pattern_syntax_error.search(self.buffer)):
                self.error = self.script.CLISyntaxError(self.buffer)
                break
            # Then check for operaion error
            if (self.profile.rx_pattern_operation_error and
                    self.profile.rx_pattern_operation_error.search(self.buffer)):
                self.error = self.script.CLIOperationError(self.buffer)
                break
            # Parse all possible objects
            while buffer:
                pr = parser(buffer)
                if not pr:
                    break  # No new objects
                key, obj, buffer = pr
                if key not in seen:
                    seen.add(key)
                    objects += [obj]
                    repeats = 0
                    r_key = None
                elif r_key:
                    if r_key == key:
                        repeats += 1
                        if repeats >= 3 and cmd_stop and not stop_sent:
                            # Stop loop at final page
                            # After 3 repeats
                            self.logger.debug("Stopping stream. Sending %r" % cmd_stop)
                            self.send(cmd_stop)
                            stop_sent = True
                else:
                    r_key = key
                    if cmd_next:
                        self.logger.debug("Next screen. Sending %r" % cmd_next)
                        self.send(cmd_next)
            # Check for prompt
            for rx, handler in self.pattern_table.iteritems():
                offset = max(0, len(buffer) - self.MATCH_TAIL)
                match = rx.search(buffer, offset)
                if match:
                    self.logger.debug("Match: %s", rx.pattern)
                    matched = buffer[:match.start()]
                    buffer = self.buffer[match.end():]
                    r = handler(matched, match)
                    if r is not None:
                        self.logger.debug("Prompt matched")
                        done = True
                        break
        raise tornado.gen.Return(objects)

    def send_pager_reply(self, data, match):
        """
        Send proper pager reply
        """
        pg = match.group(0)
        for p, c in zip(self.more_patterns, self.more_commands):
            if p.search(pg):
                self.collected_data += [data]
                self.send(c)
                return
        raise self.InvalidPagerPattern(pg)

    def expect(self, patterns):
        """
        Send command if not none and set reply patterns
        """
        self.pattern_table = {}
        for pattern_name in patterns:
            rx = self.patterns[pattern_name]
            if not rx:
                continue
            self.pattern_table[rx] = patterns[pattern_name]

    def on_start(self, data=None, match=None):
        self.logger.debug("State: <START>")
        self.expect({
            "username": self.on_username,
            "password": self.on_password,
            "prompt": self.on_prompt,
            "pager": self.send_pager_reply,
            "unprivileged_prompt": self.on_unprivileged_prompt
        })

    def on_username(self, data, match):
        self.logger.debug("State: <USERNAME>")
        self.send(
            self.script.credentials.get("user", "") +
            (self.profile.username_submit or "\n")
        )
        self.expect({
            "username": self.on_failure,
            "password": self.on_password,
            "unprivileged_prompt": self.on_unprivileged_prompt,
            "prompt": self.on_prompt
        })

    def on_password(self, data, match):
        self.logger.debug("State: <PASSWORD>")
        self.send(
            self.script.credentials.get("password", "") +
            (self.profile.username_submit or "\n")
        )
        self.expect({
            "username": self.on_failure,
            "password": self.on_failure,
            "unprivileged_prompt": self.on_unprivileged_prompt,
            "prompt": self.on_prompt,
            "pager": self.send_pager_reply
        })

    def on_unprivileged_prompt(self, data, match):
        self.logger.debug("State: <UNPRIVILEGED_PROMPT>")
        if not self.profile.command_super:
            self.on_failure(data, match)
        self.send(
            self.profile.command_super +
            (self.profile.command_submit or "\n")
        )
        self.expect({
            "username": self.on_super_username,
            "password": self.on_super_password,
            "prompt": self.on_prompt
        })

    def on_failure(self, data, match):
        self.logger.debug("State: <FAILURE>")
        raise self.CLIError(self.buffer or None)

    def on_prompt(self, data, match):
        self.logger.debug("State: <PROMT>")
        if not self.is_started:
            self.resolve_pattern_prompt(match)
        d = "".join(self.collected_data + [data])
        self.collected_data = []
        self.expect({
            "prompt": self.on_prompt,
            "pager": self.send_pager_reply
        })
        return d

    def on_super_username(self, data, match):
        self.logger.debug("State: SUPER_USERNAME")
        self.send(
            (self.script.credentials.get("user", "") or "") +
            (self.profile.username_submit or "\n")
        )
        self.expect({
            "username": self.on_failure,
            "password": self.on_super_password,
            "unprivileged_prompt": self.on_unprivileged_prompt,
            "prompt": self.on_prompt,
            "pager": self.send_pager_reply
        })

    def on_super_password(self, data, match):
        self.send(
            (self.script.credentials.get("super_password", "") or "") +
            (self.profile.username_submit or "\n")
        )
        self.expect({
            "prompt": self.on_prompt,
            "password": self.on_failure,
            "pager": self.send_pager_reply,
            "unprivileged_prompt": self.on_failure
        })

    def build_patterns(self):
        """
        Return dict of compiled regular expressions
        """
        patterns = {
            "username": re.compile(self.profile.pattern_username,
                                   re.DOTALL | re.MULTILINE),
            "password": re.compile(self.profile.pattern_password,
                                   re.DOTALL | re.MULTILINE),
            "prompt": re.compile(self.profile.pattern_prompt,
                                 re.DOTALL | re.MULTILINE)
        }
        if self.profile.pattern_unpriveleged_prompt:
            patterns["unprivileged_prompt"] = re.compile(
                self.profile.pattern_unpriveleged_prompt,
                re.DOTALL | re.MULTILINE
            )
        else:
            patterns["unprivileged_prompt"] = None
        if isinstance(self.profile.pattern_more, basestring):
            more_patterns = [self.profile.pattern_more]
            self.more_commands = [self.profile.command_more]
        else:
            # .more_patterns is a list of (pattern, command)
            more_patterns = [x[0] for x in self.profile.pattern_more]
            self.more_commands = [x[1] for x in self.profile.pattern_more]
        # Merge pager patterns
        patterns["pager"] = re.compile(
            "|".join([r"(%s)" % p for p in more_patterns]),
            re.DOTALL | re.MULTILINE
        )
        self.more_patterns = [re.compile(p, re.MULTILINE | re.DOTALL)
                              for p in more_patterns]
        return patterns

    def resolve_pattern_prompt(self, match):
        """
        Resolve adaptive pattern prompt
        """
        old_pattern_prompt = self.patterns["prompt"].pattern
        pattern_prompt = old_pattern_prompt
        sl = self.profile.can_strip_hostname_to
        for k, v in match.groupdict().iteritems():
            if v:
                if k == "hostname" and sl and len(v) > sl:
                    ss = list(reversed(v[sl:]))
                    v = re.escape(v[:sl]) + reduce(
                        lambda x, y: "(?:%s%s)?" % (
                            re.escape(y), x),
                        ss[1:],
                        "(?:%s)?" % re.escape(ss[0])
                    )
                else:
                    v = re.escape(v)
                pattern_prompt = replace_re_group(
                    pattern_prompt,
                    "(?P<%s>" % k,
                    v
                )
                pattern_prompt = replace_re_group(
                    pattern_prompt,
                    "(?P=%s" % k,
                    v
                )
            else:
                self.logger.error("Invalid prompt pattern")
        if old_pattern_prompt != pattern_prompt:
            self.logger.debug("Refining pattern prompt to %r",
                              pattern_prompt
                              )
        self.patterns["prompt"] = re.compile(pattern_prompt,
                                             re.DOTALL | re.MULTILINE)

    def push_prompt_pattern(self, pattern):
        """
        Override prompt pattern
        """
        self.logger.debug("New prompt pattern: %s", pattern)
        self.prompt_stack += [
            self.patterns["prompt"]
        ]
        self.patterns["prompt"] = re.compile(
            pattern, re.DOTALL | re.MULTILINE
        )
        self.pattern_table[self.patterns["prompt"]] = self.on_prompt

    def pop_prompt_pattern(self):
        """
        Restore prompt pattern
        """
        self.logger.debug("Restore prompt pattern")
        pattern = self.prompt_stack.pop(-1)
        self.patterns["prompt"] = pattern
        self.pattern_table[self.patterns["prompt"]] = self.on_prompt

    def get_motd(self):
        """
        Return collected message of the day
        """
        return self.motd
