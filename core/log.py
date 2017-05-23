# -*- coding: utf-8 -*-
##----------------------------------------------------------------------
## Various logging utilities
##----------------------------------------------------------------------
## Copyright (C) 2007-2014 The NOC Project
## See LICENSE for details
##----------------------------------------------------------------------

## Python modules
import logging
import datetime


class PrefixLoggerAdapter(object):
    """
    Add [prefix] to log message
    """
    def __init__(self, logger, prefix, target=None):
        """
        :param logger: Parent logger
        :param prefix: Prefix to add in front of every message
        :param target: Optional file-like handle to duplicate output
        """
        self.logger = logger
        self.target = target
        self.prefix = None
        self.set_prefix(prefix)

    def set_prefix(self, prefix):
        if prefix:
            self.prefix = "[%s] " % str(prefix).replace("][", "|").replace("] [", "|")
        else:
            self.prefix = ""

    def _log(self, level, msg, args, **kwargs):
        self.logger._log(
            level,
            self.prefix + msg,
            args,
            **kwargs
        )
        if self.target:
            if args:
                msg = msg % args
            msg = "%s %s %s\n" % (
                datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S.%f"),
                self.prefix,
                msg
            )
            self.target.write(msg)

    def debug(self, msg, *args, **kwargs):
        if self.logger.isEnabledFor(logging.DEBUG):
            self._log(logging.DEBUG, msg, args, **kwargs)

    def info(self, msg, *args, **kwargs):
        if self.logger.isEnabledFor(logging.INFO):
            self._log(logging.INFO, msg, args, **kwargs)

    def warning(self, msg, *args, **kwargs):
        if self.logger.isEnabledFor(logging.WARNING):
            self._log(logging.WARNING, msg, args, **kwargs)

    def error(self, msg, *args, **kwargs):
        if self.logger.isEnabledFor(logging.ERROR):
            self._log(logging.ERROR, msg, args, **kwargs)

    def critical(self, msg, *args, **kwargs):
        if self.logger.isEnabledFor(logging.CRITICAL):
            self._log(logging.CRITICAL, msg, args, **kwargs)

    def exception(self, msg, *args, **kwargs):
        if self.logger.isEnabledFor(logging.ERROR):
            kwargs["exc_info"] = 1
            self._log(logging.ERROR, msg, args, **kwargs)

    def isEnabledFor(self, level):
        """
        See if the underlying logger is enabled for the specified level.
        """
        return self.logger.isEnabledFor(level)

    def get_logger(self, prefix):
        """
        Returns new logger adapter with additional prefix
        """
        return PrefixLoggerAdapter(
            self.logger,
            self.prefix[1:] + prefix,
            self.target
        )


class ColorFormatter(logging.Formatter):
    """
    Colored terminal formatter
    """
    DEFAULT_LOG_COLORS = {
        logging.DEBUG: 4,  # Blue
        logging.INFO: 2,  # Green
        logging.WARNING: 3,  # Yellow
        logging.ERROR: 1,  # Red
    }

    def __init__(self, *args, **kwargs):
        self._colors = {}
        self._end_color = ""
        self.setup_colors()
        logging.Formatter.__init__(self, *args, **kwargs)

    def format(self, record):
        def safe_unicode(s):
            try:
                return unicode(s)
            except UnicodeDecodeError:
                return repr(s)

        try:
            message = record.getMessage()
            assert isinstance(message, (str, unicode))
            record.message = safe_unicode(message)
        except Exception as e:
            record.message = "Bad message (%r): %r" % (e, record.__dict__)
        record.asctime = self.formatTime(record, self.datefmt)
        record.color = ""
        if record.levelno in self._colors:
            record.color = self._colors[record.levelno]
        record.endcolor = self._end_color
        formatted = self._fmt % record.__dict__
        return formatted.replace("\n", "\n    ")

    def setup_colors(self):
        """
        Set up terminal colors
        """
        import curses
        self._colors = {}
        fg_color = (curses.tigetstr("setaf") or
                    curses.tigetstr("setf") or
                    "")
        for level in self.DEFAULT_LOG_COLORS:
            self._colors[level] = unicode(
                curses.tparm(fg_color, self.DEFAULT_LOG_COLORS[level]),
                "ascii"
            )
        self._end_color = unicode(curses.tigetstr("sgr0"), "ascii")
