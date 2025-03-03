# ----------------------------------------------------------------------
# HTTP Checker
# ----------------------------------------------------------------------
# Copyright (C) 2007-2024 The NOC Project
# See LICENSE for details
# ----------------------------------------------------------------------

# Python modules
from urllib.parse import urlparse
from typing import List, Iterable

# NOC modules
from noc.core.checkers.base import Checker, CheckResult, Check, CheckError
from noc.core.http.async_client import HttpClient as ASyncHttpClient
from noc.core.http.sync_client import HttpClient as SyncHttpClient

HTTP_CHECK = "HTTP"
HTTPS_CHECK = "HTTPS"


class HTTPChecker(Checker):
    """
    Check address availability from remote device
    """

    name = "http"
    CHECKS: List[str] = [HTTP_CHECK, HTTPS_CHECK]
    CONNECT_TIMEOUT = 2
    REQUEST_TIMEOUT = 3

    @staticmethod
    def parse_url(url, address, check) -> str:
        url = urlparse(url)
        if not url.scheme:
            url = url._replace(scheme="http" if check == HTTP_CHECK else "https")
        if not url.netloc:
            url = url._replace(netloc=address)
        return url.geturl()

    async def iter_result_async(self, checks: List[Check]) -> Iterable[CheckResult]:
        client = ASyncHttpClient(
            max_redirects=None,
            headers={"X-NOC-Calling-Service": b"noc-check"},
            connect_timeout=self.CONNECT_TIMEOUT,
            timeout=self.REQUEST_TIMEOUT,
        )
        for c in checks:
            # url = urlparse()
            url = self.parse_url(c.args["url"], c.address, c.name)
            code, headers, data = await client.get(url)
            # Process response
            if code == 200:
                error = None
            elif code in (598, 599):
                self.logger.debug("Timed out")
                error = CheckError(code=str(code), message="Timed out", is_available=False)
            else:
                error = CheckError(
                    code=str(code), message=f"HTTP Error {code}: {data}", is_available=True
                )
            yield CheckResult(
                check=HTTP_CHECK,
                address=c.address,
                port=c.port,
                args=c.args,
                status=not bool(error),
                error=error,
            )

    def iter_result(self, checks: List[Check]) -> Iterable[CheckResult]:
        client = SyncHttpClient(
            max_redirects=None,
            headers={"X-NOC-Calling-Service": b"noc-check"},
            connect_timeout=self.CONNECT_TIMEOUT,
            timeout=self.REQUEST_TIMEOUT,
        )
        for c in checks:
            url = self.parse_url(c.args["url"], c.address, c.name)
            code, headers, data = client.get(url)
            # Process response
            if code == 200:
                error = None
            elif code in (598, 599):
                self.logger.debug("Timed out")
                error = CheckError(code=str(code), message="Timed out", is_available=False)
            else:
                error = CheckError(
                    code=str(code), message=f"HTTP Error {code}: {data}", is_available=True
                )
            yield CheckResult(
                check=HTTP_CHECK,
                address=c.address,
                port=c.port,
                args=c.args,
                status=not bool(error),
                error=error,
            )
