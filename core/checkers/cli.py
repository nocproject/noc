# ----------------------------------------------------------------------
# CLI checker
# ----------------------------------------------------------------------
# Copyright (C) 2007-2024 The NOC Project
# See LICENSE for details
# ----------------------------------------------------------------------

# Python modules
from typing import List, Iterable, Dict, Tuple

# NOC modules
from .base import Checker, CheckResult, Check
from ..script.scheme import Protocol, CLICredential
from noc.core.service.client import open_sync_rpc
from noc.core.service.error import RPCError
from noc.core.text import safe_shadow


class CLIProtocolChecker(Checker):
    """
    Check ManagedObject supported access protocols and credential
    """

    name = "cli"
    CHECKS: List[str] = ["TELNET", "SSH"]
    GENERIC_PROFILE = "Generic.Host"
    PROTO_CHECK_MAP: Dict[str, Protocol] = {p.config.check: p for p in Protocol if p.config.check}

    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.rules: List[CLICredential] = self.load_suggests(kwargs.get("rules"))
        self.profile = kwargs.get("profile")

    @staticmethod
    def load_suggests(credentials):
        if not credentials:
            return []
        return [x for x in credentials if isinstance(x, CLICredential)]

    @staticmethod
    def is_unsupported_error(message) -> bool:
        """
        Todo replace to error_code
        :param message:
        :return:
        """
        if "Exception: TimeoutError()" in message:
            return True
        if "Error: Connection refused" in message:
            return True
        if "Error: Connection reset" in message:
            return True
        if "No supported authentication methods" in message:
            return True
        return False

    def iter_result(self, checks: List[Check]) -> Iterable[CheckResult]:
        """ """
        # Group by address
        for c in checks:
            if c.name not in self.CHECKS:
                # Unknown check, skipped
                continue
            profile = c.arg0
            if self.profile and self.profile != self.GENERIC_PROFILE:
                profile = self.profile
            if profile == self.GENERIC_PROFILE:
                self.logger.info("CLI Access for Generic profile is not supported. Ignoring")
                continue
            self.logger.info("[CLI] Profile: %s,%s", profile, c.credentials)
            for cred in self.rules:
                status, error = self.check_login(
                    c.address,
                    c.port,
                    cred.username,
                    cred.password,
                    cred.super_password,
                    self.PROTO_CHECK_MAP[c.name],
                    self.profile or c.arg0,
                    cred.raise_privilege,
                )
                if not status and not self.is_unsupported_error(error):
                    continue
                yield CheckResult(
                    check=c.name,
                    arg0=c.arg0,
                    status=status,
                    port=c.port,
                    is_available=not error or not self.is_unsupported_error(error),
                    is_access=status,
                    credentials=[cred] if status else None,
                )
                break
            else:
                yield CheckResult(
                    check=c.name,
                    arg0=c.arg0,
                    status=False,
                    port=c.port,
                    is_available=True,
                    is_access=False,
                )

    def check_login(
        self,
        address: str,
        port: int,
        user: str,
        password: str,
        super_password: str,
        protocol: Protocol,
        profile: str,
        raise_privilege: bool = True,
    ) -> Tuple[bool, str]:
        """
        Check user, password for cli proto
        :param address:
        :param port:
        :param user:
        :param password:
        :param super_password:
        :param protocol:
        :param profile:
        :param raise_privilege:
        :return:
        """
        if not self.pool:
            raise NotImplementedError("Not supported local checks. Set pool")
        self.logger.debug("Checking %s: %s/%s/%s", protocol, user, password, super_password)
        self.logger.info(
            "Checking %s: %s/%s/%s",
            protocol,
            safe_shadow(user),
            safe_shadow(password),
            safe_shadow(super_password),
        )
        try:
            r = open_sync_rpc(
                "activator", pool=self.pool, calling_service=self.calling_service
            ).script(
                f"{profile}.login",
                {
                    "cli_protocol": protocol.config.alias,
                    "cli_port": port,
                    "address": address,
                    "user": user,
                    "password": password,
                    "super_password": super_password,
                    "path": None,
                    "raise_privileges": raise_privilege,
                    "access_preference": "C",
                },
            )
            self.logger.info("Result: %s, %s", r, r["message"])
            return bool(r["result"]), r["message"]  # bool(False) == bool(None)
        except RPCError as e:
            self.logger.debug("RPC Error: %s", e)
            return False, ""
