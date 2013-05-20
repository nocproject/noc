#!./bin/python
# -*- coding: utf-8 -*-
##----------------------------------------------------------------------
## noc-activator daemon
##----------------------------------------------------------------------
## Copyright (C) 2007-2011 The NOC Project
## See LICENSE for details
##----------------------------------------------------------------------

if __name__ == "__main__":
    # Run activator
    from noc.sa.activator import Activator
    Activator().process_command()
