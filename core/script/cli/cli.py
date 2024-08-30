# ----------------------------------------------------------------------
# CLI FSM
# ----------------------------------------------------------------------
# Copyright (C) 2007-2024 The NOC Project
# See LICENSE for details
# ----------------------------------------------------------------------

# Python modules
import re
import functools
from functools import reduce
import asyncio
from typing import Optional, Any, Type, Callable, Dict, Set, Union

# NOC modules
from noc.core.text import replace_re_group
from noc.config import config
from noc.core.span import Span
from noc.core.perf import metrics
from noc.core.comp import smart_bytes, smart_text
from noc.core.ioloop.util import IOLoopContext
from .error import (
    CLIError,
    CLIAuthFailed,
    CLINoSuperCommand,
    CLILowPrivileges,
    CLIConnectionRefused,
    CLIConnectionReset,
    CLIStartTimeout,
    CLISetupTimeout,
    CLIUsernameTimeout,
    CLIPasswordTimeout,
    CLISuperTimeout,
    CLISuperUsernameTimeout,
    CLISuperPasswordTimeout,
)
from .base import BaseCLI


class CLI(BaseCLI):
    name = "cli"
    BUFFER_SIZE = config.activator.buffer_size
    MATCH_TAIL = 256
    # Buffer to check missed ECMA control characters
    MATCH_MISSED_CONTROL_TAIL = 8
    SYNTAX_ERROR_CODE = b"+@@@NOC:SYNTAXERROR@@@+"

    class InvalidPagerPattern(Exception):
        pass

    class InvalidPagerCommand(Exception):
        pass

    def __init__(self, script, tos=None):
        super().__init__(script, tos)
        self.motd = ""
        self.command = None
        self.prompt_stack = []
        self.patterns = self.profile.patterns.copy()
        self.buffer: bytes = b""
        self.result = None
        self.error = None
        self.pattern_table = None
        self.collected_data = []
        self.setup_complete = False
        self.to_raise_privileges = script.credentials.get("raise_privileges", True)
        self.state = "start"
        self.ignore_errors = None
        self.allow_empty_response = None
        self.native_encoding = self.script.native_encoding
        self.prompt_matched = False
        self.script_labels = script.get_labels()
        self.labels = None
        # State retries
        self.super_password_retries = self.profile.cli_retries_super_password
        self.cli_retries_unprivileged_mode = self.profile.cli_retries_unprivileged_mode
        #
        self._to_setup_session = bool(self.profile.setup_session)
        self._to_disable_pager = bool(self.profile.command_disable_pager)
        self._in_setup = False

    def set_state(self, state):
        self.logger.debug("Changing state to <%s>", state)
        self.state = state

    def execute(
        self,
        cmd: str,
        obj_parser: Optional[Callable] = None,
        cmd_next: Optional[bytes] = None,
        cmd_stop: Optional[bytes] = None,
        ignore_errors: bool = False,
        allow_empty_response: bool = True,
        labels: Optional[Union[str, Set[str]]] = None,
    ) -> str:
        self.buffer = b""
        self.command = cmd
        self.error = None
        self.ignore_errors = ignore_errors
        self.allow_empty_response = allow_empty_response
        # Labels
        labels = labels or set()
        if isinstance(labels, str):
            labels = {labels}
        self.labels = self.script_labels | labels
        if obj_parser:
            parser = functools.partial(
                self.parse_object_stream, obj_parser, smart_bytes(cmd_next), smart_bytes(cmd_stop)
            )
        else:
            parser = self.read_until_prompt
        with Span(
            server=self.script.credentials.get("address"), service=self.name, in_label=cmd
        ) as s:
            with IOLoopContext() as loop:
                loop.run_until_complete(self.submit(parser))
            if self.error:
                if s:
                    s.error_text = str(self.error)
                raise self.error
            return self.result

    async def start_stream(self):
        await super().start_stream()
        # Process motd
        if not self.is_started:
            await self.on_start()
            motd = await self.read_until_prompt()
            self.motd = smart_text(motd, errors="ignore", encoding=self.native_encoding)
            self.is_started = True

    async def submit(self, parser=None):
        # Create iostream and connect, when necessary
        if not self.stream or not self.is_started:
            try:
                await self.start_stream()
            except ConnectionRefusedError:
                self.error = CLIConnectionRefused("Connection refused")
                metrics["cli_connection_refused", ("proto", self.name)] += 1
                return
            except CLIAuthFailed as e:
                self.error = CLIAuthFailed(*e.args)
                self.logger.info("CLI Authentication failed")
                # metrics["cli_connection_refused", ("proto", self.name)] += 1
                return
        metrics["cli_commands", ("proto", self.name)] += 1
        # Send command
        # @todo: encode to object's encoding
        if self.profile.batch_send_multiline or self.profile.command_submit not in self.command:
            await self.send(self.command)
        else:
            # Send multiline commands line-by-line
            for cmd in self.command.split(self.profile.command_submit):
                # Send line
                await self.send(cmd + self.profile.command_submit)
                # Await response
                await self.stream.wait_for_read()
        parser = parser or self.read_until_prompt
        self.result = await parser()
        self.logger.debug(
            "Command: %s\n%s", self.command.strip(), smart_text(self.result, errors="replace")
        )
        if (
            self.profile.rx_pattern_syntax_error
            and not self.ignore_errors
            and parser == self.read_until_prompt
            and (
                self.profile.rx_pattern_syntax_error.search(self.result)
                or self.result == self.SYNTAX_ERROR_CODE
            )
        ):
            error_text = self.result
            if self.profile.send_on_syntax_error and not self.is_beef():
                self.allow_empty_response = True
                await self.on_error_sequence(
                    self.profile.send_on_syntax_error, self.command, error_text
                )
            self.error = self.script.CLISyntaxError(error_text)
            self.result = None
        return self.result

    def is_beef(self) -> bool:
        return False

    def cleaned_input(self, s: bytes) -> bytes:
        """
        Clean up received input and wipe out control sequences
        and rogue chars
        """
        # Wipe out rogue chars
        if self.profile.rogue_chars:
            s = self.profile.clean_rogue_chars(s)
        # Clean control sequences
        return self.profile.cleaned_input(s)

    async def send(self, cmd: bytes, shadow=False) -> None:
        # cmd = str(cmd)
        self.logger.debug("Send: %r", cmd if not shadow else "*******")
        await self.stream.write(cmd)

    async def read_until_prompt(self):
        while True:
            try:
                metrics["cli_reads", ("proto", self.name)] += 1
                r = await self.stream.read(self.BUFFER_SIZE)
            except (asyncio.TimeoutError, TimeoutError):
                self.logger.warning("Timeout error")
                metrics["cli_timeouts", ("proto", self.name)] += 1
                # Stream must be closed to prevent hanging read callbacks
                # @todo: Really? May be changed during migration to asyncio
                self.close_stream()
                raise self.timeout_exception_cls()
            if not r:
                self.logger.debug("Connection reset")
                # For socket close on device we close it on system
                self.close_stream()
                await self.on_failure(r, None, error_cls=CLIConnectionReset)
            if r == self.SYNTAX_ERROR_CODE:
                metrics["cli_syntax_errors", ("proto", self.name)] += 1
                return self.SYNTAX_ERROR_CODE
            metrics["cli_read_bytes", ("proto", self.name)] += len(r)
            if self.script.to_track:
                self.script.push_cli_tracking(r, self.state)
            self.logger.debug("Received: %r", r)
            # Clean input
            if self.buffer.find(b"\x1b", -self.MATCH_MISSED_CONTROL_TAIL) != -1:
                self.buffer = self.cleaned_input(self.buffer + r)
            else:
                self.buffer += self.cleaned_input(r)
            # Try to find matched pattern
            offset = max(0, len(self.buffer) - self.MATCH_TAIL)
            for rx, handler in self.pattern_table.items():
                match = rx.search(self.buffer, offset)
                if match:
                    self.logger.debug("Match: %s", rx.pattern)
                    matched = self.buffer[: match.start()]
                    self.buffer = self.buffer[match.end() :]
                    if isinstance(handler, tuple):
                        metrics["cli_state", ("state", handler[0].__name__)] += 1
                        r = await handler[0](matched, match, *handler[1:])
                    else:
                        metrics["cli_state", ("state", handler.__name__)] += 1
                        r = await handler(matched, match)
                    if r is not None:
                        return r
                    break  # This state is processed

    async def parse_object_stream(self, parser=None, cmd_next=None, cmd_stop=None):
        """
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
        buffer = b""
        repeats = 0
        r_key = None
        stop_sent = False
        done = False
        while not done:
            r = await self.stream.read(self.BUFFER_SIZE)
            if self.script.to_track:
                self.script.push_cli_tracking(r, self.state)
            self.logger.debug("Received: %r", r)
            buffer = self.cleaned_input(buffer + r)
            # Check for syntax error
            if (
                self.profile.rx_pattern_syntax_error
                and not self.ignore_errors
                and self.profile.rx_pattern_syntax_error.search(buffer)
            ):
                error_text = buffer
                if self.profile.send_on_syntax_error:
                    await self.on_error_sequence(
                        self.profile.send_on_syntax_error, self.command, error_text
                    )
                self.error = self.script.CLISyntaxError(error_text)
                break
            # Then check for operation error
            if (
                self.profile.rx_pattern_operation_error_str
                and self.profile.rx_pattern_operation_error.search(buffer)
            ):
                self.error = self.script.CLIOperationError(buffer)
                break
            # Parse all possible objects
            while buffer:
                pr = parser(smart_text(buffer, errors="replace"))
                if not pr:
                    break  # No new objects
                key, obj, buffer = pr
                buffer = smart_bytes(buffer)
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
                            await self.send(cmd_stop)
                            stop_sent = True
                else:
                    r_key = key
                    if cmd_next:
                        self.logger.debug("Next screen. Sending %r" % cmd_next)
                        await self.send(cmd_next)
            # Check for prompt
            for rx, handler in self.pattern_table.items():
                offset = max(0, len(buffer) - self.MATCH_TAIL)
                match = rx.search(buffer, offset)
                if match:
                    self.logger.debug("Match: %s", rx.pattern)
                    matched = buffer[: match.start()]
                    buffer = self.buffer[match.end() :]
                    r = await handler(matched, match)
                    if r is not None:
                        self.logger.debug("Prompt matched")
                        done = True
                        break
        return objects

    async def send_pager_reply(self, data, match):
        """
        Send proper pager reply
        """
        pg = match.group(0)
        for p, c in self.patterns["more_patterns_commands"]:
            if p.search(pg):
                self.collected_data += [data]
                if isinstance(c, bytes):
                    await self.send(c)
                    return
                elif isinstance(c, dict):
                    # handling case if command is dict
                    default_command = c.get(None)
                    for ck, cv in c.items():
                        if isinstance(ck, tuple):
                            ck = set(ck)
                            if ck & self.labels == ck:
                                await self.send(cv)
                                return
                    if default_command:
                        await self.send(default_command)
                        return
                    raise self.InvalidPagerCommand("Absent required None key")
                else:
                    raise self.InvalidPagerCommand(c)
        raise self.InvalidPagerPattern(pg)

    def expect(
        self,
        patterns: Dict[str, Any],
        timeout: Optional[float] = None,
        error: Optional[Type[Exception]] = None,
    ):
        """
        Send command if not none and set reply patterns
        """
        self.pattern_table = {}
        for pattern_name in patterns:
            rx = self.patterns.get(pattern_name)
            if not rx:
                continue
            self.pattern_table[rx] = patterns[pattern_name]
        self.set_timeout(timeout, error=error)

    async def on_start(self, data=None, match=None):
        self.set_state("start")
        if self.profile.setup_sequence and not self.setup_complete:
            self.expect(
                {"setup": self.on_setup_sequence},
                self.profile.cli_timeout_setup,
                error=CLISetupTimeout,
            )
        else:
            self.expect(
                {
                    "username": self.on_username,
                    "password": self.on_password,
                    "unprivileged_prompt": self.on_unprivileged_prompt,
                    "prompt": self.on_prompt,
                    "pager": self.send_pager_reply,
                },
                self.profile.cli_timeout_start,
                error=CLIStartTimeout,
            )

    async def on_username(self, data, match):
        self.set_state("username")
        await self.send(
            smart_bytes(
                self.script.credentials.get("user", "") or "", encoding=self.native_encoding
            )
            + (self.profile.username_submit or b"\n"),
            shadow=True,
        )
        self.expect(
            {
                "username": (self.on_failure, CLIAuthFailed),
                "password": self.on_password,
                "unprivileged_prompt": self.on_unprivileged_prompt,
                "prompt": self.on_prompt,
            },
            self.profile.cli_timeout_user,
            error=CLIUsernameTimeout,
        )

    async def on_password(self, data, match):
        self.set_state("password")
        await self.send(
            smart_bytes(
                self.script.credentials.get("password", "") or "", encoding=self.native_encoding
            )
            + (self.profile.password_submit or b"\n"),
            shadow=True,
        )
        self.expect(
            {
                "username": (self.on_failure, CLIAuthFailed),
                "password": (self.on_failure, CLIAuthFailed),
                "unprivileged_prompt": self.on_unprivileged_prompt,
                "super_password": self.on_super_password,
                "prompt": self.on_prompt,
                "pager": self.send_pager_reply,
            },
            self.profile.cli_timeout_password,
            error=CLIPasswordTimeout,
        )

    async def on_unprivileged_prompt(self, data, match):
        self.set_state("unprivileged_prompt")
        if self.to_raise_privileges:
            # Start privilege raising sequence
            if not self.profile.command_super:
                await self.on_failure(data, match, CLINoSuperCommand)
            await self.send(
                smart_bytes(self.profile.command_super, encoding=self.native_encoding)
                + (self.profile.command_submit or b"\n")
            )
            # Do not remove `pager` section
            # It fixes this situation on Huawei MA5300:
            # xxx>enable
            # { <cr>|level-value<U><1,15> }:
            # xxx#
            if self.cli_retries_unprivileged_mode > 1:
                self.cli_retries_unprivileged_mode -= 1
                self.expect(
                    {
                        "username": self.on_super_username,
                        "password": self.on_super_password,
                        "prompt": self.on_prompt,
                        "pager": self.send_pager_reply,
                    },
                    self.profile.cli_timeout_super,
                    error=CLISuperTimeout,
                )
            else:
                self.expect(
                    {
                        "username": self.on_super_username,
                        "password": self.on_super_password,
                        "prompt": self.on_prompt,
                        "pager": self.send_pager_reply,
                        "unprivileged_prompt": (self.on_failure, CLILowPrivileges),
                    },
                    self.profile.cli_timeout_super,
                    error=CLISuperTimeout,
                )
        else:
            # Do not raise privileges
            # Use unprivileged prompt as primary prompt
            self.patterns["prompt"] = self.patterns["unprivileged_prompt"]
            return await self.on_prompt(data, match)

    async def on_failure(self, data, match, error_cls=None):
        self.set_state("failure")
        error_cls = error_cls or CLIError
        raise error_cls(self.buffer or data or None)

    async def on_prompt(self, data, match):
        self.set_state("prompt")
        if not self.allow_empty_response:
            s_data = data.strip()
            # Endswith for example 'command: ' output
            if not s_data or s_data.endswith(self.command.strip()):
                return None
        if not self.is_started:
            self.resolve_pattern_prompt(match)
        d = b"".join(self.collected_data + [data])
        self.collected_data = []
        self.expect(
            {"pager": self.send_pager_reply, "prompt": self.on_prompt},
            self.profile.cli_timeout_prompt,
        )
        return d

    async def on_super_username(self, data, match):
        self.set_state("super_username")
        await self.send(
            smart_bytes(
                self.script.credentials.get("user", "") or "", encoding=self.native_encoding
            )
            + (self.profile.username_submit or b"\n")
        )
        self.expect(
            {
                "username": (self.on_failure, CLILowPrivileges),
                "password": self.on_super_password,
                "unprivileged_prompt": self.on_unprivileged_prompt,
                "prompt": self.on_prompt,
                "pager": self.send_pager_reply,
            },
            self.profile.cli_timeout_user,
            error=CLISuperUsernameTimeout,
        )

    async def on_super_password(self, data, match):
        self.set_state("super_password")
        await self.send(
            smart_bytes(
                self.script.credentials.get("super_password", "") or "",
                encoding=self.native_encoding,
            )
            + (self.profile.password_submit or b"\n"),
            shadow=True,
        )
        if self.super_password_retries > 1:
            unprivileged_handler = self.on_unprivileged_prompt
            self.super_password_retries -= 1
        else:
            unprivileged_handler = (self.on_failure, CLILowPrivileges)
        self.expect(
            {
                "prompt": self.on_prompt,
                "password": (self.on_failure, CLILowPrivileges),
                "super_password": (self.on_failure, CLILowPrivileges),
                "pager": self.send_pager_reply,
                "unprivileged_prompt": unprivileged_handler,
            },
            self.profile.cli_timeout_password,
            error=CLISuperPasswordTimeout,
        )

    async def on_setup_sequence(self, data, match):
        self.set_state("setup")
        self.logger.debug("Performing setup sequence: %s", self.profile.setup_sequence)
        lseq = len(self.profile.setup_sequence)
        for i, c in enumerate(self.profile.setup_sequence):
            if isinstance(c, (float, int)):
                await asyncio.sleep(c)
                continue
            cmd = c % self.script.credentials
            await self.send(cmd)
            # Waiting for response and drop it
            if i < lseq - 1:
                with self.stream.timeout(30.0):
                    resp = self.stream.read(4096)
                if self.script.to_track:
                    self.script.push_cli_tracking(resp, self.state)
                self.logger.debug("Receiving: %r", resp)
        self.logger.debug("Setup sequence complete")
        self.setup_complete = True
        await self.on_start(data, match)

    def resolve_pattern_prompt(self, match):
        """
        Resolve adaptive pattern prompt
        """
        old_pattern_prompt = self.patterns["prompt"].pattern
        pattern_prompt = old_pattern_prompt
        sl = self.profile.can_strip_hostname_to
        for k, v in match.groupdict().items():
            if v:
                k = smart_bytes(k)
                if k == b"hostname" and sl and len(v) > sl:
                    ss = [bytes([x]) for x in reversed(v[sl:])]
                    v = re.escape(v[:sl]) + reduce(
                        lambda x, y: b"(?:%s%s)?" % (re.escape(y), x),
                        ss[1:],
                        b"(?:%s)?" % re.escape(ss[0]),
                    )
                else:
                    v = re.escape(v)
                pattern_prompt = replace_re_group(pattern_prompt, b"(?P<%s>" % k, v)
                pattern_prompt = replace_re_group(pattern_prompt, b"(?P=%s" % k, v)
            else:
                self.logger.error("Invalid prompt pattern")
        if old_pattern_prompt != pattern_prompt:
            self.logger.debug("Refining pattern prompt to %r", pattern_prompt)
        self.patterns["prompt"] = re.compile(pattern_prompt, re.DOTALL | re.MULTILINE)

    def push_prompt_pattern(self, pattern):
        """
        Override prompt pattern
        """
        self.logger.debug("New prompt pattern: %s", pattern)
        self.prompt_stack += [self.patterns["prompt"]]
        self.patterns["prompt"] = re.compile(pattern, re.DOTALL | re.MULTILINE)
        self.pattern_table[self.patterns["prompt"]] = self.on_prompt

    def pop_prompt_pattern(self):
        """
        Restore prompt pattern
        """
        self.logger.debug("Restore prompt pattern")
        pattern = self.prompt_stack.pop(-1)
        self.patterns["prompt"] = pattern
        self.pattern_table[self.patterns["prompt"]] = self.on_prompt

    def prepare(self) -> None:
        """
        Perform preparation and initialization.

        May be called recursive during session setup
        """
        if self._to_setup_session:
            # Allow only first time
            self.logger.debug("Setup session")
            self._to_setup_session = False
            self._in_setup = True
            self.profile.setup_session(self.script)
            self._to_setup = False
        # Do not disable pager during setup phase
        if self._to_disable_pager and not self._in_setup:
            self._to_disable_pager = False
            self.logger.debug("Disable paging")
            if isinstance(self.profile.command_disable_pager, str):
                self.script.cli(self.profile.command_disable_pager, ignore_errors=True)
            elif isinstance(self.profile.command_disable_pager, list):
                for cmd in self.profile.command_disable_pager:
                    self.script.cli(cmd, ignore_errors=True)
            else:
                msg = "Invalid command_disable_pager"
                raise UnexpectedResultError(msg)

    def shutdown_session(self):
        if self.profile.shutdown_session:
            self.logger.debug("Shutdown session")
            self.profile.shutdown_session(self.script)

    async def on_error_sequence(self, seq, command, error_text):
        """
        Process error sequence
        :param seq:
        :param command:
        :param error_text:
        :return:
        """
        if isinstance(seq, str):
            self.logger.debug("Recovering sequece must byte type")
        elif isinstance(seq, bytes):
            self.logger.debug("Recovering from error. Sending %r", seq)
            await self.stream.write(seq)
        elif callable(seq):
            if asyncio.iscoroutinefunction(seq):
                # Await coroutine
                await seq(self, command, error_text)
            else:
                seq = seq(self, command, error_text)
                await self.stream.write(seq)
