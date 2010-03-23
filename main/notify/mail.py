# -*- coding: utf-8 -*-
##----------------------------------------------------------------------
##  SMTP Mail plugin
##----------------------------------------------------------------------
## Copyright (C) 2007-2009 The NOC Project
## See LICENSE for details
##----------------------------------------------------------------------
from noc.main.notify import Notify as NotifyBase
from noc.lib.validators import is_email
import smtplib,socket
from email.mime.text import MIMEText
from email.header import Header
import email.utils
##
##
##
class Notify(NotifyBase):
    name="mail"

    def send_message(self,params,subject,body,link=None):
        # Check params
        if not is_email(params):
            self.error("Invalid email: %s"%params)
            return True
        # Prepare message
        if link:
            body+="\n\nSee details: %s\n"%link
        from_address=self.config.get(self.name,"from_address")
        message=MIMEText(body,_charset="utf-8")
        message["From"]=from_address
        message["To"]=params
        message["Date"]=email.utils.formatdate()
        message["Subject"]=Header(subject,"utf-8")
        self.debug(message.as_string())
        # Connect to SMTP server
        smtp=smtplib.SMTP()
        self.debug("Connecting %s"%self.config.get(self.name,"smtp_server"))
        try:
            smtp.connect(self.config.get(self.name,"smtp_server"),self.config.getint(self.name,"smtp_port"))
        except socket.error,why:
            self.error("SMTP error: %s"%str(why))
            return False
        smtp.ehlo(self.config.get(self.name,"helo_hostname"))
        # Enforce TLS when required
        if self.config.getboolean(self.name,"use_tls"):
            smtp.starttls()
            smtp.ehlo(self.config.get(self.name,"helo_hostname"))
        # Authenticate when necessary
        smtp_user=self.config.get(self.name,"smtp_user")
        smtp_password=self.config.get(self.name,"smtp_password")
        if smtp_user and smtp_password:
            self.debug("Authenticating as %s"%smtp_user)
            try:
                smtp.login(smtp_user,smtp_password)
            except smtplib.SMTPAuthenticationError,why:
                self.error("SMTP Authentication error: %s"%str(why))
                return False
        # Send mail
        try:
            smtp.sendmail(from_address,[params],message.as_string())
        except smtplib.SMTPSenderRefused,why:
            self.error("Sender refused: %s"%str(why))
            return False
        #
        return True
