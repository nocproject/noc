#!./bin/python
# ----------------------------------------------------------------------
# tgsender service
# ----------------------------------------------------------------------
# Copyright (C) 2007-2022 The NOC Project
# See LICENSE for details
# ----------------------------------------------------------------------

# Python modules
import orjson
import requests
import time
from typing import Dict, Any, Optional
from io import StringIO

# NOC modules
from noc.core.service.fastapi import FastAPIService
from noc.core.msgstream.message import Message
from noc.core.mx import MX_TO
from noc.core.perf import metrics
from noc.config import config
from noc.core.comp import smart_text, DEFAULT_ENCODING
from noc.core.text import split_text

API = "https://api.telegram.org/bot"
TGSENDER_STREAM = "tgsender"


class TgSenderService(FastAPIService):
    name = "tgsender"
    use_telemetry = True

    async def on_activate(self):
        if not config.tgsender.token:
            self.logger.info("No token defined")
            self.url = None
        else:
            self.url = f"{API}{config.tgsender.token}"
            self.slot_number, self.total_slots = await self.acquire_slot()
            await self.subscribe_stream(TGSENDER_STREAM, self.slot_number, self.on_message)

    async def on_message(self, msg: Message) -> None:
        """
        Process incoming message. Usually forwarded by `mx` service.
        Message MUST have `To` header, containing target Telegram topic.

        :param msg:
        :return:
        """
        metrics["messages"] += 1
        self.logger.debug("[%s]] Receiving message %s", msg.offset, msg.headers)
        dst = msg.headers.get(MX_TO)
        if not dst:
            self.logger.debug("[%s] Missed '%s' header. Dropping", msg.offset, MX_TO)
            metrics["messages_drops"] += 1
            return
        metrics["messages_processed"] += 1
        return self.send_tb(
            msg.offset, orjson.loads(msg.value), dst.decode(encoding=DEFAULT_ENCODING)
        )

    def send_tb(
        self, message_id: int, data: Dict[str, Any], address_to: Optional[str] = None
    ) -> None:
        body_l = 3000
        file_size = 5e7  # 50Mb
        t_type = "/sendMessage"
        subject = smart_text(data["subject"])
        body = smart_text(data["body"])
        if "address" in data:
            address = data["address"]
        elif address_to:
            address = address_to
        else:
            self.logger.warning("[%s] Message without address", message_id)
            return
        send = {
            "chat_id": address,
            "text": f"{subject}\n\n{body}",
            "parse_mode": "HTML",
        }
        # HTML Style
        """
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
        """
        # Text of the message to be sent, 1-4096 characters after entities parsing
        # Check, if len (body)
        # If len(body) > 4096 use /sendDocument
        # Bots can currently send files of any type of up to 50 MB in size
        if len(body) > body_l:
            caption = f"{subject}\n\n{body[0:500]}..."
            t_type = "/sendDocument"
        time.sleep(config.tgsender.retry_timeout)
        if self.url:
            url = "".join([self.url, t_type])
            proxy = {}
            if config.tgsender.use_proxy and config.tgsender.proxy_address:
                self.logger.info(f"USE PROXY {config.tgsender.proxy_address}")
                proxy = {"https": config.tgsender.proxy_address}
            try:
                if t_type == "/sendMessage":
                    self.logger.info("Send Message")
                    response = requests.post(url, send, proxies=proxy)
                else:
                    self.logger.info("Send Document")
                    buf = StringIO()
                    for part, text in enumerate(split_text(body, file_size)):
                        part = part + 1
                        buf.write(text)
                        buf.seek(0)
                        buf.name = f"part_{part}.txt"
                        if part > 1:
                            caption = None
                        response = requests.post(
                            url,
                            {"chat_id": address, "caption": caption},
                            proxies=proxy,
                            files={"document": buf},
                        )
                        buf = StringIO()
                    buf.close()
                if proxy:
                    self.logger.info(f"Proxy Send: {response.json()}\n")
                    metrics["telegram_proxy_proxy_ok"] += 1
                else:
                    self.logger.info(f"Send: {response.json()}\n")
                    metrics["telegram_sended_ok"] += 1
            except requests.HTTPError as error:
                self.logger.error(f"Http Error: {error}")
                if proxy:
                    metrics["telegram_proxy_failed_httperror"] += 1
                else:
                    metrics["telegram_failed_httperror"] += 1
            except requests.ConnectionError as error:
                self.logger.error(f"Error Connecting: {error}")
                if proxy:
                    metrics["telegram_proxy_failed_connection"] += 1
                else:
                    metrics["telegram_failed_connection"] += 1
            except requests.Timeout as error:
                self.logger.error(f"Timeout Error: {error}")
                if proxy:
                    metrics["telegram_proxy_failed_timeout"] += 1
                else:
                    metrics["telegram_failed_timeout"] += 1
            except requests.RequestException as error:
                self.logger.error(f"OOps: Something Else {error}")
                if proxy:
                    metrics["telegram_proxy_failed_else_error"] += 1
                else:
                    metrics["telegram_failed_else_error"] += 1
        else:
            self.logger.info("No token, no Url.")


if __name__ == "__main__":
    TgSenderService().start()
