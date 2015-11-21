# -*- coding: utf-8 -*-
##----------------------------------------------------------------------
## SSH CLI
##----------------------------------------------------------------------
## Copyright (C) 2007-2015 The NOC Project
## See LICENSE for details
##----------------------------------------------------------------------

## Python modules
import os
## Third-party modules modules
from tornado.iostream import IOStream
import tornado.gen
import libssh2
import _libssh2
## NOC modules
from base import CLI


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
        self.logger.debug("Startup ssh session")
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
                ah = getattr(self, "auth_%s" % method, None)
                if ah:
                    authenticated |= ah()
                    if authenticated:
                        break
            if authenticated:
                self.logger.debug("User is authenticated")
            else:
                self.logger.error("Failed to authenticate user '%s'", user)
                raise self.cli.CLIError("Failed to log in")
            self.channel = self.session.open_session()
            self.channel.pty("xterm")
            self.channel.shell()
            self.channel.setblocking(0)
        except _libssh2.Error, why:
            raise self.cli.CLIError("SSH Error: %s" % why)

    def read_from_fd(self):
        try:
            return self.channel.read(self.read_chunk_size)
        except _libssh2.Error, why:
            raise self.cli.CLIError("SSH Error: %s" % why)

    def write_to_fd(self, data):
        try:
            return self.channel.write(data)
        except _libssh2.Error, why:
            raise self.cli.CLIError("SSH Error: %s" % why)

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
        try:
            self.session.userauth_publickey_fromfile(
                self.script.credentials["user"],
                publickey=pub_path,
                privatekey=priv_path,
                passphrase=""
            )
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
        try:
            self.session.userauth_password(
                self.script.credentials["user"],
                self.script.credentials["password"]
            )
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
