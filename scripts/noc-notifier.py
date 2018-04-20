#!./bin/python
# -*- coding: utf-8 -*-
##----------------------------------------------------------------------
## noc-notifier daemon
##----------------------------------------------------------------------
## Copyright (C) 2007-2011 The NOC Project
## See LICENSE for details
##----------------------------------------------------------------------

if __name__ == "__main__":
    from noc.main.notifier.daemon import Notifier
    Notifier().process_command()
