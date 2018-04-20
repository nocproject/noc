# -*- coding: utf-8 -*-
##----------------------------------------------------------------------
##  File notification channel
##----------------------------------------------------------------------
## Copyright (C) 2007-2013 The NOC Project
## See LICENSE for details
##----------------------------------------------------------------------

## Python modules
import os
## NOC modules
from base import NotificationChannel


class FileNotificationChannel(NotificationChannel):
    """
    Message "subject" will be written to file.
    File path is passed as "params" agrument.
    Path must be relative path
    inside etc/noc-notifier.conf:[file]/prefix directory
    """
    name = "file"

    def send(self, to, subject, body, link=None):
        # Resolve file path
        prefix = self.config.get(self.name, "prefix")
        path = os.path.normpath(os.path.join(prefix, to))
        # Check path is inside "prefix" directory
        if os.path.commonprefix([prefix,
                                 path]) == prefix:
            d = os.path.dirname(path)
            # Create directory tree when necessary
            if not os.path.isdir(d):
                self.debug("Creating directory: %s" % d)
                os.makedirs(d)
            # Write message
            self.debug("Write '%s' to '%s'" % (subject, path))
            with open(path, "a+") as f:
                f.write(subject + "\n")
        else:
            self.error("Path '%s' is outside of '%s' directory. "
                       "Discarding message" % (path, prefix))
        return True
