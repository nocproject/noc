#!./bin/python
# -*- coding: utf-8 -*-
# ----------------------------------------------------------------------
# webhook service
# ----------------------------------------------------------------------
# Copyright (C) 2007-2019 The NOC Project
# See LICENSE for details
# ----------------------------------------------------------------------

# Third-party modules
import re
import datetime
import time
import urllib
# NOC modules
from noc.core.service.base import Service
from noc.core.http.client import fetch_sync
from noc.core.perf import metrics
from noc.config import config


class WebhookService(Service):
    name = "webhook"

    def __init__(self, *args, **kwargs):
        super(WebhookService, self).__init__(*args, **kwargs)
        self.url = config.webhook.url
        self.message = config.webhook.message
        self.sender = config.webhook.sender
        self.method = "POST" if config.webhook.method is True else "GET"
        self.received = config.webhook.received
        self.options = config.webhook.options

    def on_activate(self):
        if self.url and self.message and self.received:
            self.subscribe(
                topic=self.name,
                channel="sender",
                handler=self.on_message
            )

    def on_message(self, message, address, subject, body, **kwargs):
        self.logger.info(
            "[%s] Receiving message: %s (%s) [%s, attempt %d]",
            message.id, subject, address,
            datetime.datetime.fromtimestamp(
                message.timestamp / 1000000000.0
            ),
            message.attempts
        )
        return self.send_tb(message.id, address, subject, body)

    def _str(self, uni):
        ''' Make inbound a string Encoding to utf-8 if needed '''
        try:
            return str(uni)
        except Exception as e:
            self.logger.error("Not str() -> %s failed: %s", uni, e)
            return uni.encode('utf-8')

    @staticmethod
    def escape_markdown(text):
        """Helper function to escape telegram markup symbols"""
        escape_chars = '\*_`'
        return re.sub(r'([%s])' % escape_chars, r'\\\1', text)

    def send_tb(self, messages, address, subject, body):
        # proxy_addres = config.proxy.https_proxy  # not used.
        sendMessage = self._str(subject + '\n' + body)
        time.sleep(config.webhook.retry_timeout)
        if self.url and self.message and self.received:
            url = self.url
            if self.received:
                url = url + "%s%s" % (self.received, address)
            if self.sender:
                url = url + self.sender
            url = url + "%s%s" % (self.message, urllib.quote(sendMessage))
            if self.options:
                url = url + self.options
            self.logger.info("HTTP %s %s", self.method, url)
            try:
                code, header, body = fetch_sync(
                    url,
                    method=self.method,
                    allow_proxy=True,
                    request_timeout=config.activator.http_request_timeout,
                    follow_redirects=True,
                    validate_cert=config.activator.http_validate_cert,
                )
                if 200 <= code <= 299:
                    self.logger.info("Result: %s" % body)
                    metrics["webhook_proxy_sended_ok"] += 1
                    return True
                else:
                    self.logger.error("HTTP %s %s failed: %s %s", self.method, url, code, body)
                    metrics["webhook_proxy_failed_httperror"] += 1
                    return False
            except Exception as e:
                self.logger.error("HTTP %s failed: %s", self.method, e)
        else:
            self.logger.info("No Url, no message, no sender, no received")
            return False


if __name__ == "__main__":
    WebhookService().start()
