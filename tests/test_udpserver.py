# ----------------------------------------------------------------------
# UDP Server test
# ----------------------------------------------------------------------
# Copyright (C) 2007-2022 The NOC Project
# See LICENSE for details
# ----------------------------------------------------------------------

# Python modules
import asyncio
import os
from subprocess import Popen
from typing import Tuple

# NOC modules
from .udpserver.config import (
    DATAGRAMS_ALL,
    LIMIT_PERCENT_OF_LOST,
    SERVER_ADDRESS,
    SERVER_PORT,
)
from noc.core.ioloop.udpserver_tornado import UDPServer


class UDPServerStub(UDPServer):
    def __init__(self):
        super().__init__()
        self.received = 0

    def on_read(self, data: bytes, address: Tuple[str, int]):
        self.received += 1


async def server_routine():
    udpserver = UDPServerStub()
    udpserver.listen(SERVER_PORT, SERVER_ADDRESS)
    udpserver.start()
    while True:
        received_old = udpserver.received
        await asyncio.sleep(0.5)
        if received_old == udpserver.received:
            print("Server timeout")
            udpserver.stop()
            break
    p_of_lost = (DATAGRAMS_ALL - udpserver.received) / DATAGRAMS_ALL * 100
    print("Datagrams sent:", DATAGRAMS_ALL, "Datagrams received:", udpserver.received)
    print("Percent of lost diagrams:", p_of_lost)
    assert p_of_lost <= LIMIT_PERCENT_OF_LOST


# Testing UDP-server by sending a lot of datagrams from multiple clients
def test_server_operation():
    # start clients
    devnull = open(os.devnull, "w")
    Popen(["python", "tests/udpserver/client.py"], stdout=devnull)
    # start server
    asyncio.run(server_routine())
