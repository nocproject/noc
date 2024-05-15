# ----------------------------------------------------------------------
# CLI checker
# ----------------------------------------------------------------------
# Copyright (C) 2007-2024 The NOC Project
# See LICENSE for details
# ----------------------------------------------------------------------

# Python modules
from typing import List, Iterable, Dict, Tuple, Optional

# NOC modules
from .base import Checker, CheckResult, Check, CheckError
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
    PARAMS = ["profile", "rules"]

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

    def iter_credential(
        self,
        check: Check,
    ) -> Iterable[Tuple[Protocol, CLICredential]]:
        """

        :param check:
        :return:
        """
        if check.credential:
            yield self.PROTO_CHECK_MAP[check.name], check.credential
        for proto, cred in self.rules:
            yield proto, cred

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
            for proto, cred in self.iter_credential(c):
                status, error = self.check_login(
                    c.address or self.address,
                    c.port,
                    cred.username,
                    cred.password,
                    cred.super_password,
                    proto,
                    profile,
                    cred.raise_privilege,
                )
                if not status and not self.is_unsupported_error(error.message):
                    continue
                yield CheckResult(
                    check=c.name,
                    args=c.args,
                    status=status,
                    port=c.port,
                    error=error,
                    credential=cred if status else None,
                )
                break
            else:
                yield CheckResult(
                    check=c.name,
                    args=c.args,
                    status=False,
                    port=c.port,
                    error=CheckError(code="0", is_access=False, is_available=True),
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
    ) -> Tuple[bool, Optional[CheckError]]:
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
            status = bool(r["result"])
            if status:
                return True, None
            return status, CheckError(
                code="0",
                message=r["message"],
                is_available=not status or not self.is_unsupported_error(r["message"]),
                is_access=status,
            )  # bool(False) == bool(None)
        except RPCError as e:
            self.logger.debug("RPC Error: %s", e)
            return False, CheckError(code="0", message=str(e))
