#!./bin/python
# -*- coding: utf-8 -*-
##----------------------------------------------------------------------
## mailsender service
##----------------------------------------------------------------------
## Copyright (C) 2007-2016 The NOC Project
## See LICENSE for details
##----------------------------------------------------------------------

## Python modules
import datetime
import smtplib
import socket
from email.mime.text import MIMEText
from email.header import Header
## Third-party modules
import pytz
## NOC modules
from noc.core.service.base import Service


class MailSenderService(Service):
    name = "mailsender"

    def __init__(self, *args, **kwargs):
        super(MailSenderService, self).__init__(*args, **kwargs)
        self.tz = pytz.timezone(self.config.timezone)

    def on_activate(self):
        self.subscribe(
            topic=self.name,
            channel="sender",
            handler=self.on_message
        )

    def on_message(self, message, address, subject, body, **kwargs):
        self.logger.info(
            "[%s] Sending message: %s (%s) [%s, attempt %d]",
            message.id, subject, address,
            datetime.datetime.fromtimestamp(message.timestamp),
            message.attempts
        )
        return self.send_mail(address, subject, body)

    def send_mail(self, address, subject, body):
        """
        Send mail message
        :param address: Mail address
        :param subject: Mail subject
        :param body: mail body
        :returns: sending status as boolean
        """
        now = datetime.datetime.now(self.TZ)
        md = now.strftime("%a, %d %b %Y %H:%M:%S %z")
        from_address = self.config.from_address
        message = MIMEText(body, _charset="utf-8")
        message["From"] = from_address
        message["To"] = address
        message["Date"] = md
        message["Subject"] = Header(subject, "utf-8")
        msg = message.as_string()
        self.logger.debug("Message: %s", msg)
        # Connect to SMTP server
        smtp = smtplib.SMTP()
        self.logger.debug(
            "Connecting %s:%s",
            self.config.smtp_server, self.config.smtp_port
        )
        try:
            smtp.connect(self.config.smtp_server, self.config.smtp_port)
        except socket.error as e:
            self.logger.error("SMTP error: %s", e)
            return False
        smtp.ehlo(self.config.helo_hostname)
        # Enforce TLS when required
        if self.config.use_tls:
            try:
                smtp.starttls()
            except smtplib.SMTPException as e:
                self.logger.error("STARTTLS failed: %s", e)
                return False
            smtp.ehlo(self.config.helo_hostname)
        # Authenticate when necessary
        if self.config.smtp_user and self.config.smtp_password:
            self.logger.debug("Authenticating as %s",
                              self.config.smtp_user)
            try:
                smtp.login(
                    self.config.smtp_user,
                    self.config.smtp_password
                )
            except smtplib.SMTPAuthenticationError as e:
                self.logger.error("SMTP Authentication error: %s", e)
                return False
            # Send mail
        try:
            self.logger.debug("Sending")
            smtp.sendmail(from_address, [address], msg)
        except smtplib.SMTPSenderRefused as e:
            self.logger.error("Sender refused: %s", e)
            return False
        except smtplib.SMTPServerDisconnected as e:
            self.logger.error("Server disconnected: %s", e)
            return False
        except smtplib.SMTPDataError as e:
            self.logger.error("Data error: %s", e)
            return False
        self.logger.debug("Sent")


if __name__ == "__main__":
    MailSenderService().start()
