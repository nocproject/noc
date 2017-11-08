#!./bin/python
# -*- coding: utf-8 -*-
# ----------------------------------------------------------------------
# mailsender service
# ----------------------------------------------------------------------
# Copyright (C) 2007-2017 The NOC Project
# See LICENSE for details
# ----------------------------------------------------------------------

# Python modules
import datetime
import smtplib
import socket
from email.header import Header
from email.mime.base import MIMEBase
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText

# Third-party modules
import pytz
# NOC modules
from noc.config import config
from noc.core.service.base import Service


class MailSenderService(Service):
    name = "mailsender"

    def __init__(self, *args, **kwargs):
        super(MailSenderService, self).__init__(*args, **kwargs)
        self.tz = None

    def on_activate(self):
        self.tz = pytz.timezone(config.timezone)
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
        return self.send_mail(message.id, address, subject, body, attachments)

    def send_mail(self, message_id, address, subject, body, attachments=None):
        """
        Send mail message
        :param message_id: NSQ Message id
        :param address: Mail address
        :param subject: Mail subject
        :param body: mail body
        :param attachments: List of dict with filename and data keys
        :returns: sending status as boolean
        """
        attachments = attachments or []
        now = datetime.datetime.now(self.tz)
        md = now.strftime("%a, %d %b %Y %H:%M:%S %z")
        from_address = config.mailsender.from_address
        message = MIMEMultipart()
        message["From"] = from_address
        message["To"] = address
        message["Date"] = md
        message["Subject"] = Header(subject, "utf-8")
        message.attach(
            MIMEText(body, _charset="utf-8")
        )
        for a in attachments:
            part = MIMEBase("application", "octet-stream")
            part.set_payload(a["data"])
            part.add_header(
                "Content-Disposition",
                "attachment",
                filename=a["filename"]
            )
            message.attach(part)
        msg = message.as_string()
        self.logger.debug("Message: %s", msg)
        # Connect to SMTP server
        smtp = smtplib.SMTP()
        self.logger.debug(
            "[%s] Connecting %s:%s",
            message_id,
            config.mailsender.smtp_server, config.mailsender.smtp_port
        )
        try:
            smtp.connect(config.mailsender.smtp_server,
                         config.mailsender.smtp_port)
        except socket.error as e:
            self.logger.error("[%s] SMTP error: %s", message_id, e)
            return False
        smtp.ehlo(config.mailsender.helo_hostname)
        # Enforce TLS when required
        if config.mailsender.use_tls:
            try:
                smtp.starttls()
            except smtplib.SMTPException as e:
                self.logger.error("[%s] STARTTLS failed: %s", message_id, e)
                return False
            smtp.ehlo(config.mailsender.helo_hostname)
        # Authenticate when necessary
        if config.mailsender.smtp_user and config.mailsender.smtp_password:
            self.logger.debug(
                "[%s] Authenticating as %s",
                message_id,
                config.mailsender.smtp_user
            )
            try:
                smtp.login(
                    config.mailsender.smtp_user,
                    config.mailsender.smtp_password
                )
            except smtplib.SMTPAuthenticationError as e:
                self.logger.error(
                    "[%s] SMTP Authentication error: %s",
                    message_id, e
                )
                self.perf_metrics["smtp_response_%d" % e.smtp_code] += 1
                return False
        # Send mail
        try:
            smtp.ehlo_or_helo_if_needed()
            esmtp_opts = []
            if smtp.does_esmtp:
                if smtp.has_extn('size'):
                    esmtp_opts.append("size=%d" % len(msg))
            # MAIL FROM
            code, resp = smtp.mail(from_address, esmtp_opts)
            if code != 250:
                smtp.rset()
                self.logger.error("[%s] MAIL FROM '%s' failed: %s %s",
                                  message_id, from_address, code, resp)
                self.perf_metrics["smtp_response_%d" % code] += 1
                return False
            # RCPT TO
            code, resp = smtp.rcpt(address, [])
            if code not in (250, 251):
                smtp.rset()
                self.logger.error("[%s] RCPT TO '%s' failed: %s %s",
                                  message_id, address, code, resp)
                self.perf_metrics["smtp_response_%d" % code] += 1
                return False
            # Data
            code, resp = smtp.data(msg)
            if code != 250:
                smtp.rset()
                self.logger.error("[%s] DATA failed: %s %s",
                                  message_id, code, resp)
                self.perf_metrics["smtp_response_%d" % code] += 1
                return False
            self.logger.info("[%s] Message sent: %s", message_id, resp)
            self.perf_metrics["smtp_response_%d" % code] += 1
        except smtplib.SMTPException as e:
            self.logger.error("[%s] SMTP Error: %s", message_id, e)
            smtp.rset()
            return False
        try:
            smtp.quit()
        except smtplib.SMTPException as e:
            self.logger.error(
                "[%s] Failed to quit properly: %s",
                message_id, e
            )
        return True


if __name__ == "__main__":
    MailSenderService().start()
