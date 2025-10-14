#!./bin/python
# ----------------------------------------------------------------------
# tgsender service
# ----------------------------------------------------------------------
# Copyright (C) 2007-2025 The NOC Project
# See LICENSE for details
# ----------------------------------------------------------------------

# Python modules
import orjson
from typing import Dict, Any, Optional, Iterable, Tuple
from urllib.parse import urlencode

# Third-party modules
from gufo.http import DEFLATE, GZIP, Proxy

# NOC modules
from noc.core.service.fastapi import FastAPIService
from noc.core.msgstream.message import Message
from noc.core.mx import MX_TO, MX_WH_API_URL, MX_NOTIFICATION_METHOD
from noc.core.perf import metrics
from noc.config import config
from noc.core.http.sync_client import HttpClient, ERR_TIMEOUT
from noc.core.comp import DEFAULT_ENCODING
from noc.core.text import split_text

TG_API = "https://api.telegram.org/bot"
TGSENDER_STREAM = "tgsender"
CHAT_THREAD_SPLITTER = "::"
MAX_BODY_SIZE = config.tgsender.max_body_size
FILE_SIZE = int(5e7)  # 50Mb


class TgSenderService(FastAPIService):
    name = "tgsender"
    use_telemetry = True

    async def on_activate(self):
        if not config.tgsender.token:
            self.logger.info("No Telegram Bot token defined")
            self.url = None
        else:
            self.url = f"{TG_API}{config.tgsender.token}"
            self.slot_number, self.total_slots = await self.acquire_slot()
            await self.subscribe_stream(TGSENDER_STREAM, self.slot_number, self.on_message)

    @staticmethod
    def parse_address(data, address_to) -> Optional[str]:
        """Parse send address"""
        if address_to:
            return address_to
        if "address" in data:
            return data["address"]
        return None

    async def on_message(self, msg: Message) -> None:
        """
        Process incoming message. Usually forwarded by `mx` service.
        Message MUST have `To` header, containing target Telegram topic.
        Args:
            msg:
        """
        metrics["messages"] += 1
        self.logger.debug("[%s]] Receiving message %s", msg.offset, msg.headers)
        dst = msg.headers.get(MX_TO)
        if not dst:
            self.logger.debug("[%s] Missed '%s' header. Dropping", msg.offset, MX_TO)
            metrics["messages_drops"] += 1
            return
        metrics["messages_processed"] += 1
        data, dst = orjson.loads(msg.value), dst.decode(encoding=DEFAULT_ENCODING)
        address = self.parse_address(data, dst)
        if not address:
            self.logger.warning("[%s] Message without address", msg.offset)
            return
        method = msg.headers[MX_NOTIFICATION_METHOD].decode()
        if method == "webhook" and MX_WH_API_URL in msg.headers:
            # parse webhook_headers
            args = self.parse_webhook_headers(msg.headers)
            await self.send_webhook(msg.offset, address, data, **args)
        elif method == "webhook":
            self.logger.info("[%s] WebHook API is not set", msg.offset)
        elif not method or method == "tg":
            await self.send_tb(msg.offset, address, data)
        else:
            self.logger.info("[%s] Unknown notification method", msg.offset)

    @classmethod
    def iter_tb_messages(
        cls,
        data: Dict[str, Any],
        address_to: str,
    ) -> Iterable[Tuple[bytes, Optional[Dict[str, bytes]]]]:
        """
        Render TG message
                # HTML Style
        <b>bold</b>, <strong>bold</strong>
        <i>italic</i>, <em>italic</em>
        <u>underline</u>, <ins>underline</ins>
        <s>strikethrough</s>, <strike>strikethrough</strike>, <del>strikethrough</del>
        <span class="tg-spoiler">spoiler</span>, <tg-spoiler>spoiler</tg-spoiler>
        <b>bold <i>italic bold <s>italic bold strikethrough <span class="tg-spoiler">italic bold strikethrough spoiler</span></s> <u>underline italic bold</u></i> bold</b>
        <a href="http://www.example.com/">inline URL</a>
        <a href="tg://user?id=123456789">inline mention of a user</a>
        <code>inline fixed-width code</code>
        <pre>pre-formatted fixed-width code block</pre>
        <pre><code class="language-python">pre-formatted fixed-width code block written in the Python programming language</code></pre>

        # Text of the message to be sent, 1-4096 characters after entities parsing
        # Check, if len (body)
        # If len(body) > 4096 use /sendDocument
        # Bots can currently send files of any type of up to 50 MB in size
        """
        address, *message_thread_id = address_to.split(CHAT_THREAD_SPLITTER)
        body, subject = data["body"], data["subject"]
        if len(body.encode()) < MAX_BODY_SIZE:
            send = {
                "chat_id": address,
                "text": f"{subject}\n\n{body}",
                "parse_mode": "HTML",
            }
            if message_thread_id:
                send["message_thread_id"] = message_thread_id[0]
            yield orjson.dumps(send), None
            return
        send = {"chat_id": address, "caption": f"{subject}\n\n{body[0:500]}..."}
        # Send Document
        for part, text in enumerate(split_text(body, max_chunk=FILE_SIZE), start=1):
            # Compress
            if part > 1:
                send = {"chat_id": address}
            yield urlencode(send).encode(), {"document": (text.encode(), f"part_{part}.txt")}

    async def send_tb(
        self,
        message_id: int,
        address: str,
        data: Dict[str, Any],
    ):
        """Send Telegram Bot message"""
        if not self.url:
            # Parse URL
            self.logger.info("No token defined")
            return
        proxy = None
        if config.tgsender.use_proxy and config.tgsender.proxy_address:
            self.logger.info(f"USE PROXY {config.tgsender.proxy_address}")
            proxy = [Proxy(config.tgsender.proxy_address)]
        client = HttpClient(
            max_redirects=None,
            compression=DEFLATE | GZIP,
            validate_cert=False,
            proxies=proxy,
            connect_timeout=config.tgsender.http_connect_timeout,
            timeout=config.tgsender.http_request_timeout,
        )
        for body, files in self.iter_tb_messages(data, address):
            if files:
                url = f"{self.url}/sendDocument"
                h = {"Content-Type": b"application/x-www-form-urlencoded"}
                self.logger.info("Send Document")
            else:
                url = f"{self.url}/sendMessage"
                h = {"Content-Type": b"application/json"}
                self.logger.info("Send Message")
            code, headers, data = client.post(url, body, files=files, headers=h)
            if code == 200:
                self.logger.info(f"Send: {data}\n")
                metrics["telegram_send_ok"] += 1
                continue
            if code == ERR_TIMEOUT:
                self.logger.error("Timeout Error")
                metrics["telegram_send_failed"] += 1
                metrics["error", ("type", "send_telegram_post"), ("code", code)] += 1
            else:
                self.logger.warning("Error when send: %s, %s", code, data)
                metrics["telegram_send_failed"] += 1
                metrics["error", ("type", "send_telegram_post"), ("code", code)] += 1
            break

    @staticmethod
    def parse_webhook_headers(headers: Dict[str, bytes]) -> Dict[str, str]:
        """Parse webhooks headers to params"""
        r = {"api_url": headers[MX_WH_API_URL].decode()}
        for h in headers:
            if not h.startswith("WebHook") or h == MX_WH_API_URL:
                continue
            code, name = h.split("-", 1)
            r[name.replace("-", "_").lower()] = headers[h].decode()
        return r

    async def send_webhook(
        self,
        message_id: int,
        address: str,
        data: Dict[str, Any],
        api_url: str,
        api_method: str = "POST",
        api_authorization: Optional[str] = None,
        to_param_name: Optional[str] = None,
        message_param_name: Optional[str] = None,
        content_type: Optional[str] = None,
        **kwargs,
    ):
        """Send WebHook"""
        client = HttpClient(
            max_redirects=None,
            compression=DEFLATE | GZIP,
            validate_cert=False,
            connect_timeout=config.tgsender.http_connect_timeout,
            timeout=config.tgsender.http_request_timeout,
        )
        headers = {}
        if api_authorization:
            headers["Authorization"] = api_authorization.encode()
        if api_method != "POST":
            self.logger.warning("Unknown API Method: %s", api_method)
            return
        if to_param_name:
            data[to_param_name] = address
        if message_param_name:
            body, subject = data["subject"], data.get("body", "")
            data[message_param_name] = f"{subject}\n\n{body}"
        if content_type and content_type == "application/x-www-form-urlencoded":
            data = urlencode(data).encode()
        else:
            data = orjson.dumps(data)
        content_type = content_type or "application/json"
        headers["Content-Type"] = content_type.encode()
        self.logger.info("[%s] Send Data: %s", "webhook", data)
        code, headers, data = client.post(api_url, data, headers=headers or None)
        self.logger.info("Send: %s, %s", code, data)


if __name__ == "__main__":
    TgSenderService().start()
