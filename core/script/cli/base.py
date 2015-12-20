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
## Third-party modules
import tornado.gen
import tornado.ioloop
## NOC modules
from noc.lib.log import PrefixLoggerAdapter
from noc.lib.text import replace_re_group


class CLI(object):
    name = "cli"
    default_port = None
    iostream_class = None
    BUFFER_SIZE = 1048576
    MATCH_TAIL = 256

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

    def execute(self, cmd):
        self.buffer = ""
        self.command = cmd
        if not self.ioloop:
            self.logger.debug("Creating IOLoop")
            self.ioloop = tornado.ioloop.IOLoop()
        self.ioloop.run_sync(self.submit)
        return self.result

    @tornado.gen.coroutine
    def submit(self):
        # Create iostream and connect, when necessary
        if not self.iostream:
            self.iostream = self.create_iostream()
            address = (
                self.script.credentials.get("address"),
                self.script.credentials.get("port", self.default_port)
            )
            self.logger.debug("Connecting %s", address)
            yield self.iostream.connect(address)
            self.logger.debug("Connected")
            yield self.iostream.startup()
        # Perform all necessary login procedures
        if not self.is_started:
            self.on_start()
            self.motd = yield self.read_until_prompt()
            self.is_started = True
        # Send command
        # @todo: encode to object's encoding
        self.send(self.command)
        result = yield self.read_until_prompt()
        self.logger.debug("Command: %s\n%s",
                          self.command.strip(), result)
        # @todo: decode from object's encoding
        self.result = result
        raise tornado.gen.Return(result)

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
        while True:
            r = yield self.iostream.read_bytes(self.BUFFER_SIZE,
                                               partial=True)
            self.logger.debug("Received: %r", r)
            # Clean input
            self.buffer += self.cleaned_input(r)
            # Try to find matched pattern
            for rx, handler in self.pattern_table.iteritems():
                offset = max(0, len(self.buffer) - self.MATCH_TAIL)
                match = rx.search(self.buffer, offset)
                if match:
                    self.logger.debug("Match: %s", rx.pattern)
                    matched = self.buffer[:match.start()]
                    self.buffer = self.buffer[match.end():]
                    r = handler(matched, match)
                    if r is not None:
                        raise tornado.gen.Return(r)

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
            "prompt": self.on_prompt,
            "unprivileged_prompt": self.on_unprivileged_prompt
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
        self.send(self.profile.command_super)
        self.expect({
            "username": self.on_super_username,
            "password": self.on_super_password,
            "prompt": self.on_prompt
        })

    def on_failure(self, data, match):
        self.logger.debug("State: <FAILURE>")
        raise self.CLIError()

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
            self.script.credentials.get("user", "") +
            (self.profile.username_submit or "\n")
        )
        self.expect({
            "username": self.on_failure,
            "password": self.on_super_password,
            "prompt": self.on_prompt,
            "unprivileged_prompt": self.on_unprivileged_prompt,
            "pager": self.send_pager_reply
        })

    def on_super_password(self, data, match):
        self.send(
            self.script.credentials.get("super_password", "") +
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

    def pop_prompt_pattern(self):
        """
        Restore prompt pattern
        """
        self.logger.debug("Restore prompt pattern")
        pattern = self.prompt_stack.pop(-1)
        self.patterns["prompt"] = re.compile(
            pattern, re.DOTALL | re.MULTILINE
        )

    def get_motd(self):
        """
        Return collected message of the day
        """
        return self.motd
