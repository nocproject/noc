#!./bin/python
# ----------------------------------------------------------------------
# tgsender service
# ----------------------------------------------------------------------
# Copyright (C) 2007-2022 The NOC Project
# See LICENSE for details
# ----------------------------------------------------------------------

# Python modules
import re
import orjson
import requests
import time
from io import StringIO

# NOC modules
from noc.core.service.fastapi import FastAPIService
from noc.core.liftbridge.message import Message
from noc.core.mx import MX_TO
from noc.core.perf import metrics
from noc.config import config
from noc.core.comp import smart_text
from noc.core.text import split_text

API = "https://api.telegram.org/bot"
TGSENDER_STREAM = "tgsender"


class TgSenderService(FastAPIService):
    name = "tgsender"

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
        self.logger.debug(f"[{msg.offset}] Receiving message {msg.headers}")
        dst = msg.headers.get(MX_TO)
        if not dst:
            self.logger.debug(f"[{msg.offset}] Missed '{MX_TO}' header. Dropping")
            metrics["messages_drops"] += 1
            return
        metrics["messages_processed"] += 1
        return self.send_tb(smart_text(dst), orjson.loads(msg.value))

    @staticmethod
    def escape_markdown(text):
        """Helper function to escape telegram markup symbols"""
        escape_chars = r"\*_`["
        return re.sub(r"([%s])" % escape_chars, r"\\\1", text)

    def send_tb(self, topic: str, data: str) -> None:
        body_l = 3000
        file_size = 5e7  # 50Mb
        t_type = "/sendMessage"
        subject = self.escape_markdown(smart_text(data["subject"], errors="ignore"))
        body = self.escape_markdown(smart_text(data["body"], errors="ignore"))
        send = {
            "chat_id": data["address"],
            "text": f"- {subject} --\n\n {body}",
            "parse_mode": "Markdown",
        }
        # Text of the message to be sent, 1-4096 characters after entities parsing
        # Check, if len (body)
        # If len(body) > 4096 use /sendDocument
        # Bots can currently send files of any type of up to 50 MB in size
        if len(body) > body_l:
            caption = f"- {subject} --\n\n {body[0:500]}..."
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
                            {"chat_id": data["address"], "caption": caption},
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
