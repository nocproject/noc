#!./bin/python
# -*- coding: utf-8 -*-
##----------------------------------------------------------------------
## mailsender service
##----------------------------------------------------------------------
## Copyright (C) 2007-2016 The NOC Project
## See LICENSE for details
##----------------------------------------------------------------------

## Third-party modules

import datetime
import socket
import json
import requests
import time
## NOC modules
from noc.core.service.base import Service
from noc.core.perf import metrics


class TgSenderService(Service):
    name = "tgsender"
    process_name = "noc-%(name).10s-%(instance).3s"

    def on_activate(self):
        self.subscribe(
            topic=self.name,
            channel="sender",
            handler=self.on_message
        )

    def on_message(self, message, address, subject, body, attachments=None, **kwargs):
        self.logger.info(
            "[%s] Receiving message: %s (%s) [%s, attempt %d]",
            message.id, subject, address,
            datetime.datetime.fromtimestamp(
                message.timestamp / 1000000000.0
            ),
            message.attempts
        )

        return self.send_tb(message.id, address, subject, body)

    def make_url_query_string(self, params):
        return '?' + '&'.join([str(key) + '=' + str(params[key]) for key in params])

    def send_tb(self, message_id, address, subject, body):
        TOKEN = self.config.token
        INTERVAL = 2.0
        URL = 'https://api.telegram.org/bot'
        time.sleep(INTERVAL)
        params = self.make_url_query_string({'chat_id': address, 'text': body})
        req = requests.get(URL + TOKEN + '/sendMessage' + params)
        if req.json()['ok']:
            self.logger.info("Send: %s\n" % req.json())
            metrics["telegram_sended"] += 1
            return True
        elif req.status_code != 200 or not req.json()['ok']:
            self.logger.info("Error: %s\n" % req.json())
            metrics["telegram_failed"] += 1
            return False

if __name__ == "__main__":
    TgSenderService().start()
