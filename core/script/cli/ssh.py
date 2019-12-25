# -*- coding: utf-8 -*-
# ----------------------------------------------------------------------
# SSH CLI
# ----------------------------------------------------------------------
# Copyright (C) 2007-2019 The NOC Project
# See LICENSE for details
# ----------------------------------------------------------------------

# Python modules
from __future__ import absolute_import
import os
import threading
import operator
import logging
import codecs

# Third-party modules modules
import cachetools
from tornado.iostream import IOStream
import tornado.gen
from ssh2.session import Session, LIBSSH2_HOSTKEY_HASH_SHA1
from ssh2.exceptions import SSH2Error
from ssh2.error_codes import LIBSSH2_ERROR_EAGAIN

# NOC modules
from noc.config import config
from noc.core.perf import metrics
from noc.core.comp import smart_bytes, smart_text
from .base import CLI
from .error import CLIAuthFailed, CLISSHProtocolError

key_lock = threading.Lock()
logger = logging.getLogger(__name__)


class SSHIOStream(IOStream):
    SSH_KEY_PREFIX = config.path.ssh_key_prefix

    _key_cache = cachetools.TTLCache(100, ttl=60)

    def __init__(self, sock, cli, *args, **kwargs):
        super(SSHIOStream, self).__init__(sock, *args, **kwargs)
        self.cli = cli
        self.script = self.cli.script
        self.logger = cli.logger
        self.session = None
        self.channel = None

    def __del__(self):
        self.channel = None
        self.session = None

    @classmethod
    @cachetools.cachedmethod(operator.attrgetter("_key_cache"), lock=lambda _: key_lock)
    def get_publickey(cls, pool):
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
        with open(pub_path) as fpub, open(priv_path) as fpriv:
            return fpub.read(), fpriv.read()

    @tornado.gen.coroutine
    def startup(self):
        """
        SSH session startup
        """
        user = self.script.credentials["user"]
        if user is None:
            user = ""
        self.logger.debug("Startup ssh session for user '%s'", user)
        self.session = Session()
        try:
            self.session.handshake(self.socket)
            host_hash = smart_bytes(self.session.hostkey_hash(LIBSSH2_HOSTKEY_HASH_SHA1))
            hex_hash = smart_text(codecs.encode(host_hash, "hex"))
            self.logger.debug("Connected. Host fingerprint is %s", hex_hash)
            auth_methods = self.session.userauth_list(user)
            if not auth_methods:
                self.logger.info("No supported authentication methods. Failed to log in")
                raise CLIAuthFailed("Failed to log in")
            self.logger.debug("Supported authentication methods: %s", ", ".join(auth_methods))
            # Try to authenticate
            authenticated = False
            for method in auth_methods:
                ah = getattr(self, "auth_%s" % method.replace("-", ""), None)
                if ah:
                    metrics["ssh_auth", ("method", method)] += 1
                    authenticated |= ah()
                    if authenticated:
                        metrics["ssh_auth_success", ("method", method)] += 1
                        break
                    metrics["ssh_auth_fail", ("method", method)] += 1
            if not authenticated:
                self.logger.error("Failed to authenticate user '%s'", user)
                raise CLIAuthFailed("Failed to log in")
            self.logger.debug("User is authenticated")
            self.logger.debug("Open channel")
            self.channel = self.session.open_session()
            self.channel.pty("xterm")
            self.channel.shell()
            self.session.keepalive_config(False, 60)
            self.session.set_blocking(False)
        except SSH2Error as e:
            self.logger.info("SSH Error: %s", e)
            raise CLISSHProtocolError("SSH Error: %s" % e)

    def read_from_fd(self):
        try:
            metrics["ssh_reads"] += 1
            code, data = self.channel.read(self.read_chunk_size)
            if code == 0:
                if self.channel.eof():
                    self.logger.info("SSH session reset")
                    self.close()
                metrics["ssh_reads_blocked"] += 1
                return None
            elif code > 0:
                metrics["ssh_read_bytes"] += len(data)
                return data
            elif code == LIBSSH2_ERROR_EAGAIN:
                metrics["ssh_reads_blocked"] += 1
                return None  # Blocking call
            metrics["ssh_errors", ("code", code)] += 1
            raise CLISSHProtocolError("SSH Error code %s" % code)
        except SSH2Error as e:
            raise CLISSHProtocolError("SSH Error: %s" % e)

    def write_to_fd(self, data):
        # ssh2 doesn't accept memoryview
        metrics["ssh_writes"] += 1
        if isinstance(data, memoryview):
            data = data.tobytes()
        try:
            _, written = self.channel.write(data)
            metrics["ssh_write_bytes"] += written
            return written
        except SSH2Error as e:
            raise CLISSHProtocolError("SSH Error: %s" % e)

    def close(self, exc_info=False):
        if not self.closed():
            if self.channel:
                self.logger.debug("Closing channel")
                try:
                    self.channel.close()
                except SSH2Error as e:
                    self.logger.debug("Cannot close channel clearly: %s", e)
                self.channel = None
            if self.session:
                self.logger.debug("Closing ssh session")
                self.session = None
        super(SSHIOStream, self).close(exc_info=exc_info)

    def get_user(self):
        # type: () -> str
        """
        Get current user
        """
        return self.script.credentials["user"] or ""

    def get_password(self):
        # type: () -> str
        """
        Get current user's password
        """
        return self.script.credentials["password"] or ""

    def auth_publickey(self):
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
    default_port = 22
    iostream_class = SSHIOStream
