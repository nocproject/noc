#!./bin/python
# ----------------------------------------------------------------------
# icqsender service
# ----------------------------------------------------------------------
# Copyright (C) 2007-2021 The NOC Project
# See LICENSE for details
# ----------------------------------------------------------------------

# Python modules
import re
import orjson
import requests
import time
from typing import Dict, Any, Optional
from urllib.parse import urlencode

# NOC modules
from noc.core.service.fastapi import FastAPIService
from noc.core.liftbridge.message import Message
from noc.core.mx import MX_TO
from noc.core.perf import metrics
from noc.config import config
from noc.core.comp import smart_text, DEFAULT_ENCODING

API = "https://api.icq.net/bot/v1/messages/sendText?token="
ICQSENDER_STREAM = "icqsender"


class IcqSenderService(FastAPIService):
    name = "icqsender"

    async def on_activate(self):
        if not config.icqsender.token:
            self.logger.info("No ICQ token defined")
            self.url = None
        else:
            self.url = API + config.icqsender.token + "&"
            self.slot_number, self.total_slots = await self.acquire_slot()
            await self.subscribe_stream(ICQSENDER_STREAM, self.slot_number, self.on_message)

    async def on_message(self, msg: Message) -> None:
        """
        Process incoming message. Usually forwarded by `mx` service.
        Message MUST have `To` header, containing target ICQ topic.

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
        return self.send_icq(
            msg.offset, orjson.loads(msg.value), dst.decode(encoding=DEFAULT_ENCODING)
        )

    @staticmethod
    def escape_markdown(text):
        """Helper function to escape markup symbols"""
        escape_chars = r"\*_`"
        return re.sub(r"([%s])" % escape_chars, r"\\\1", text)

    def send_icq(
        self, message_id: int, data: Dict[str, Any], address_to: Optional[str] = None
    ) -> None:
        if "address" in data:
            address = data["address"]
        elif address_to:
            address = address_to
        else:
            self.logger.warning("[%s] Message without address", message_id)
            return
        sendMessage = {
            "chatId": address,
            "text": "*"
            + self.escape_markdown(smart_text(data["subject"], errors="ignore"))
            + "*\n"
            + self.escape_markdown(smart_text(data["body"], errors="ignore")),
        }
        time.sleep(config.icqsender.retry_timeout)
        if self.url:
            get = self.url + urlencode(sendMessage)
            self.logger.info("HTTP GET %s", urlencode(sendMessage))
            proxy = {}
            if config.icqsender.use_proxy and config.icqsender.proxy_address:
                self.logger.info("USE PROXY %s", config.icqsender.proxy_address)
                proxy = {"https": config.icqsender.proxy_address}
            try:
                response = requests.get(get, proxies=proxy)
                if proxy:
                    self.logger.info("Proxy Send: %s\n" % response.json())
                    metrics["icq_proxy_proxy_ok"] += 1
                else:
                    self.logger.info("Send: %s\n" % response.json())
                    metrics["icq_sended_ok"] += 1
            except requests.HTTPError as error:
                self.logger.error("Http Error: %s", error)
                if proxy:
                    metrics["icq_proxy_failed_httperror"] += 1
                else:
                    metrics["icq_failed_httperror"] += 1
            except requests.ConnectionError as error:
                self.logger.error("Error Connecting: %s", error)
                if proxy:
                    metrics["icq_failed_connection"] += 1
                else:
                    metrics["icq_connection"] += 1
            except requests.Timeout as error:
                self.logger.error("Timeout Error: %s", error)
                if proxy:
                    metrics["icq_failed_timeout"] += 1
                else:
                    metrics["icq_failed_timeout"] += 1
            except requests.RequestException as error:
                self.logger.error("OOps: Something Else: %s", error)
                if proxy:
                    metrics["icq_proxy_failed_else_error"] += 1
                else:
                    metrics["icq_failed_else_error"] += 1
        else:
            self.logger.info("No token, no Url.")


if __name__ == "__main__":
    IcqSenderService().start()
