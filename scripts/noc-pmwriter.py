#!./bin/python
# -*- coding: utf-8 -*-
##----------------------------------------------------------------------
## noc-pmwriter daemon
##----------------------------------------------------------------------
## Copyright (C) 2007-2013 The NOC Project
## See LICENSE for details
##----------------------------------------------------------------------

if __name__ == "__main__":
    from noc.pm.pmwriter.daemon import PMWriterDaemon
    PMWriterDaemon().process_command()
