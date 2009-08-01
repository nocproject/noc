# -*- coding: utf-8 -*-
##----------------------------------------------------------------------
##  File plugin
##----------------------------------------------------------------------
## Copyright (C) 2007-2009 The NOC Project
## See LICENSE for details
##----------------------------------------------------------------------
from __future__ import with_statement
from noc.main.notify import Notify as NotifyBase
import os
##
## File plugin
## Message "subject" will be written to file.
## File path is passed as "params" agrument.
## Path must be relative path inside etc/noc-notifier.conf:[file]/prefix directory
##
class Notify(NotifyBase):
    name="file"

    def send_message(self,params,subject,body,link=None):
        # Resolve file path
        prefix=self.config.get(self.name,"prefix")
        path=os.path.normpath(os.path.join(prefix,params))
        if os.path.commonprefix([prefix,path])==prefix: # Check path is inside "prefix" directory
            d=os.path.dirname(path)
            if not os.path.isdir(d): # Create directory tree when necessary
                self.debug("Creating directory: %s"%d)
                os.makedirs(d)
            # Write message
            self.debug("Write '%s' to '%s'"%(subject,path))
            with open(path,"a+") as f:
                f.write(subject+"\n")
        else:
            self.error("Path '%s' is outside of '%s' directory. Discarding message"%(path,prefix))
        return True
