#!./bin/python
# -*- coding: utf-8 -*-
# ----------------------------------------------------------------------
# icqsender service
# ----------------------------------------------------------------------
# Copyright (C) 2007-2019 The NOC Project
# See LICENSE for details
# ----------------------------------------------------------------------

# Third-party modules
import re
import datetime
import json
import time

# Third-party modules
from six.moves.urllib.parse import urlencode

# NOC modules
from noc.core.service.base import Service
from noc.core.http.client import fetch_sync
from noc.core.perf import metrics
from noc.config import config

API = "https://api.icq.net/bot/v1/messages/sendText?token="


class IcqSenderService(Service):
    name = "icqsender"

    def on_activate(self):
        if not config.icqsender.token:
            self.logger.info("No ICQ token defined")
            self.url = None
        else:
            self.url = API + config.icqsender.token + "&"
            self.subscribe(topic=self.name, channel="sender", handler=self.on_message)

    def on_message(self, message, address, subject, body, attachments=None, **kwargs):
        self.logger.info(
            "[%s] Receiving message: %s (%s) [%s, attempt %d]",
            message.id,
            subject,
            address,
            datetime.datetime.fromtimestamp(message.timestamp / 1000000000.0),
            message.attempts,
        )
        return self.send_tb(message.id, address, subject, body)

    @staticmethod
    def escape_markdown(text):
        """Helper function to escape markup symbols"""
        escape_chars = r"\*_`"
        return re.sub(r"([%s])" % escape_chars, r"\\\1", text)

    def send_tb(self, messages, address, subject, body):
        # proxy_addres = config.proxy.https_proxy  # not used.
        sendMessage = {
            "chatId": address,
            "text": "*"
            + self.escape_markdown(subject.encode("utf8"))
            + "*\n"
            + self.escape_markdown(body.encode("utf8")),
        }
        time.sleep(config.icqsender.retry_timeout)
        if self.url:
            get = self.url + urlencode(sendMessage)
            self.logger.info("HTTP GET %s", get)
            code, header, body = fetch_sync(
                get,
                allow_proxy=True,
                request_timeout=config.activator.http_request_timeout,
                follow_redirects=True,
                validate_cert=config.activator.http_validate_cert,
            )
            if 200 <= code <= 299:
                check = json.loads(body)
                self.logger.info("Result: %s" % check)
                metrics["icq_sended_ok"] += 1
                return True
            else:
                self.logger.error("HTTP GET %s failed: %s %s", get, code, body)
                metrics["icq_failed_httperror"] += 1
                return False
        else:
            self.logger.info("No token, no Url.")
            return False


if __name__ == "__main__":
    IcqSenderService().start()
