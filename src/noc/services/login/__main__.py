# ----------------------------------------------------------------------
# Login service
# ----------------------------------------------------------------------
# Copyright (C) 2007-2026 The NOC Project
# See LICENSE for details
# ----------------------------------------------------------------------

# NOC modules
from noc.services.login.service import LoginService

if __name__ == "__main__":
    LoginService().start()
