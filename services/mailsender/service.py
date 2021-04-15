#!./bin/python
# ----------------------------------------------------------------------
# mailsender service
# ----------------------------------------------------------------------
# Copyright (C) 2007-2020 The NOC Project
# See LICENSE for details
# ----------------------------------------------------------------------

# Python modules
import datetime
import smtplib
from email.mime.text import MIMEText
from email.mime.base import MIMEBase
from email.mime.multipart import MIMEMultipart
from email.mime.application import MIMEApplication
from email.header import Header

# Third-party modules
import pytz

# NOC modules
from noc.config import config
from noc.core.service.tornado import TornadoService
from noc.core.perf import metrics
from noc.core.comp import smart_text


class MailSenderService(TornadoService):
    name = "mailsender"

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.tz = None

    async def on_activate(self):
        self.tz = pytz.timezone(config.timezone)
        await self.subscribe(topic=self.name, channel="sender", handler=self.on_message)

    def on_message(self, message, address, subject, body, attachments=None, **kwargs):
        message_id = smart_text(message.id)
        self.logger.info(
            "[%s] Receiving message: %s (%s) [%s, attempt %d]",
            message_id,
            subject,
            address,
            datetime.datetime.fromtimestamp(message.timestamp / 1000000000.0),
            message.attempts,
        )
        return self.send_mail(message_id, address, subject, body, attachments)

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
        self.tz = pytz.timezone(config.timezone)
        now = datetime.datetime.now(self.tz)
        md = now.strftime("%a, %d %b %Y %H:%M:%S %z")
        if isinstance(address, str):
            address = [address]
        from_address = config.mailsender.from_address
        message = MIMEMultipart()
        message["From"] = from_address
        message["To"] = ", ".join(address)
        message["Date"] = md
        message["Subject"] = Header(subject, "utf-8")
        message.attach(MIMEText(body, _charset="utf-8"))
        for a in attachments:
            part = MIMEBase("application", "octet-stream")
            if "transfer-encoding" in a:
                part = MIMEApplication(a["data"])
            else:
                part.set_payload(a["data"].encode("utf-8"), charset="utf-8")
            part.add_header("Content-Disposition", "attachment", filename=a["filename"])
            message.attach(part)
        msg = message.as_string()
        self.logger.debug("Message: %s", msg)
        # Connect to SMTP server
        self.logger.debug(
            "[%s] Connecting %s:%s",
            message_id,
            config.mailsender.smtp_server,
            config.mailsender.smtp_port,
        )
        try:
            smtp = smtplib.SMTP(
                host=config.mailsender.smtp_server, port=config.mailsender.smtp_port
            )
        except OSError as e:
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
            self.logger.debug("[%s] Authenticating as %s", message_id, config.mailsender.smtp_user)
            try:
                smtp.login(config.mailsender.smtp_user, config.mailsender.smtp_password)
            except smtplib.SMTPAuthenticationError as e:
                self.logger.error("[%s] SMTP Authentication error: %s", message_id, e)
                metrics["smtp_response", ("code", e.smtp_code)] += 1
                return False
        # Send mail
        try:
            smtp.ehlo_or_helo_if_needed()
            esmtp_opts = []
            if smtp.does_esmtp:
                if smtp.has_extn("size"):
                    esmtp_opts.append("size=%d" % len(msg))
            # MAIL FROM
            code, resp = smtp.mail(from_address, esmtp_opts)
            if code != 250:
                smtp.rset()
                self.logger.error(
                    "[%s] MAIL FROM '%s' failed: %s %s", message_id, from_address, code, resp
                )
                metrics["smtp_response", ("code", code)] += 1
                return False
            # RCPT TO
            for addrs in address:
                code, resp = smtp.rcpt(addrs, [])
                if code not in (250, 251):
                    smtp.rset()
                    self.logger.error(
                        "[%s] RCPT TO '%s' failed: %s %s", message_id, addrs, code, resp
                    )
                    metrics["smtp_response", ("code", code)] += 1
                    return False
            # Data
            code, resp = smtp.data(msg)
            if code != 250:
                smtp.rset()
                self.logger.error("[%s] DATA failed: %s %s", message_id, code, resp)
                metrics["smtp_response", ("code", code)] += 1
                return False
            self.logger.info("[%s] Message sent: %s", message_id, resp)
            metrics["smtp_response", ("code", code)] += 1
        except smtplib.SMTPException as e:
            self.logger.error("[%s] SMTP Error: %s", message_id, e)
            smtp.rset()
            return False
        try:
            smtp.quit()
        except smtplib.SMTPException as e:
            self.logger.error("[%s] Failed to quit properly: %s", message_id, e)
        return True


if __name__ == "__main__":
    MailSenderService().start()
