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


class PrefixLoggerAdapter(logging.LoggerAdapter):
    """
    Add [prefix] to log message
    """
    def __init__(self, logger, prefix, extra=None):
        self._pattern = None
        self.set_prefix(prefix)
        logging.LoggerAdapter.__init__(self, logger, extra or {})

    def process(self, msg, kwargs):
        return self._pattern % msg, kwargs

    def set_prefix(self, prefix):
        self._pattern = "[%s] %%s" % prefix
        self._pattern = self._pattern.replace("][", "|")


class TeeLoggerAdapter(logging.LoggerAdapter):
    """
    Duplicate log messages to the list
    """
    def __init__(self, logger, out, extra=None):
        self.out = out
        logging.LoggerAdapter.__init__(self, logger, extra or {})

    def _append(self, msg, args):
        if args:
            msg = msg % args
        msg = "%s %s" % (
            datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S.%f"),
            msg
        )
        self.out += [msg]

    def debug(self, msg, *args, **kwargs):
        self._append(msg, args)
        logging.LoggerAdapter.debug(self, msg, *args, **kwargs)

    def info(self, msg, *args, **kwargs):
        self._append(msg, args)
        logging.LoggerAdapter.info(self, msg, *args, **kwargs)

    def warning(self, msg, *args, **kwargs):
        self._append(msg, args)
        logging.LoggerAdapter.warning(self, msg, *args, **kwargs)

    def error(self, msg, *args, **kwargs):
        self._append(msg, args)
        logging.LoggerAdapter.error(self, msg, *args, **kwargs)

    def critical(self, msg, *args, **kwargs):
        self._append(msg, args)
        logging.LoggerAdapter.critical(self, msg, *args, **kwargs)

    def log(self, level, msg, *args, **kwargs):
        self._append(msg, args)
        logging.LoggerAdapter.log(self, msg, *args, **kwargs)

    def set_prefix(self, prefix):
        try:
            self.logger.set_prefix(prefix)
        except AttributeError:
            pass


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
