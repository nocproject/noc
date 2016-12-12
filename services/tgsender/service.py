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
import traceback
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
        data = {'chat_id': address, 'text': body}
        time.sleep(RETRY_TIME)
        try:
            result = urllib2.urlopen("https://api.telegram.org/bot" + token + "/sendMessage", urllib.urlencode(data)).read()
            check = json.loads(result)
            self.logger.info("Send: %s\n" % check)
            metrics["telegram_sended_ok"] += 1
            return True
        except urllib2.HTTPError, e:
            self.logger.info("HTTPError: %s\n" % e.code)
            metrics["telegram_failed_httperror"] += 1
            return False   
        except httplib.HTTPException, e:
            self.logger.info("HTTPException: %s\n" % e.code)
            metrics["telegram_failed_httpexceprion"] += 1
            return False  
        except Exception:
            self.logger.info("Generic Exception: %s\n" + traceback.format_exc())                   
            metrics["telegram_failed_exceprion"] += 1
            return False 
            
if __name__ == "__main__":
    TgSenderService().start()
