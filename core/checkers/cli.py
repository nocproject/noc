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
from noc.core.script.loader import loader
from noc.core.perf import metrics


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
        self.profile = kwargs.get("profile")

    @staticmethod
    def load_suggests(credentials):
        if not credentials:
            return []
        return [(p, x) for p, x in credentials if isinstance(x, CLICredential)]

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
                    address=c.address,
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
                    address=c.address,
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
        script = f"{profile}.login"
        script_class = loader.get_script(script)
        if not script_class:
            return False, CheckError(code="1", message="Unknown script")
        script = script_class(
            service="activator",
            credentials={
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
            name=script,
            timeout=60,
        )
        try:
            r = script.run()
        except script.ScriptError as e:
            metrics["error", ("type", "script_error")] += 1
            return False, CheckError(code="0", message="Script error: %s" % e.__doc__)
        status = bool(r["result"])
        if status:
            return status, None
        return False, CheckError(
            code="0",
            message=r["message"],
            is_available=not status or not self.is_unsupported_error(r["message"]),
            is_access=status,
        )
