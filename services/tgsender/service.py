#!./bin/python
# ----------------------------------------------------------------------
# tgsender service
# ----------------------------------------------------------------------
# Copyright (C) 2007-2021 The NOC Project
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

API = "https://api.telegram.org/bot"
TGSENDER_STREAM = "tgsender"


class TgSenderService(FastAPIService):
    name = "tgsender"

    async def on_activate(self):
        if not config.tgsender.token:
            self.logger.info("No token defined")
            self.url = None
        else:
            self.url = API + config.tgsender.token
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
        self.logger.debug("[%d] Receiving message %s", msg.offset, msg.headers)
        dst = msg.headers.get(MX_TO)
        if not dst:
            self.logger.debug("[%d] Missed '%s' header. Dropping", msg.offset, MX_TO)
            metrics["messages_drops"] += 1
            return
        metrics["messages_processed"] += 1
        return self.send_tb(smart_text(dst), orjson.loads(msg.value))

    @staticmethod
    def escape_markdown(text):
        """Helper function to escape telegram markup symbols"""
        escape_chars = r"\*_`"
        return re.sub(r"([%s])" % escape_chars, r"\\\1", text)

    def send_tb(self, topic: str, data: str) -> None:
        body_l = 3000
        file_size = 5e7  # 50Mb
        t_type = "/sendMessage"
        subject = self.escape_markdown(smart_text(data["subject"], errors="ignore"))
        body = self.escape_markdown(smart_text(data["body"], errors="ignore"))
        send = {
            "chat_id": data["address"],
            "text": "*" + subject + "**\n\n" + body,
            "parse_mode": "Markdown",
        }
        # Text of the message to be sent, 1-4096 characters after entities parsing
        # Check, if len (body)
        if len(body) > body_l:
            caption = "*" + subject + "**\n\n" + body[0:500] + "..."
            # Bots can currently send files of any type of up to 50 MB in size
            # If len(body) > 50Mb use /sendDocument
            if len(body) > file_size:  # len(body) > 50Mb
                t_type = "/sendDocument"
                part = 1
        time.sleep(config.tgsender.retry_timeout)
        if self.url:
            url = self.url + t_type
            proxy = {}
            if config.tgsender.use_proxy and config.tgsender.proxy_address:
                self.logger.info("USE PROXY %s", config.tgsender.proxy_address)
                proxy = {"https": config.tgsender.proxy_address}
            try:
                if t_type == "/sendMessage":
                    self.logger.info("Send Message")
                    response = requests.post(url, send, proxies=proxy)
                else:
                    self.logger.info("Send Document")
                    buf = StringIO()
                    file_lines = body.splitlines()
                    for line in file_lines:
                        if buf.tell() < file_size:
                            if line.strip() == file_lines[-1].strip():
                                buf.write(line)
                                buf.seek(0)
                                buf.name = "part_%s.txt" % part
                                if part > 1:
                                    caption = None
                                response = requests.post(
                                    url,
                                    {"chat_id": data["address"], "caption": caption},
                                    proxies=proxy,
                                    files={"document": buf},
                                )
                                buf.close()
                                continue
                            else:
                                buf.write(line + "\n")
                                continue
                        else:
                            buf.seek(0)
                            buf.name = "part_%s.txt" % part
                            if part > 1:
                                caption = None
                            response = requests.post(
                                url,
                                {"chat_id": data["address"], "caption": caption},
                                proxies=proxy,
                                files={"document": buf},
                            )
                            part = part + 1
                            buf.close()
                            buf = StringIO()
                if proxy:
                    self.logger.info("Proxy Send: %s\n" % response.json())
                    metrics["telegram_proxy_proxy_ok"] += 1
                else:
                    self.logger.info("Send: %s\n" % response.json())
                    metrics["telegram_sended_ok"] += 1
            except requests.HTTPError as error:
                self.logger.error("Http Error: %s" % error)
                if proxy:
                    metrics["telegram_proxy_failed_httperror"] += 1
                else:
                    metrics["telegram_failed_httperror"] += 1
            except requests.ConnectionError as error:
                self.logger.error("Error Connecting: %s" % error)
                if proxy:
                    metrics["telegram_proxy_failed_connection"] += 1
                else:
                    metrics["telegram_failed_connection"] += 1
            except requests.Timeout as error:
                self.logger.error("Timeout Error: %s" % error)
                if proxy:
                    metrics["telegram_proxy_failed_timeout"] += 1
                else:
                    metrics["telegram_failed_timeout"] += 1
            except requests.RequestException as error:
                self.logger.error("OOps: Something Else %s" % error)
                if proxy:
                    metrics["telegram_proxy_failed_else_error"] += 1
                else:
                    metrics["telegram_failed_else_error"] += 1
        else:
            self.logger.info("No token, no Url.")


if __name__ == "__main__":
    TgSenderService().start()
