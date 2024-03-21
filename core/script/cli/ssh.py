# ----------------------------------------------------------------------
# SSH CLI
# ----------------------------------------------------------------------
# Copyright (C) 2007-2024 The NOC Project
# See LICENSE for details
# ----------------------------------------------------------------------

# Python modules
import asyncio
from asyncio import coroutines
import os
import re
import threading
import operator
import logging
import codecs
from typing import AnyStr, Iterable, Tuple, Optional, Union, List, cast

# Third-party modules modules
import cachetools

import asyncssh as asyncssh
from asyncssh.misc import PermissionDenied
from asyncssh.misc import ConnectionLost

# NOC modules
from noc.config import config
from noc.core.perf import metrics
from noc.core.comp import smart_bytes, smart_text
from .cli import CLI
from .base import BaseStream
from .error import CLIAuthFailed, CLISSHProtocolError

key_lock = threading.Lock()
logger = logging.getLogger(__name__)


class NOCSSHThread(threading.Thread):
    def __init__(self, socket, owner, username, password, pub_key, priv_key) -> None:
        super().__init__()
        self.socket = socket
        self._owner = owner

        self.logger = self._owner.logger

        self.username = username
        self.password = password
        self.pub_key = pub_key
        self.priv_key = priv_key

        self.auth_success = False
        self.connection = None
        self.writer = None
        self.stdout_reader = None
        self.stderr_reader = None

        self.loop = asyncio.new_event_loop()

    def is_running(self) -> bool:
        return self.loop.is_running()

    def is_auth_success(self) -> bool:
        return self.auth_success

    async def _read(self, n: int):
        data = b""
        self.logger.debug("Receiving ||")
        try:
            data = await self.stdout_reader.read(n)
        except ConnectionLost as e:
            self.logger.info("Connection is lost while reading (%s)", e)
        except Exception as e:
            self.logger.info("Some connection trouble while reading (%s)", e)

        self.logger.debug("Received |%s|", data)
        return data

    async def _write(self, data: bytes) -> None:
        try:
            self.writer.write(data)
            await self.writer.drain()
        except Exception as e:
            self.logger.info("Some connection trouble while writing (%s)", e)

    async def _connect(self) -> None:
        def NOCSSHClient_factory() -> NOCSSHClient:
            return NOCSSHClient(self)

        try:
            self.connection = await asyncssh.run_client(
                self.socket,
                client_factory=NOCSSHClient_factory,
                known_hosts=None,
                username=self.username,
                term_type="xterm",
                kex_algs="+diffie-hellman-group1-sha1",
                encryption_algs="+3des-cbc",
                keepalive_interval=60,
                keepalive_count_max=5,
            )

            if self.connection:
                self.auth_success = True

            host_key = self.connection.get_server_host_key()
            host_hash = smart_bytes(host_key.get_fingerprint(hash_name="sha1"))
            hex_hash = smart_text(codecs.encode(host_hash, "hex"))
            self.logger.debug("Connected. Host fingerprint is %s", hex_hash)

            res = await self.connection.open_session(encoding=None)
            self.writer = res[0]
            self.stdout_reader = res[1]
            self.stderr_reader = res[2]
        except PermissionDenied as e:
            self.logger.info("Auth failed for user %s", self.username)
        except Exception as e:
            self.logger.info("Something happens while connection creating %s", e)

    def connect(self) -> None:
        return asyncio.run_coroutine_threadsafe(self._connect(), self.loop).result()

    def read(self, n: int):
        return asyncio.run_coroutine_threadsafe(self._read(n), self.loop).result()

    def write(self, data: bytes) -> None:
        return asyncio.run_coroutine_threadsafe(self._write(data), self.loop).result()

    def run(self) -> None:
        self.logger.debug("Starting ssh async thread")
        asyncio.set_event_loop(self.loop)
        self.loop.run_forever()
        self.logger.debug("Stopped ssh async thread")

    def stop(self) -> None:
        self.logger.debug("Closing ssh async connection")
        if self.connection:
            self.connection.close()
        else:
            self.logger.info("Connection not exists")
        self.logger.debug("Stopping ssh async event loop")
        self.loop.call_soon_threadsafe(self.loop.stop)
        self.logger.debug("Wait for thread is closed")
        self.join()


class NOCSSHClient(asyncssh.SSHClient):
    def __init__(self, owner: NOCSSHThread) -> None:
        self._owner = owner
        self.logger = self._owner.logger

        self.username = self._owner.username
        self.password = self._owner.password
        self.pub_key = self._owner.pub_key
        self.priv_key = self._owner.priv_key

        self.key_sended = False

    def public_key_auth_requested(self) -> Optional[Tuple[bytes, bytes]]:
        self.logger.debug("Requested key auth")

        if not self.priv_key:
            self.logger.debug("No private key for pool. Skip key auth")
            return None

        if self.key_sended:
            return None

        self.key_sended = True
        return self.priv_key

    def password_auth_requested(self) -> Optional[str]:
        self.logger.debug("Requested password auth")
        return self.password

    def auth_completed(self) -> None:
        self.logger.debug("Auth successfull")

    def connection_made(self, conn) -> None:
        self.logger.debug("Connection successfull")

    def connection_lost(self, exc) -> None:
        if exc:
            self.logger.info("Connection is lost with exception %s", exc)
        else:
            self.logger.info("Connection is lost without exception")


class SSHStream(BaseStream):
    default_port = 22
    SSH_KEY_PREFIX = config.path.ssh_key_prefix

    _key_cache = cachetools.TTLCache(100, ttl=60)

    def __init__(self, cli: CLI):
        super().__init__(cli)
        self.script = cli.script  # @todo: Remove
        self.session = None
        self.channel = None
        self.credentials = cli.script.credentials

    def __del__(self):
        self.channel = None
        self.session = None

    @classmethod
    @cachetools.cachedmethod(operator.attrgetter("_key_cache"), lock=lambda _: key_lock)
    def get_publickey(cls, pool: str) -> Tuple[Optional[bytes], Optional[bytes]]:
        """
        Return public, private key pair
        :return: bytes, bytes or None, None
        """
        logger.debug("Getting keys for pool %s", pool)
        pub_path = os.path.join(config.path.ssh_key_prefix, pool, "id_rsa.pub")
        priv_path = os.path.join(config.path.ssh_key_prefix, pool, "id_rsa")
        if not os.path.exists(pub_path):
            logger.debug("No public key for pool %s (%s)", pool, pub_path)
            return None, None
        if not os.path.exists(priv_path):
            logger.debug("No private key for pool %s (%s)", pool, priv_path)
            return None, None
        with open(pub_path, "rb") as fpub, open(priv_path, "rb") as fpriv:
            return fpub.read(), fpriv.read()

    async def startup(self) -> None:
        """
        SSH session startup
        """

        user = self.credentials["user"]
        if user is None:
            user = ""

        password = self.get_password()
        pub_key, priv_key = self.get_publickey(self.script.pool)

        self.logger.debug("Startup asyncssh session for user '%s'", user)

        self.loop = asyncio.new_event_loop()
        self.thread = NOCSSHThread(
            socket=self.socket,
            owner=self,
            username=user,
            password=password,
            pub_key=pub_key,
            priv_key=priv_key,
        )

        self.thread.start()
        while not self.thread.is_running():
            await asyncio.sleep(0.1)

        self.thread.connect()

        if not self.thread.is_auth_success():
            raise CLIAuthFailed("Failed to log in")

    async def read(self, n: int) -> bytes:
        data = self.thread.read(n)
        n = len(data)
        metrics["ssh_read_bytes"] += n
        return data

    async def write(self, data: bytes) -> None:
        self.thread.write(data)
        metrics["ssh_write_bytes"] += len(data)

    def close(self, exc_info=False) -> None:
        if self.thread:
            self.logger.debug("Stopping ssh async thread")
            self.thread.stop()
        super().close()

    def get_user(self) -> str:
        """
        Get current user
        """
        return self.script.credentials["user"] or ""

    def get_password(self) -> str:
        """
        Get current user's password
        """
        return self.script.credentials["password"] or ""


class SSHCLI(CLI):
    name = "ssh"

    def get_stream(self) -> BaseStream:
        return SSHStream(self)
