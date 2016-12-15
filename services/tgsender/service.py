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
import urllib
import urllib2
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

    def send_tb(self, messages, address, subject, body):
        RETRY_TIME = 2.0
        token = self.config.token
        proxy_addres = self.config.proxy_addres
        data = {'chat_id': address, 'text': '*'+subject+'*\n'+body,'parse_mode': 'Markdown'}
        time.sleep(RETRY_TIME)
        if self.config.use_proxy:
            try:
                proxy = urllib2.ProxyHandler({'https': proxy_addres})
                auth = urllib2.HTTPBasicAuthHandler()
                opener = urllib2.build_opener(proxy)
                urllib2.install_opener(opener)
                result = urllib2.urlopen("https://api.telegram.org/bot" + token + "/sendMessage",
                                         urllib.urlencode(data)).read()
                check = json.loads(result)
                self.logger.info("Proxy Send: %s\n" % check)
                metrics["telegram_proxy_sended_ok"] += 1
                return True
            except urllib2.HTTPError, e:
                self.logger.info("Proxy HTTPError: %s\n" % e.code)
                metrics["telegram_proxy_failed_httperror"] += 1
                return False
            except urllib2.URLError, e:
                self.logger.info("Proxy URLError: %s\n" % e.args)
                metrics["telegram_proxy_failed_urlerror"] += 1
                return False      
            except urllib2.HTTPException, e:
                self.logger.info("Proxy HTTPException: %s\n" % e.err)
                metrics["telegram_proxy_failed_urlerror"] += 1
                return False                         
            except Exception, e:
                self.logger.info("Proxy Generic Exception: %s\n" % e.exp)
                metrics["telegram_proxy_failed_exceprion"] += 1
                return False
        else:
            try:
                result = urllib2.urlopen("https://api.telegram.org/bot" + token + "/sendMessage",
                                         urllib.urlencode(data)).read()
                check = json.loads(result)
                self.logger.info("Send: %s\n" % check)
                metrics["telegram_sended_ok"] += 1
                return True
            except urllib2.HTTPError, e:
                self.logger.info("HTTPError: %s\n" % e.code)
                metrics["telegram_failed_httperror"] += 1
                return False
            except urllib2.URLError, e:
                self.logger.info("URLError: %s\n" % e.args)
                metrics["telegram_failed_urlerror"] += 1
                return False      
            except urllib2.HTTPException, e:
                self.logger.info("HTTPException: %s\n" % e.err)
                metrics["telegram_failed_urlerror"] += 1
                return False                         
            except Exception, e:
                self.logger.info("Generic Exception: %s\n" % e.exc)
                metrics["telegram_proxy_failed_exceprion"] += 1
                return False


if __name__ == "__main__":
    TgSenderService().start()
