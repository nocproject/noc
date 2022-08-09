# Create and run <CLIENTS_QUANTITY> clients

# Python modules
import asyncio
import random
import socket

# NOC modules
from config import (
    CLIENTS_QUANTITY,
    DATAGRAMS_FOR_CLIENT,
    SERVER_ADDRESS,
    SERVER_PORT,
)


def random_string():
    s_len = random.randint(1, 500)
    s = ""
    for _ in range(s_len):
        s += chr(random.randint(0, 255))
    return s


class UDPClient:
    async def work(self, client_id, datagrams_quantity):
        self.client_id = client_id
        self.datagrams_quantity = datagrams_quantity
        self.sock = socket.socket(family=socket.AF_INET, type=socket.SOCK_DGRAM)
        self.sock.setblocking(False)
        await self.send_datagrams()
        self.sock.close()

    async def send_datagrams(self):
        for datagram_id in range(self.datagrams_quantity):
            data = random_string().encode()
            self.sock.sendto(data, (SERVER_ADDRESS, SERVER_PORT))
            pause = random.uniform(0.001, 0.01)
            await asyncio.sleep(pause)


# create and run clients
async def clients_routine():
    all_tasks = []
    for client_id in range(CLIENTS_QUANTITY):
        udpclient = UDPClient()
        all_tasks.append(udpclient.work(client_id, DATAGRAMS_FOR_CLIENT))
    await asyncio.gather(*all_tasks)


asyncio.run(clients_routine())
