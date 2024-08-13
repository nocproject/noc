# ----------------------------------------------------------------------
# UDP Server test
# ----------------------------------------------------------------------
# Copyright (C) 2007-2024 The NOC Project
# See LICENSE for details
# ----------------------------------------------------------------------

# Python modules
import asyncio
from typing import Tuple
import random
import socket

# NOC modules
from noc.core.ioloop.udpserver import UDPServer

CLIENTS_QUANTITY = 200  # 200
DATAGRAMS_FOR_CLIENT = 250  # 250
DATAGRAMS_ALL = DATAGRAMS_FOR_CLIENT * CLIENTS_QUANTITY
LIMIT_PERCENT_OF_LOST = 0.5  # 0.5%

SERVER_ADDRESS = "127.0.0.1"


class UDPServerStub(UDPServer):
    def __init__(self):
        super().__init__()
        self.received = 0
        self.ready = asyncio.Event()

    def on_read(self, data: bytes, address: Tuple[str, int]):
        self.received += 1

    @property
    def sock_addr(self) -> Tuple[str, int]:
        return self._sockaddr[0]


async def server_routine(udpserver: UDPServerStub):
    await udpserver.listen(0, SERVER_ADDRESS)
    udpserver.start()
    udpserver.ready.set()
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


def random_string():
    s_len = random.randint(1, 500)
    s = ""
    for _ in range(s_len):
        s += chr(random.randint(0, 255))
    return s


async def client_routine(server: UDPServerStub, datagrams_quantity: int) -> None:
    # Wait for the server
    await server.ready.wait()
    # Create socket
    loop = asyncio.get_running_loop()
    transport, _ = await loop.create_datagram_endpoint(
        lambda: asyncio.DatagramProtocol(), remote_addr=server.sock_addr
    )
    # Send messages
    for _ in range(datagrams_quantity):
        data = random_string().encode()
        transport.sendto(data)
        pause = random.uniform(0.001, 0.01)
        await asyncio.sleep(pause)
    # Cleanup
    transport.close()


# Testing UDP-server by sending a lot of datagrams from multiple clients
def test_server_operation():
    async def inner():
        udpserver = UDPServerStub()
        tasks = [server_routine(udpserver)] + [
            client_routine(udpserver, DATAGRAMS_FOR_CLIENT) for _ in range(CLIENTS_QUANTITY)
        ]
        await asyncio.gather(*tasks)

    asyncio.run(inner())
