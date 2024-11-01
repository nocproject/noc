# ----------------------------------------------------------------------
# SSH CLI
# ----------------------------------------------------------------------
# Copyright (C) 2007-2021 The NOC Project
# See LICENSE for details
# ----------------------------------------------------------------------

# Python modules
import os
import threading
import operator
import logging
import codecs
from typing import Tuple, Optional, List

# Third-party modules modules
import cachetools
from ssh2.session import Session, LIBSSH2_HOSTKEY_HASH_SHA1
from ssh2.exceptions import SSH2Error
from ssh2.error_codes import LIBSSH2_ERROR_EAGAIN

# NOC modules
from noc.config import config
from noc.core.perf import metrics
from noc.core.comp import smart_bytes, smart_text
from .cli import CLI
from .base import BaseStream
from .error import CLIAuthFailed, CLISSHProtocolError

key_lock = threading.Lock()
logger = logging.getLogger(__name__)


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

    async def startup(self):
        """
        SSH session startup
        """
        user = self.credentials["user"]
        if user is None:
            user = ""
        self.logger.debug("Startup ssh session for user '%s'", user)
        self.session = Session()
        try:
            self.session.handshake(self.socket)
            host_hash = smart_bytes(self.session.hostkey_hash(LIBSSH2_HOSTKEY_HASH_SHA1))
            hex_hash = smart_text(codecs.encode(host_hash, "hex"))
            self.logger.debug("Connected. Host fingerprint is %s", hex_hash)
            # libssh2's userauth_list implementation tries to authenticate
            # using `none` method internally. So calling `userauth_list`
            # can bring session into authenticated state.
            auth_methods = self.session.userauth_list(user)
            if self.session.userauth_authenticated():
                self.logger.info("Authenticated using 'none' method")
                metrics["ssh_auth_success", ("method", "none")] += 1
            elif auth_methods:
                if not self.authenticate(user, auth_methods):
                    raise CLIAuthFailed("Failed to log in")
            else:
                self.logger.info("No supported authentication methods. Failed to log in")
                raise CLIAuthFailed("No supported authentication methods. Failed to log in")
            self.logger.debug("User is authenticated")
            self.logger.debug("Open channel")
            self.channel = self.session.open_session()
            if isinstance(self.channel, int):
                # Return error code, see handle_error_codes on utils
                raise SSH2Error(f"SSH Error code: {self.channel}")
            self.channel.pty("xterm")
            self.channel.shell()
            self.session.keepalive_config(False, 60)
            self.session.set_blocking(False)
        except SSH2Error as e:
            self.logger.info("SSH Error: %s", e)
            raise CLISSHProtocolError("SSH Error: %s" % e)

    async def read(self, n: int) -> bytes:
        while True:
            try:
                code, data = self.channel.read(n)
                if code == LIBSSH2_ERROR_EAGAIN:
                    await self.wait_for_read()
                    metrics["ssh_reads_blocked"] += 1
                    continue
                metrics["ssh_reads"] += 1
                if code == 0:
                    if self.channel.eof():
                        self.logger.info("SSH session reset")
                        self.close()
                        return b""
                    metrics["ssh_reads_blocked"] += 1
                    continue
                elif code > 0:
                    n = len(data)
                    metrics["ssh_read_bytes"] += n
                    return data

                metrics["ssh_errors", ("code", code)] += 1
                raise CLISSHProtocolError("SSH Error code %s" % code)
            except SSH2Error as e:
                raise CLISSHProtocolError("SSH Error: %s" % e)

    async def write(self, data: bytes):
        metrics["ssh_writes"] += 1
        while data:
            await self.wait_for_write()
            try:
                _, sent = self.channel.write(data)
                metrics["ssh_write_bytes"] += sent
                data = data[sent:]
            except SSH2Error as e:
                raise CLISSHProtocolError("SSH Error: %s" % e)

    def close(self, exc_info=False):
        if self.channel:
            self.logger.debug("Closing channel")
            try:
                self.channel.close()
            except SSH2Error as e:
                self.logger.debug("Cannot close channel clearly: %s", e)
            # The causes of memory leak
            # self.channel = None
        if self.session:
            self.logger.debug("Closing ssh session")
            self.session = None
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

    def authenticate(self, user: str, methods: List[str]) -> bool:
        """
        Try to authenticate. Return True on success
        :param user: Username
        :param methods: List of available authentication methods
        :return:
        """
        self.logger.debug("Supported authentication methods: %s", ", ".join(methods))
        for method in methods:
            auth_handler = getattr(self, "auth_%s" % method.replace("-", ""), None)
            if not auth_handler:
                self.logger.debug("'%s' method is not supported, skipping", method)
                continue
            metrics["ssh_auth", ("method", method)] += 1
            if auth_handler():
                metrics["ssh_auth_success", ("method", method)] += 1
                return True
            metrics["ssh_auth_fail", ("method", method)] += 1
        self.logger.error("Failed to authenticate user '%s'", user)
        return False

    def auth_publickey(self) -> bool:
        """
        Public key authentication
        """
        self.logger.debug("Trying publickey authentication")
        pub_key, priv_key = self.get_publickey(self.script.pool)
        if not pub_key or not priv_key:
            self.logger.debug("No keys for pool. Skipping")
            return False
        user = self.get_user()
        try:
            self.session.userauth_publickey_frommemory(user, priv_key, "", pub_key)
            return True
        except SSH2Error:
            msg = self.session.last_error()
            self.logger.debug("Failed: %s", msg)
            return False

    def auth_keyboardinteractive(self):
        """
        Keyboard-interactive authentication. Send username and password
        """
        self.logger.debug("Trying keyboard-interactive")
        if not hasattr(self.session, "userauth_keyboardinteractive"):
            self.logger.debug("keyboard-interactive is not supported by ssh library. Skipping")
            return False
        try:
            self.session.userauth_keyboardinteractive(self.get_user(), self.get_password())
            self.logger.debug("Success")
            return True
        except SSH2Error:
            msg = self.session.last_error()
            self.logger.debug("Failed: %s", msg)
            return False

    def auth_password(self):
        """
        Password authentication. Send username and password
        """
        self.logger.debug("Trying password authentication")
        try:
            self.session.userauth_password(self.get_user(), self.get_password())
            self.logger.debug("Success")
            return True
        except SSH2Error:
            msg = self.session.last_error()
            self.logger.debug("Failed: %s", msg)
            return False


class SSHCLI(CLI):
    name = "ssh"

    def get_stream(self) -> BaseStream:
        return SSHStream(self)
