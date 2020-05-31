# ----------------------------------------------------------------------
# BeefCLI
# ----------------------------------------------------------------------
# Copyright (C) 2007-2020 The NOC Project
# See LICENSE for details
# ----------------------------------------------------------------------

# Python modules
import asyncio
from typing import Optional

# NOC modules
from .cli import CLI
from .stream import BaseStream
from .telnet import TelnetStream


class BeefStream(TelnetStream):
    def __init__(self, cli: CLI):
        super().__init__(cli)
        self.cli = cli
        self.beef = None
        self.read_buffer = []
        self.read_event = asyncio.Event()

    def close(self):
        self.cli = None

    async def connect(self, address: str, port: Optional[int] = None):
        self.beef = self.cli.script.request_beef()
        if not self.beef:
            # Connection refused
            raise ConnectionRefusedError
        self.cli.set_state("start")

    async def read(self, n: int):
        while True:
            await self.read_event.wait()
            if self.read_buffer:
                data = self.read_buffer.pop(0)
                if not self.read_buffer:
                    self.read_event.clear()
                return data

    async def write(self, data: bytes, raw: bool = False):
        try:
            self.read_buffer += list(self.beef.iter_cli_reply(data))
        except KeyError:
            self.read_buffer += [self.cli.SYNTAX_ERROR_CODE]
        self.read_event.set()

    async def wait_for_read(self):
        pass

    async def wait_for_write(self):
        pass

    async def enter_state(self, state):
        self.read_buffer += list(self.beef.iter_fsm_state_reply(state))
        self.read_event.set()


class BeefCLI(CLI):
    name = "beef_cli"

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.state = "notconnected"

    def get_stream(self) -> BaseStream:
        return BeefStream(self)

    def set_state(self, state):
        changed = self.state != state
        super().set_state(state)
        # Force state enter reply
        if changed:
            asyncio.get_running_loop().create_task(self.stream.enter_state(state))

    async def reply_state(self, state):
        self.logger.debug("Replying '%s' state", state)
        beef = self.script.request_beef()
        for reply in beef.iter_fsm_state_reply(state):
            await self.stream.write(reply)

    async def send(self, cmd: bytes) -> None:
        self.logger.debug("Send: %r", cmd)
        if self.state != "prompt":
            return  # Will be replied via reply_state
        await self.stream.write(cmd[: -len(self.profile.command_submit)])

    def is_beef(self) -> bool:
        return True

    async def send_pager_reply(self, data, match):
        """
        Beef need no pagers
        """
        self.collected_data += [data]
