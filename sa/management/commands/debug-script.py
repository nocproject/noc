# -*- coding: utf-8 -*-
##----------------------------------------------------------------------
## Usage: debug-script <script> <object> [ <args> ]
##----------------------------------------------------------------------
## Copyright (C) 2007-2011 The NOC Project
## See LICENSE for details
##----------------------------------------------------------------------

## Python modules
from __future__ import with_statement
import logging
import sys
import ConfigParser
import Queue
import cPickle
import threading
import signal
import os
import datetime
import pprint
from optparse import OptionParser, make_option
## Django modules
from django.core.management.base import BaseCommand, CommandError
## NOC modules
from noc.sa.profiles import profile_registry
from noc.sa.script import script_registry, Script
from noc.sa.script.ssh.keys import Key
from noc.sa.activator import Service, ServersHub
from noc.sa.protocols.sae_pb2 import *
from noc.sa.rpc import TransactionFactory
from noc.lib.url import URL
from noc.lib.nbsocket import SocketFactory, UDPSocket
from noc.lib.validators import is_int
from noc.lib.fileutils import read_file
from noc.lib.test.beeftestcase import BeefTestCase


class Controller(object):
    pass


class SessionCan(object):
    """Canned beef output"""
    def __init__(self, script_name, input=None, private=False):
        self.cli = {}  # Command -> result
        self.input = input or {}
        self.result = None
        self.motd = ""
        self.script_name = script_name
        self.snmp_get = {}
        self.snmp_getnext = {}
        self.http_get = {}
        self.platform = None
        self.version = None
        self.private = private

    def set_version(self, platform, version):
        self.platform = platform
        self.version = version

    def save_interaction(self, provider, cmd, data):
        """Store data"""
        if provider == "cli":
            self.cli[cmd] = data

    def save_snmp_get(self, oid, result):
        self.snmp_get[oid] = result

    def save_snmp_getnext(self, oid, result):
        self.snmp_getnext[oid] = result

    def save_http_get(self, path,result):
        self.http_get[path] = result

    def save_result(self, result, motd=""):
        """Save final result"""
        self.result = result
        self.motd = motd

    def dump(self, output):
        """Dump canned data"""
        vendor, profile, script = self.script_name.split(".")
        return BeefTestCase().save_beef(output, script=self.script_name,
            vendor=vendor, platform=self.platform, version=self.version,
            input=self.input, result=self.result,
            cli=self.cli, snmp_get=self.snmp_get,
            snmp_getnext=self.snmp_getnext, http_get=self.http_get,
            motd=self.motd, private=self.private
        )


class ActivatorStubFactory(SocketFactory):
    def unregister_socket(self, socket):
        super(ActivatorStubFactory, self).unregister_socket(socket)
        if isinstance(socket, UDPSocket):
            # Reset activator watchdog on UDP socket closing
            self.controller.reset_wait_ticks()


class ActivatorStub(object):
    """
    Activator emulation
    """
    WAIT_TICKS = 4

    def __init__(self, script_name, values=[], output=None, private=False):
        # Simple config stub
        self.config = ConfigParser.SafeConfigParser()
        self.config.read("etc/noc-activator.defaults")
        self.config.read("etc/noc-activator.conf")
        self.script_call_queue = Queue.Queue()
        self.ping_check_results = None
        self.factory = ActivatorStubFactory(tick_callback=self.tick,
                                            controller=self)
        self.servers = ServersHub(self)
        self.log_cli_sessions = None
        self.wait_ticks = self.WAIT_TICKS
        self.to_save_output = output is not None
        self.output = output
        self.use_canned_session = False
        self.scripts = []
        if self.to_save_output:
            self.script_name = script_name
            args = {}
            for k, v in values:
                args[k] = cPickle.loads(v)
            self.session_can = SessionCan(self.script_name, args, private)
        # SSH keys
        self.ssh_public_key = None
        self.ssh_private_key = None
        self.load_ssh_keys()

    def load_ssh_keys(self):
        """Initialize ssh keys"""
        private_path = self.config.get("ssh", "key")
        public_path = private_path + ".pub"
        # Load keys
        logging.debug("Loading private ssh key from '%s'" % private_path)
        s_priv = read_file(private_path)
        logging.debug("Loading public ssh key from '%s'" % public_path)
        s_pub = read_file(public_path)
        # Check all keys presend
        if s_priv is None or s_pub is None:
            self.error("Cannot find ssh keys. Generate one by './noc generate-ssh-keys' command")
            os._exit(1)
        self.ssh_public_key = Key.from_string(s_pub)
        self.ssh_private_key = Key.from_string_private_noc(s_priv)

    def reset_wait_ticks(self):
        logging.debug("Resetting wait ticks")
        self.wait_ticks = self.WAIT_TICKS

    def tick(self):
        logging.debug("Tick")
        while not self.script_call_queue.empty():
            try:
                f, args, kwargs = self.script_call_queue.get_nowait()
            except:
                break
            logging.debug("Calling delayed %s(*%s, **%s)" % (f, args, kwargs))
            apply(f, args, kwargs)
        if not self.factory.sockets:
            self.wait_ticks -= 1
            if not self.wait_ticks:
                logging.debug("EXIT")
                if self.to_save_output:
                    p = self.session_can.dump(self.output)
                    logging.debug("Writing session test to %s" % p)
                # Finally dump results
                for s in self.scripts:
                    if s.result:
                        # Format output
                        r = cPickle.loads(s.result)
                        if isinstance(r, basestring):
                            r = unicode(str(r), "utf8")
                        else:
                            r = pprint.pformat(r)
                        logging.debug(u"SCRIPT RESULT: %s\n%s" % (s.debug_name, r))
                self.factory.shutdown()
            logging.debug("%d TICKS TO EXIT" % self.wait_ticks)
        else:
            # Sockets left
            self.reset_wait_ticks()

    def on_script_exit(self, script):
        if self.to_save_output:
            get_version = ".".join(script.name.split(".")[:-1]) + ".get_version"
            if get_version in script.call_cache:
                v = script.call_cache[get_version]["{}"]
                self.session_can.set_version(v["platform"], v["version"])
            elif script.name == get_version:
                v = cPickle.loads(script.result)
                self.session_can.set_version(v["platform"], v["version"])
        if script.parent is None:
            self.servers.close()

    def run_script(self, object_name, _script_name, access_profile, callback, timeout=0, **kwargs):
        pv, pos, sn = _script_name.split(".", 2)
        profile = profile_registry["%s.%s" % (pv, pos)]()
        script = script_registry[_script_name](profile, self, object_name, access_profile, **kwargs)
        self.scripts += [script]
        if self.to_save_output:
            platform = None
            version = None
            for a in access_profile.attrs:
                if a.key == "platform":
                    platform = a.value
                elif a.key == "version":
                    version = a.value
            if platform and version:
                self.session_can.set_version(platform, version)
        script.start()

    def request_call(self, f, *args, **kwargs):
        logging.debug("Requesting call: %s(*%s, **%s)" % (f, args, kwargs))
        self.script_call_queue.put((f, args, kwargs))

    def can_run_script(self):
        return True

    def save_interaction(self, provider, cmd, data):
        """Handler to accept canned input"""
        self.session_can.save_interaction(provider, cmd, data)

    def save_result(self, result, motd=""):
        """Handler to save final result"""
        self.session_can.save_result(result, motd)

    def save_snmp_get(self, oid, result):
        self.session_can.save_snmp_get(oid, result)

    def save_snmp_getnext(self, oid, result):
        self.session_can.save_snmp_getnext(oid, result)

    def save_http_get(self, path, result):
        self.session_can.save_http_get(path, result)

    def error(self, msg):
        logging.error(msg)


class Command(BaseCommand):
    """
    debug-script handler
    """
    help = "Debug SA Script"
    option_list = BaseCommand.option_list + (
        make_option("-c", "--read-community", dest="snmp_ro"),
        make_option("-o", "--output", dest="output"),
        make_option("-p", "--profile", dest="profile", action="store_true"),
        make_option("-P", "--private", action="store_true", dest="private")
        )

    def SIGINT(self, signo, frame):
        """Gentler SIGINT handler"""
        logging.info("SIGINT")
        os._exit(0)

    def _usage(self):
        """
        Print usage and exit
        @todo: Must be a gentler way
        """
        print "USAGE:"
        print "%s debug-script [-c <community>] [-o <output>] <script> <obj1> [ .. <objN>] [<key1>=<value1> [ .. <keyN>=<valueN>]]" % sys.argv[0]
        print "Where:"
        print "\t-c <community> - SNMP RO Community"
        print "\t-o <output>    - Canned beef output"
        print "\t--private      - Mark canned beef as private"
        print "\t--profile      - Run through python profiler"
        return

    def set_access_profile_url(self, access_profile, obj, profile, snmp_ro_community):
        """Create access profile from URL string"""
        if profile is None:
            raise CommandError("Script name must contain profile when using URLs")
        url = URL(obj)
        access_profile.profile = profile
        access_profile.scheme = Script.get_scheme_id(url.scheme)
        access_profile.address = url.host
        if url.port:
            access_profile.port = url.port
        access_profile.user = url.user
        if "\x00" in url.password:
            # Check the password really the pair of password/enable password
            p, s = url.password.split("\x00", 1)
            access_profile.password = p
            access_profile.super_password = s
        else:
            access_profile.password = url.password
        access_profile.path = url.path
        if snmp_ro_community:
            access_profile.snmp_ro = snmp_ro_community

    def set_access_profile_name(self, access_profile, obj, profile, snmp_ro_community):
        """Create access profile from database object"""
        from noc.sa.models import ManagedObject
        from django.db.models import Q

        # Prepare query
        if is_int(obj):
            q = Q(id=int(obj)) | Q(name=obj)  # Integers can be object id or name
        else:
            q = Q(name=obj)  # Search by name otherwise
        # Get object from database
        try:
            o = ManagedObject.objects.get(q)
        except ManagedObject.DoesNotExist:
            raise CommandError("Object not found: %s" % obj)
        # Fill access profile
        credentials = o.credentials
        access_profile.profile = o.profile_name
        access_profile.scheme = o.scheme
        access_profile.address = o.address
        if o.port:
            access_profile.port = o.port
        access_profile.user = credentials.user
        access_profile.password = credentials.password
        if credentials.super_password:
            access_profile.super_password = credentials.super_password
        if snmp_ro_community:
            if snmp_ro_community != "-":
                access_profile.snmp_ro = snmp_ro_community
            elif credentials.snmp_ro:
                access_profile.snmp_ro = credentials.snmp_ro
        if o.remote_path:
            access_profile.path = o.remote_path
        attrs = [(a.key, a.value) for a in o.managedobjectattribute_set.all()]
        for k, v in attrs:
            a = access_profile.attrs.add()
            a.key = str(k)
            a.value = v

    def get_request(self, script, obj, snmp_ro_community, values):
        """Prepare script request"""
        profile = None
        r = ScriptRequest()
        r.object_name = obj
        # Normalize script name
        if "." in script:
            vendor, os_name, script = script.split(".", 2)
            profile = "%s.%s" % (vendor, os_name)
            # Fill access profile and script name
        if "://" in obj:
            # URL
            self.set_access_profile_url(r.access_profile, obj, profile, snmp_ro_community)
            r.script = "%s.%s" % (profile, script)
        else:
            # Database name or id
            self.set_access_profile_name(r.access_profile, obj, profile, snmp_ro_community)
            if profile and r.access_profile.profile != profile:
                raise CommandError("Profile mismatch for '%s'" % obj)
            r.script = "%s.%s" % (r.access_profile.profile, script)
            ## Fill values
        for k, v in values:
            a = r.kwargs.add()
            a.key = k
            a.value = v
        return r

    def expand_selectors(self, objects):
        """Expand names starting with "selector:"""
        if [o for o in objects if o.startswith("selector:")]:
            # Has selectors
            from noc.sa.models import ManagedObjectSelector

            r = set()
            for o in objects:
                if o.startswith("selector:"):
                    o = o[9:]
                    try:
                        s = ManagedObjectSelector.objects.get(name=o)
                    except ManagedObjectSelector.DoesNotExist:
                        raise CommandError("Selector not found: %s" % o)
                    r |= set([mo.name for mo in s.managed_objects])
                else:
                    r.add(o)
            return list(r)
        else:
            # No selectors. Nothing to expand
            return objects

    def run_script(self, service, request):
        def handle_callback(controller, response=None, error=None):
            if error:
                logging.debug("Error: %s" % error.text)
            if response:
                logging.debug("Script completed")
                logging.debug(response.config)

        logging.debug("Running script thread")
        controller = Controller()
        controller.transaction = self.tf.begin()
        service.script(controller=controller, request=request, done=handle_callback)

    def handle(self, *args, **options):
        """Process debug-script command"""
        if len(args) < 2:
            return self._usage()
        script_name = args[0]
        objects = []
        values = []
        # Parse args
        for a in args[1:]:
            if "=" in a:
                # key=value
                k, v = a.split("=", 1)
                v = cPickle.dumps(eval(v, {}, {}))
                values += [(k, v)]
            else:
                # object
                objects += [a]
        # Canned beef for only one object
        output = options.get("output", None)
        if output and len(objects) != 1:
            raise CommandError("Can write canned beef for one object only")
        # Get SNMP community
        snmp_ro_community = None
        if options["snmp_ro"]:
            snmp_ro_community = options["snmp_ro"]
        # Prepare requests
        objects = self.expand_selectors(objects)
        requests = [self.get_request(script_name, obj, snmp_ro_community, values) for obj in objects]
        # Set up logging and signal handlers
        logging.root.setLevel(logging.DEBUG)
        signal.signal(signal.SIGINT, self.SIGINT)
        ## Prepare activator stub
        self.tf = TransactionFactory()
        service = Service()
        service.activator = ActivatorStub(
            requests[0].script if output else None, values, output,
            bool(options.get("private")))

        ## Run scripts
        def run():
            for r in requests:
                print r
                t = threading.Thread(target=self.run_script, args=(service, r))
                t.start()
                # Finally give control to activator's factory
            service.activator.factory.run(run_forever=True)

        if options.get("profile", True):
            logging.debug("Enabling python profiler")
            import cProfile

            cProfile.runctx("run()", globals(), locals())
        else:
            run()
