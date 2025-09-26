#!./bin/python
# ----------------------------------------------------------------------
# mailsender service
# ----------------------------------------------------------------------
# Copyright (C) 2007-2022 The NOC Project
# See LICENSE for details
# ----------------------------------------------------------------------

# Python modules
from typing import Dict, Any, Optional
import orjson
import datetime
import smtplib
from email.mime.text import MIMEText
from email.mime.base import MIMEBase
from email.mime.multipart import MIMEMultipart
from email.mime.application import MIMEApplication
from email.header import Header


# NOC modules
from noc.core.service.fastapi import FastAPIService
from noc.core.msgstream.message import Message
from noc.core.mx import MX_TO
from noc.core.perf import metrics
from noc.config import config
from noc.core.comp import DEFAULT_ENCODING

MAILSENDER_STREAM = "mailsender"


class MailSenderService(FastAPIService):
    name = "mailsender"
    use_telemetry = True

    async def on_activate(self):
        self.slot_number, self.total_slots = await self.acquire_slot()
        await self.subscribe_stream(MAILSENDER_STREAM, self.slot_number, self.on_message)

    async def on_message(self, msg: Message) -> None:
        """
        Process incoming message. Usually forwarded by `mx` service.
        Message MUST have `To` header, containing target Mail topic.

        :param msg:
        :return:
        """
        metrics["messages"] += 1
        self.logger.debug("[%d] Receiving message %s", msg.offset, msg.headers)
        dst = msg.headers.get(MX_TO)
        if not dst:
            self.logger.debug("[%d] Missed '%s' header. Dropping", msg.offset, MX_TO)
            metrics["messages_drops"] += 1
            return None
        metrics["messages_processed"] += 1
        return self.send_mail(
            msg.offset, orjson.loads(msg.value), dst.decode(encoding=DEFAULT_ENCODING)
        )

    def send_mail(
        self, message_id: int, data: Dict[str, Any], address_to: Optional[str] = None
    ) -> None:
        attachments = data.get("attachments", [])
        now = datetime.datetime.now(config.timezone)
        md = now.strftime("%a, %d %b %Y %H:%M:%S %z")
        if "address" in data:
            address = [data["address"]]
        elif address_to:
            address = [address_to]
        else:
            self.logger.warning("[%s] Message without address", message_id)
            return None
        from_address = config.mailsender.from_address
        message = MIMEMultipart()
        message["From"] = from_address
        message["To"] = ", ".join(address)
        message["Date"] = md
        message["Subject"] = Header(data["subject"], "utf-8")
        message.attach(MIMEText(data["body"], _charset="utf-8"))
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
