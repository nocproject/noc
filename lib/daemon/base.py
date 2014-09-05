# -*- coding: utf-8 -*-
##----------------------------------------------------------------------
## System daemons base class
##----------------------------------------------------------------------
## Copyright (C) 2007-2011 The NOC Project
## See LICENSE for details
##----------------------------------------------------------------------

## Python modules
from __future__ import with_statement
import ConfigParser
import sys
import logging
import os
import signal
import optparse
import logging.handlers
## NOC modules
from noc.lib.debug import error_report, frame_report, set_crashinfo_context
from noc.lib.validators import is_ipv4, is_int
from noc.lib.version import get_version

# Load netifaces to resolve interface addresses when possible
try:
    import netifaces

    USE_NETIFACES = True
except ImportError:
    USE_NETIFACES = False


class Daemon(object):
    """
    Daemon base class
    """
    daemon_name = "daemon"
    defaults_config_path = "etc/%(daemon_name)s.defaults"
    config_path = "etc/%(daemon_name)s.conf"
    create_piddir = False
    # Initialize custom fields and solutions
    use_solutions = False

    LOG_FORMAT = "%(asctime)s [%(name)s] %(message)s"

    LOG_LEVELS = {
        "debug": logging.DEBUG,
        "info": logging.INFO,
        "warning": logging.WARNING,
        "error": logging.ERROR,
        "critical": logging.CRITICAL
    }

    def __init__(self):
        # Chdir to the root of project
        os.chdir(os.path.join(os.path.dirname(sys.argv[0]), ".."))
        self.prefix = os.getcwd()
        # Parse commandline
        self.opt_parser = optparse.OptionParser()
        self.opt_parser.add_option("-c", "--config", action="store",
                                   type="string", dest="config",
                                   help="Read config from CONFIG")
        self.opt_parser.add_option("-i", "--instance", action="store",
                                   type="string", dest="instance_id",
                                   default="0",
                                   help="Set instnace id")
        self.opt_parser.add_option("-f", "--foreground", action="store_false",
                                   dest="daemonize", default=True,
                                   help="Do not daemonize. "
                                        "Run at the foreground")
        self.opt_parser.add_option("-V", "--version", action="store_true",
                                   dest="show_version", default=False,
                                   help="Show daemon version")
        self.setup_opt_parser()
        self.options, self.args = self.opt_parser.parse_args()
        if self.options.show_version:
            print get_version()
            sys.exit(0)
        if len(self.args) < 1 or self.args[0] not in ["start", "launch",
                                                      "stop", "refresh",
                                                      "manifest"]:
            self.opt_parser.error(
                "You must supply one of start|launch|stop|refresh commands")
        # Read config
        self.pidfile = None
        self.config = None
        self.instance_id = self.options.instance_id
        self.load_config()
        # Register signal handlers if any
        for s in [s for s in dir(self) if s.startswith("SIG")]:
            try:
                sig = getattr(signal, s)
            except AttributeError:
                logging.error(
                    "Signal '%s' is not supported on this platform" % s)
                continue
            signal.signal(sig, getattr(self, s))
        #atexit.register(self.at_exit)
        if self.use_solutions:
            logging.info("Initializing solutions")
            from noc.lib.solutions import init_solutions
            init_solutions()

    def load_config(self):
        """
        Load and process configuration files
        :return:
        """
        first_run = True
        if self.config:
            logging.info("Loading config")
            first_run = False
        self.config = ConfigParser.SafeConfigParser()
        if self.defaults_config_path:
            self.config.read(
                self.defaults_config_path % {"daemon_name": self.daemon_name})
        if self.options.config:
            self.config.read(self.options.config)
        elif self.config_path:
            self.config.read(
                self.config_path % {"daemon_name": self.daemon_name})
        if not first_run:
            self.on_load_config()
        if self.config.get("main", "logfile"):
            set_crashinfo_context(self.daemon_name, os.path.dirname(
                self.config.get("main", "logfile").replace("{{instance}}",
                                                           self.instance_id)))
        else:
            set_crashinfo_context(None, None)
            # Set up logging
        if self.config.get("main", "loglevel") not in self.LOG_LEVELS:
            raise Exception(
                "Invalid loglevel '%s'" % self.config.get("main", "loglevel"))
        for h in logging.root.handlers:
            logging.root.removeHandler(h)  # Dirty hack for baseConfig
        self.heartbeat_enable = (self.options.daemonize and
                                 self.config.getboolean("main", "heartbeat"))
        if self.options.daemonize:
            # Set up logging
            logfile = self.config.get("main", "logfile")
            syslog_host = self.config.get("main", "syslog_host")
            if logfile or syslog_host:
                loglevel = self.LOG_LEVELS[self.config.get("main", "loglevel")]
                logging.root.setLevel(loglevel)
            if logfile:
                filename = logfile.replace(
                    "{{instance}}", self.instance_id)
                # Check permissions
                self.check_writable(filename)
                # Log to file
                rf_handler = logging.handlers.RotatingFileHandler(
                    filename=filename,
                    maxBytes=self.config.getint("main", "logsize"),
                    backupCount=self.config.getint("main", "logfiles")
                )
                # @todo: Configurable parameter
                rf_handler.setFormatter(
                    logging.Formatter(self.LOG_FORMAT, None))
                logging.root.addHandler(rf_handler)
            if syslog_host:
                # Log to remote host
                for host in syslog_host.split(","):
                    host = host.strip()
                    if not host:
                        continue
                    syslog_handler = logging.handlers.SysLogHandler(
                        address=(host, 514)
                    )
                    # @todo: Configurable parameter
                    syslog_handler.setFormatter(
                        logging.Formatter(self.LOG_FORMAT, None))
                    logging.root.addHandler(syslog_handler)
            self.pidfile = self.config.get("main", "pidfile").replace(
                "{{instance}}", self.instance_id)
            if self.pidfile and self.create_piddir:
                piddir = os.path.dirname(self.pidfile)
                if not os.path.exists(piddir):
                    try:
                        os.makedirs(piddir)
                        os.chmod(piddir, 01777)
                    except OSError, why:
                        self.die("Cannot create PIDfile directory %s: %s" % (
                            piddir, why))
                elif not os.path.isdir(piddir):
                    self.die("'%s' is not a directory" % piddir)
                elif not os.access(piddir, os.W_OK):
                    self.die("'%s' is not writable" % piddir)
            if self.pidfile:
                self.check_writable(self.pidfile)
        else:
            # Log to stdout
            handler = logging.StreamHandler(None)
            if self.is_stderr_supports_color():
                formatter = DaemonLogColorFormatter(
                    "%(color)s" + self.LOG_FORMAT + "%(endcolor)s",
                    None
                )
            else:
                formatter = logging.Formatter(self.LOG_FORMAT, None)
            handler.setFormatter(formatter)
            logging.root.addHandler(handler)
            logging.root.setLevel(logging.DEBUG)

    def die(self, msg):
        logging.error(msg)
        self.at_exit()
        os._exit(1)

    def check_writable(self, path):
        """
        Check file can be open as writable
        :return:
        """
        try:
            f = open(path, "a")
        except IOError, why:
            sys.stderr.write(str(why) + "\n")
            sys.stderr.write("Exiting\n")
            os._exit(1)

    def on_load_config(self):
        """
        Called after config has been reloaded on SIGHUP
        :return:
        """
        pass

    def run(self):
        """
        Main daemon loop. Must be overriden
        :return:
        """
        pass

    def become_daemon(self):
        """
        Daemonize process
        :return:
        """
        try:
            if os.fork():
                # Exit parent and return control to the shell immediately
                os._exit(0)
        except OSError, e:
            sys.stderr.write("Fork failed")
            sys.exit(1)
        os.setsid()  # Become session leader
        os.umask(022)
        try:
            pid = os.fork()
        except OSError, e:
            sys.stderr.write("Fork failed")
            os._exit(1)
        if pid:
            if self.pidfile:
                self.write_pidfile(pid)
            os._exit(0)
        # In daemon process, redirect stdin/stdout/stderr to /dev/null
        i = open("/dev/null", "r")
        o = open("/dev/null", "a+")
        e = open("/dev/null", "a+")
        os.dup2(i.fileno(), sys.stdin.fileno())
        os.dup2(o.fileno(), sys.stdout.fileno())
        os.dup2(e.fileno(), sys.stderr.fileno())
        sys.stdout = o
        sys.stderr = e

    def resolve_address(self, s):
        """
        Resolve interface names to IP addresses
        :param s: Interface name or IPv4 address
        :return:
        """
        if is_ipv4(s):
            return s
        if USE_NETIFACES:
            try:
                a = netifaces.ifaddresses(s)
            except ValueError:
                raise Exception("Invalid interface '%s'" % s)
            try:
                return a[2][0]["addr"]
            except (IndexError, KeyError):
                raise Exception("No ip address for interface: '%s' found" % s)
        raise Exception("Cannot resolve address '%s'" % s)

    def resolve_addresses(self, addr_list, default_port):
        """
        Parses string and returns a list of (ip,port)
        :param addr_list: Comma-separared list of addresses in form:
                          * ip
                          * ip:port
                          * interface
                          * interface:port
        :param default_port:
        :return:
        """
        r = []
        for x in addr_list.split(","):
            x = x.strip()
            if not x:
                continue
            if ":" in x:  # Implicit port notation
                x, port = x.split(":", 1)
                if is_int(port):
                    port = int(port)
                else:
                    import socket
                    try:
                        port = socket.getservbyname(port)
                    except socket.error:
                        raise Exception("Invalid port: %s" % port)
            else:
                port = int(default_port)
            if port <= 0 or port > 65535:
                raise Exception("Invalid port: %s" % port)
            if is_ipv4(x):
                r += [(x, port)]
                continue
            if USE_NETIFACES:  # Can resolve interface names
                try:
                    a = netifaces.ifaddresses(x)
                except ValueError:
                    raise Exception("Invalid interface '%s'" % x)
                try:
                    x = a[2][0]["addr"]
                except (IndexError, KeyError):
                    raise Exception(
                        "No ip address for interface: '%s' found" % x)
                r += [(x, port)]
                continue
            raise Exception("Cannot resolve address '%s'" % x)
        return r

    def write_pidfile(self, pid=None):
        """
        Write pidfile
        :return:
        """
        if not self.pidfile:
            return
        if pid is None:
            pid = os.getpid()  # Process' pid
        try:
            with open(self.pidfile, "w") as f:
                f.write(str(pid))
        except IOError, why:
            self.die("Unable to write PIDfile '%s': %s" % (self.pidfile,
                                                           why))

    def heartbeat(self):
        """
        Touch pidfile
        :return:
        """
        if self.pidfile and self.heartbeat_enable:
            logging.debug("Touching pidfile: %s" % self.pidfile)
            try:
                os.utime(self.pidfile, None)
            except OSError, why:
                logging.error("Unable to touch pidfile %s: %s" % (self.pidfile,
                                                                  why))

    def setup_opt_parser(self):
        """
        Add additional options to setup_opt_parser
        :return:
        """
        pass

    def process_command(self):
        """
        Process self.args[0] command
        :return:
        """
        getattr(self, self.args[0])()

    def guarded_run(self):
        """
        Run daemon and catch common exceptions
        :return:
        """
        try:
            self.run()
        except KeyboardInterrupt:
            pass
        except MemoryError:
            logging.error("Out of memory. Exiting.")
        except SystemExit:
            logging.info("Exiting")
        except:
            error_report()
        self.at_exit()

    def start(self):
        """
        "start" command handler
        :return:
        """
        # Daemonize
        if self.options.daemonize:
            self.become_daemon()
        self.guarded_run()

    def stop(self):
        """
        "stop" command handler
        :return:
        """
        pidfile = self.config.get("main", "pidfile")
        if os.path.exists(pidfile):
            with open(pidfile) as f:
                data = f.read().strip()
                if data:
                    pid = int(data)
                else:
                    pid = None
            if pid is not None:
                logging.info("Stopping %s pid=%s" % (self.daemon_name, pid))
                try:
                    os.kill(pid, signal.SIGTERM)
                except:
                    pass

    def launch(self):
        """
        "launch" command handler
        :return:
        """
        # Write pidfile
        self.write_pidfile()
        # Close stdin/stdout/stderr
        i = open("/dev/null", "r")
        o = open("/dev/null", "a+")
        e = open("/dev/null", "a+")
        os.dup2(i.fileno(), sys.stdin.fileno())
        os.dup2(o.fileno(), sys.stdout.fileno())
        os.dup2(e.fileno(), sys.stderr.fileno())
        sys.stdout = o
        sys.stderr = e
        self.guarded_run()

    def refresh(self):
        """
        "refresh" command handler
        :return:
        """
        self.stop()
        self.start()

    def manifest(self):
        import sys
        for name in [x for x in sys.modules if x.startswith("noc.")]:
            mod = sys.modules[name]
            if not mod:
                continue
            print mod

    def at_exit(self):
        if self.pidfile:
            try:
                logging.info("Removing pidfile: %s" % self.pidfile)
                os.unlink(self.pidfile)
            except OSError:
                pass
        logging.info("STOP")

    def is_stderr_supports_color(self):
        """
        Check stderr is TTY and supports color
        """
        try:
            import curses
        except ImportError:
            return False
        if hasattr(sys.stderr, "isatty") and sys.stderr.isatty():
            try:
                curses.setupterm()
                if curses.tigetnum("colors") > 0:
                    return True
            except Exception:
                pass
        return False

    def SIGUSR2(self, signo, frame):
        """
        Dump current execution frame trace on SIGUSR2
        :param signo:
        :param frame:
        :return:
        """
        frames = sys._current_frames().items()
        if len(frames) == 1:
            # Single thread
            frame_report(frame)
        else:
            # Multi-threaded
            import threading

            for tid, frame in frames:
                if tid in threading._active:
                    caption = "Thread: name=%s id=%s" % (
                    threading._active[tid].getName(), tid)
                else:
                    caption = "Unknown thread: id=%s" % tid
                frame_report(frame, caption)

    def SIGHUP(self, signo, frame):
        """
        Reload config on SIGHUP
        :param signo:
        :param frame:
        :return:
        """
        self.load_config()

    def SIGINT(self, signo, frame):
        """
        ^C processing
        :param signo:
        :param frame:
        :return:
        """
        logging.info("SIGINT received. Exiting")
        self.at_exit()
        os._exit(0)

    def SIGTERM(self, signo, frame):
        """
        SIGTERM processing
        :param signo:
        :param frame:
        :return:
        """
        logging.info("SIGTERM received. Exiting")
        self.at_exit()
        os._exit(0)


class DaemonLogColorFormatter(logging.Formatter):
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
        super(DaemonLogColorFormatter, self).__init__(*args, **kwargs)

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
