#!./bin/python
# -*- coding: utf-8 -*-
##----------------------------------------------------------------------
## noc-web daemon
##----------------------------------------------------------------------
## Copyright (C) 2007-2011 The NOC Project
## See LICENSE for details
##----------------------------------------------------------------------

if __name__ == "__main__":
    # Run Web server
    from noc.main.web import Web
    Web().process_command()
