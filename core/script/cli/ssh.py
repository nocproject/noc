# -*- coding: utf-8 -*-
# ----------------------------------------------------------------------
# SSH CLI
# ----------------------------------------------------------------------
# Copyright (C) 2007-2015 The NOC Project
# See LICENSE for details
# ----------------------------------------------------------------------

# Python modules
from __future__ import absolute_import
import os
# Third-party modules modules
import six
from tornado.iostream import IOStream
import tornado.gen
import libssh2
import _libssh2
# NOC modules
from .base import CLI
from .error import CLIAuthFailed, CLISSHProtocolError


class SSHIOStream(IOStream):
    SSH_KEY_PREFIX = os.path.join("var", "etc", "ssh")

    def __init__(self, sock, cli, *args, **kwargs):
        super(SSHIOStream, self).__init__(sock, *args, **kwargs)
        self.cli = cli
        self.script = self.cli.script
        self.logger = cli.logger
        self.session = libssh2.Session()
        self.channel = None

    @tornado.gen.coroutine
    def startup(self):
        """
        SSH session startup
        """
        user = self.script.credentials["user"]
        if user is None:
            user = ""
        self.logger.debug("Startup ssh session for user '%s'", user)
        try:
            self.session.startup(self.socket)
            host_hash = self.session.hostkey_hash(2)  # SHA1
            self.logger.debug("Connected. Host fingerprint is %s",
                              host_hash.encode("hex"))
            auth_methods = self.session.userauth_list(user).split(",")
            self.logger.debug("Supported authentication methods: %s",
                              ", ".join(auth_methods))
            # Try to authenticate
            authenticated = False
            for method in auth_methods:
                ah = getattr(self, "auth_%s" % method.replace("-", ""), None)
                if ah:
                    authenticated |= ah()
                    if authenticated:
                        break
            if authenticated:
                self.logger.debug("User is authenticated")
            else:
                self.logger.error("Failed to authenticate user '%s'", user)
                raise CLIAuthFailed("Failed to log in")
            self.logger.debug("Open channel")
            self.channel = self.session.open_session()
            self.channel.pty("xterm")
            self.channel.shell()
            self.channel.setblocking(0)
        except _libssh2.Error as e:
            raise CLISSHProtocolError("SSH Error: %s" % e)

    def read_from_fd(self):
        try:
            r = self.channel.read(self.read_chunk_size)
            if r is None:
                if self.channel.eof():
                    self.logger.info("SSH session reset")
                    self.close()
                return None
            elif r == -37:  # LIBSSH2_ERROR_EAGAIN
                return None  # blocking call
            elif isinstance(r, six.string_types):
                return r
            else:
                raise CLISSHProtocolError("SSH Error code %s" % r)
        except _libssh2.Error as e:
            raise CLISSHProtocolError("SSH Error: %s" % e)

    def write_to_fd(self, data):
        # libssh2 doesn't accept memoryview
        if isinstance(data, memoryview):
            data = data.tobytes()
        try:
            return self.channel.write(data)
        except _libssh2.Error as e:
            raise CLISSHProtocolError("SSH Error: %s" % e)

    def close(self, exc_info=False):
        if not self.closed():
            if self.channel:
                self.channel.setblocking(1)
                self.logger.debug("Closing channel")
                try:
                    self.channel.close()
                except _libssh2.Error as e:
                    self.logger.debug("Cannot close channel clearly: %s", e)
                self.channel = None
            self.logger.debug("Closing ssh session")
            try:
                self.session.close()
            except _libssh2.Error as e:
                self.logger.debug("Cannot close session clearly: %s", e)
            self.session = None
        super(SSHIOStream, self).close(exc_info=exc_info)

    def auth_publickey(self):
        """
        Public key authentication
        """
        self.logger.debug("Trying publickey authentication")
        pub_path = os.path.join(
            self.SSH_KEY_PREFIX,
            self.script.pool,
            "id_rsa.pub"
        )
        priv_path = os.path.join(
            self.SSH_KEY_PREFIX,
            self.script.pool,
            "id_rsa"
        )
        self.logger.debug("public_key=%s private_key=%s",
                          pub_path, priv_path)
        user = self.script.credentials["user"]
        if user is None:
            user = ""
        try:
            self.session.userauth_publickey_fromfile(
                user,
                publickey=pub_path,
                privatekey=priv_path,
                passphrase=""
            )
            return True
        except _libssh2.Error:
            code, msg = self.session.last_error()
            self.logger.debug("Failed: %s (Code: %s)", msg, code)
            return False

    def auth_keyboardinteractive(self):
        """
        Keyboard-interactive authentication. Send username and password
        """
        self.logger.debug("Trying keyboard-interactive")
        user = self.script.credentials["user"]
        if user is None:
            user = ""
        password = self.script.credentials["password"]
        if password is None:
            password = ""
        try:
            self.session.userauth_keyboardinteractive(user, password)
            self.logger.debug("Success")
            return True
        except _libssh2.Error:
            code, msg = self.session.last_error()

            self.logger.debug("Failed: %s (Code: %s)", msg, code)
            return False

    def auth_password(self):
        """
        Password authentication. Send username and password
        """
        self.logger.debug("Trying password authentication")
        user = self.script.credentials["user"]
        if user is None:
            user = ""
        password = self.script.credentials["password"]
        if password is None:
            password = ""
        try:
            self.session.userauth_password(user, password)
            self.logger.debug("Success")
            return True
        except _libssh2.Error:
            code, msg = self.session.last_error()

            self.logger.debug("Failed: %s (Code: %s)", msg, code)
            return False


class SSHCLI(CLI):
    name = "ssh"
    default_port = 22
    iostream_class = SSHIOStream
