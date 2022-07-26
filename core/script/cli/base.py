# ----------------------------------------------------------------------
# Closeable interface
# ----------------------------------------------------------------------
# Copyright (C) 2007-2020 The NOC Project
# See LICENSE for details
# ----------------------------------------------------------------------

# Python modules
from typing import Optional, Type
from asyncio.exceptions import TimeoutError

# NOC module
from noc.core.log import PrefixLoggerAdapter
from noc.core.perf import metrics
from noc.core.ioloop.util import IOLoopContext
from noc.core.comp import smart_bytes
from .error import CLIConnectionReset


class BaseCLI(object):
    name = "base"

    def __init__(self, script, tos: Optional[int] = None):
        self.script = script
        self.profile = script.profile
        self.logger = PrefixLoggerAdapter(self.script.logger, self.name)
        self.stream: Optional[BaseStream] = None
        self.tos = tos
        self.is_started = False
        # Current error to raise on TimeoutError
        self.timeout_exception_cls = CLIConnectionReset

    def close(self):
        self.script.close_current_session()
        self.close_stream()

    def close_stream(self):
        if self.stream:
            self.logger.debug("Closing stream")
            if self.is_started and self.profile.command_exit:
                with IOLoopContext(suppress_trace=True) as loop:
                    loop.run_until_complete(self.send(smart_bytes(self.profile.command_exit)))
            self.stream.close()
            self.stream = None

    def is_closed(self):
        return not self.stream

    def set_script(self, script):
        self.script = script
        self.logger = PrefixLoggerAdapter(self.script.logger, self.name)

    def shutdown_session(self):
        raise NotImplementedError

    def set_timeout(
        self, timeout: Optional[float] = None, error: Optional[Type[Exception]] = None
    ) -> None:
        if timeout:
            error = error or CLIConnectionReset
            self.logger.debug("Setting timeout: %ss, error=%s", timeout, error.__name__)
            self.timeout_exception_cls = error
            self.stream.set_timeout(timeout)
        else:
            self.logger.debug("Resetting timeouts")
            self.timeout_exception_cls = CLIConnectionReset
            self.stream.set_timeout(None)

    def get_stream(self) -> "BaseStream":
        """
        Stream factory. Must be overriden in subclasses.
        :return:
        """
        raise NotImplementedError

    async def start_stream(self):
        self.stream = self.get_stream()
        address = self.script.credentials.get("address")
        self.logger.debug("Connecting %s", address)
        try:
            metrics["cli_connection", ("proto", self.name)] += 1
            await self.stream.connect(address, self.script.credentials.get("cli_port"))
            metrics["cli_connection_success", ("proto", self.name)] += 1
        except ConnectionRefusedError:
            self.logger.debug("Connection refused")
            metrics["cli_connection_refused", ("proto", self.name)] += 1
            raise ConnectionRefusedError
        except TimeoutError:
            self.logger.debug("Connection timeout")
            metrics["cli_connection_timeout", ("proto", self.name)] += 1
            raise ConnectionRefusedError("Connection timeout")
        self.logger.debug("Connected")
        await self.stream.startup()

    async def send(self, cmd: bytes) -> None:
        raise NotImplementedError


# Avoid circular references
from .stream import BaseStream
