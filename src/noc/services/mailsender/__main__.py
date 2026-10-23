# ----------------------------------------------------------------------
# mailsender service
# ----------------------------------------------------------------------
# Copyright (C) 2007-2026 The NOC Project
# See LICENSE for details
# ----------------------------------------------------------------------

from noc.services.mailsender.service import MailSenderService


if __name__ == "__main__":
    MailSenderService().start()
