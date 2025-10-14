# ----------------------------------------------------------------------
# Synchronous HTTP Client
# ----------------------------------------------------------------------
# Copyright (C) 2007-2025 The NOC Project
# See LICENSE for details
# ----------------------------------------------------------------------

# Python modules
import logging
import uuid
from urllib.parse import urlparse
from typing import Optional, Dict, Tuple, Any, Callable, Union

# Third-party modules
from gufo.http import BasicAuth, RequestMethod, DEFLATE, GZIP, BROTLI, Proxy, HttpError
from gufo.http.sync_client import HttpClient as GufoHttpClient

# NOC modules
from noc.core.perf import metrics
from noc.core.comp import DEFAULT_ENCODING
from noc.config import config
from noc.core.validators import is_ipv4
from .proxy import SYSTEM_PROXIES
from .resolver import resolve_sync

logger = logging.getLogger(__name__)

ERR_TIMEOUT = 599
ERR_READ_TIMEOUT = 598
DEFAULT_PORTS = {"http": config.http_client.http_port, "https": config.http_client.https_port}


class HttpClient(GufoHttpClient):
    """
    Synchronous HTTP client.
    Attributes:
        headers: Headers to be added to every request.
            Used in subclasses.
        user_agent: Default user agent.
    Args:
        max_redirects: Maximal amount of redirects. Use `None`
            to disable redirect processing.
        compression: Acceptable compression methods,
            must be a combination of `DEFLATE`, `GZIP`, `BROTLI`.
            Set to `None` to disable compression support.
        validate_cert: Set to `False` to disable TLS certificate
            validation. Otherwise, raise `ConnectionError`
            on invalid certificates.
        connect_timeout: Timeout to establish connection, in seconds.
        timeout: Request timeout, in seconds.
        user: Authentication settings.
        password: Password
    """

    user_agent = config.http_client.user_agent

    def __init__(
        self: "HttpClient",
        /,
        max_redirects: Optional[int] = config.http_client.max_redirects,
        headers: Optional[Dict[str, bytes]] = None,
        compression: Optional[int] = DEFLATE | GZIP | BROTLI,
        validate_cert: bool = config.http_client.validate_certs,
        connect_timeout: float = config.http_client.connect_timeout,
        timeout: float = config.http_client.request_timeout,
        user_agent: Optional[str] = None,
        user: Optional[str] = None,
        password: Optional[str] = None,
        allow_proxy=False,
        proxies=None,
        resolver=None,
    ) -> None:
        auth = None
        if user:
            auth = BasicAuth(user=user, password=password)
        if allow_proxy:
            proxy = (proxies or SYSTEM_PROXIES).get("https")
        else:
            proxy = None
        self.resolver: Optional[Callable] = resolver or resolve_sync
        super().__init__(
            max_redirects=max_redirects,
            headers=headers,
            compression=compression,
            validate_cert=validate_cert,
            connect_timeout=connect_timeout,
            timeout=timeout,
            user_agent=user_agent or self.user_agent,
            auth=auth,
            proxy=[Proxy(proxy)] if proxy else None,
        )

    def resolve(self, url: str) -> str:
        if not self.resolver:
            return url

        u = urlparse(str(url))
        if ":" in u.netloc:
            host, port = u.netloc.rsplit(":")
        else:
            host = u.netloc
            port = DEFAULT_PORTS.get(u.scheme)
        if is_ipv4(host):
            return url
        addr = self.resolver(host)
        if not addr:
            raise TimeoutError("Cannot resolve host: %s" % host)
        if isinstance(addr, tuple):
            host = "%s:%s" % addr
        else:
            host = f"{addr}:{port}"
        return u._replace(netloc=host).geturl()

    @classmethod
    def encode_part(
        cls,
        body,
        boundary,
        name: Optional[str] = None,
        filename: Optional[str] = None,
        content_type: Optional[str] = None,
    ):
        """
        Encode Form Data Part
        Args:
            body: Part body
            boundary: Part splitter boundary
            name: Part name
            filename: If part contains file - its name
            content_type: Content type in part
        """
        content_type = content_type or "application/octet-stream"
        dispositions = ["form-data", f"name={name}"]
        if filename:
            dispositions.append(f'filename="{filename}"')
        return b"".join(
            [
                f"--{boundary}\r\n".encode(),
                f"Content-Disposition: {';'.join(dispositions)}\r\n".encode(),
                f"Content-Length: {len(body)}\r\n".encode(),
                f"Content-Type: {content_type}\r\n".encode(),
                b"\r\n",
                body,
                b"\r\n",
            ]
        )

    @classmethod
    def encode_files(
        cls,
        files: Dict[str, Union[bytes, Tuple[bytes, str], Tuple[bytes, str, str]]],
        boundary: str,
        content_type: Optional[str] = "application/octet-stream",
    ) -> bytes:
        """
        Render file ports
            "json_data": (None, json.dumps(data_payload), 'application/json'), # JSON part
            "uploaded_file": ('data.json', f, 'application/octet-stream') # File part
        Args:
            files: name -> content; name -> (content, filename); name -> (content, filename, content-type)
            boundary: File part splitter
            content_type: Default content type (application/octet-stream)
        """
        content_type = content_type or "application/octet-stream"
        payload = b""
        for name, body in files.items():
            if isinstance(body, bytes):
                args = []
            else:
                body, *args = body
            # Part Name
            if args:
                filename = args[0]
            else:
                filename = name
            # Part Content Type
            if args and len(args) > 1:
                mime = args[1]
            else:
                mime = content_type
            payload += cls.encode_part(
                body, boundary, name=name, filename=filename, content_type=mime
            )
        return payload

    def request(
        self: "HttpClient",
        method: str,
        url: str,
        /,
        body: Optional[bytes] = None,
        headers: Optional[Dict[str, bytes]] = None,
    ) -> Tuple[int, Dict[str, Any], bytes]:
        m = RequestMethod.get(method)
        if not m:
            raise NotImplementedError("Not implementer method: %s", method)
        metrics["httpclient_requests", ("method", method.lower())] += 1
        try:
            r = super().request(m, url, body=body, headers=headers)
        except ConnectionResetError:
            metrics["httpclient_timeouts"] += 1
            return ERR_TIMEOUT, {}, b"Connection reset while sending request"
        except (ConnectionError, HttpError) as e:
            metrics["httpclient_timeouts"] += 1
            return ERR_TIMEOUT, {}, b"Connection error: %s" % str(e).encode(DEFAULT_ENCODING)
        except TimeoutError:
            metrics["httpclient_timeouts"] += 1
            return ERR_TIMEOUT, {}, b"Timed out while sending request"
        return r.status, r.headers, r.content

    def get(
        self, url: str, /, headers: Optional[Dict[str, bytes]] = None
    ) -> Tuple[int, Dict[str, Any], bytes]:
        metrics["httpclient_requests", ("method", "get")] += 1
        try:
            r = super().get(url, headers=headers)
        except ConnectionResetError:
            metrics["httpclient_timeouts"] += 1
            return ERR_TIMEOUT, {}, b"Connection reset while sending request"
        except (ConnectionError, HttpError) as e:
            metrics["httpclient_timeouts"] += 1
            return ERR_TIMEOUT, {}, b"Connection error: %s" % str(e).encode(DEFAULT_ENCODING)
        except TimeoutError:
            metrics["httpclient_timeouts"] += 1
            return ERR_TIMEOUT, {}, b"Timed out while sending request"
        return r.status, r.headers, r.content

    def post(
        self,
        url: str,
        body: bytes,
        /,
        headers: Optional[Dict[str, bytes]] = None,
        files: Optional[Dict[str, Union[bytes, Tuple[bytes, str], Tuple[bytes, str, str]]]] = None,
    ) -> Tuple[int, Dict[str, Any], bytes]:
        metrics["httpclient_requests", ("method", "post")] += 1
        if files:
            boundary = str(uuid.uuid4())
            headers = headers or {}
            content_type = headers.get("Content-Type") or b"text/plain"
            # Body parts
            if body:
                body = self.encode_part(
                    body,
                    boundary,
                    name="data",
                    content_type=content_type.decode(),
                )
            body += self.encode_files(files, boundary)
            body += f"--{boundary}--\r\n".encode()
            headers = headers | {
                "Content-Type": f"multipart/form-data; boundary={boundary}".encode(),
                "Content-Length": str(len(body)).encode(),
            }
        try:
            r = super().post(url, body, headers=headers)
        except ConnectionResetError:
            metrics["httpclient_timeouts"] += 1
            return ERR_TIMEOUT, {}, b"Connection reset while sending request"
        except (ConnectionError, HttpError) as e:
            metrics["httpclient_timeouts"] += 1
            return ERR_TIMEOUT, {}, b"Connection error: %s" % str(e).encode(DEFAULT_ENCODING)
        except TimeoutError:
            metrics["httpclient_timeouts"] += 1
            return ERR_TIMEOUT, {}, b"Timed out while sending request"
        return r.status, r.headers, r.content

    def put(
        self,
        url: str,
        body: bytes,
        /,
        headers: Optional[Dict[str, bytes]] = None,
    ) -> Tuple[int, Dict[str, Any], bytes]:
        metrics["httpclient_requests", ("method", "put")] += 1
        try:
            r = super().put(url, body, headers=headers)
        except ConnectionResetError:
            metrics["httpclient_timeouts"] += 1
            return ERR_TIMEOUT, {}, b"Connection reset while sending request"
        except (ConnectionError, HttpError) as e:
            metrics["httpclient_timeouts"] += 1
            return ERR_TIMEOUT, {}, b"Connection error: %s" % str(e).encode(DEFAULT_ENCODING)
        except TimeoutError:
            metrics["httpclient_timeouts"] += 1
            return ERR_TIMEOUT, {}, b"Timed out while sending request"
        return r.status, r.headers, r.content
