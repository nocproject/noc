# ----------------------------------------------------------------------
# MML class
# ----------------------------------------------------------------------
# Copyright (C) 2007-2020 The NOC Project
# See LICENSE for details
# ----------------------------------------------------------------------

# Python modules
import re
import asyncio

# NOC modules
from noc.config import config
from noc.core.span import Span
from noc.core.comp import smart_bytes
from noc.core.perf import metrics
from noc.core.ioloop.util import IOLoopContext
from .error import MMLConnectionRefused, MMLAuthFailed, MMLBadResponse, MMLError
from ..cli.base import BaseCLI


class MMLBase(BaseCLI):
    name = "mml"
    BUFFER_SIZE = config.activator.buffer_size
    MATCH_TAIL = 256
    SYNTAX_ERROR_CODE = b"+@@@NOC:SYNTAXERROR@@@+"

    def __init__(self, script, tos=None):
        super().__init__(script, tos)
        self.command = None
        self.buffer = ""
        self.is_started = False
        self.result = None
        self.error = None
        self.rx_mml_end = re.compile(self.script.profile.pattern_mml_end, re.MULTILINE)
        if self.script.profile.pattern_mml_continue:
            self.rx_mml_continue = re.compile(
                self.script.profile.pattern_mml_continue, re.MULTILINE
            )
        else:
            self.rx_mml_continue = None

    async def send(self, cmd):
        # @todo: Apply encoding
        cmd = smart_bytes(cmd)
        self.logger.debug("Send: %r", cmd)
        await self.stream.write(cmd)

    async def submit(self):
        if not self.stream:
            try:
                await self.start_stream()
            except ConnectionRefusedError:
                self.error = MMLConnectionRefused("Connection refused")
                return None
        # Perform all necessary login procedures
        if not self.is_started:
            self.is_started = True
            await self.send(self.profile.get_mml_login(self.script))
            await self.get_mml_response()
            if self.error:
                self.error = MMLAuthFailed(str(self.error))
                return None
        # Send command
        await self.send(self.command)
        return await self.get_mml_response()

    async def get_mml_response(self):
        result = []
        header_sep = self.profile.mml_header_separator
        while True:
            r = await self.read_until_end()
            r = r.strip()
            # Process header
            if header_sep not in r:
                self.result = ""
                self.error = MMLBadResponse("Missed header separator")
                return None
            header, r = r.split(header_sep, 1)
            code, msg = self.profile.parse_mml_header(header)
            if code:
                # MML Error
                self.result = ""
                self.error = MMLError("%s (code=%s)" % (msg, code))
                return None
            # Process continuation
            if self.rx_mml_continue:
                # Process continued block
                offset = max(0, len(r) - self.MATCH_TAIL)
                match = self.rx_mml_continue.search(r, offset)
                if match:
                    self.logger.debug("Continuing in the next block")
                    result += [r[: match.start()]]
                    continue
            result += [r]
            break
        self.result = "".join(result)
        return self.result

    def execute(self, cmd, **kwargs):
        """
        Perform command and return result
        :param cmd:
        :param kwargs:
        :return:
        """
        self.buffer = b""
        self.command = self.profile.get_mml_command(cmd, **kwargs)
        self.error = None
        with Span(
            server=self.script.credentials.get("address"), service=self.name, in_label=self.command
        ) as s:
            with IOLoopContext() as loop:
                loop.run_until_complete(self.submit())
            if self.error:
                if s:
                    s.error_text = str(self.error)
                raise self.error
            return self.result

    async def read_until_end(self):
        while True:
            try:
                metrics["mml_reads", ("proto", self.name)] += 1
                r = await self.stream.read(self.BUFFER_SIZE)
                if r == self.SYNTAX_ERROR_CODE:
                    metrics["mml_syntax_errors", ("proto", self.name)] += 1
                    return self.SYNTAX_ERROR_CODE
                metrics["mml_read_bytes", ("proto", self.name)] += len(r)
                if self.script.to_track:
                    self.script.push_cli_tracking(r, self.state)
            except asyncio.TimeoutError:
                self.logger.info("Timeout error")
                metrics["mml_timeouts", ("proto", self.name)] += 1
                # Stream must be closed to prevent hanging read callbacks
                self.close_stream()
                raise asyncio.TimeoutError("Timeout")  # @todo: Uncaught
            self.logger.debug("Received: %r", r)
            self.buffer += r
            offset = max(0, len(self.buffer) - self.MATCH_TAIL)
            match = self.rx_mml_end.search(self.buffer, offset)
            if match:
                self.logger.debug("End of the block")
                r = self.buffer[: match.start()]
                self.buffer = self.buffer[match.end()]
                return r

    def shutdown_session(self):
        if self.profile.shutdown_session:
            self.logger.debug("Shutdown session")
            self.profile.shutdown_session(self.script)
