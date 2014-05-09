# -*- coding: utf-8 -*-
##----------------------------------------------------------------------
## SAE RPC Service
##----------------------------------------------------------------------
## Copyright (C) 2007-2011 The NOC Project
## See LICENSE for details
##----------------------------------------------------------------------

## Python modules
import logging
import datetime
## NOC modules
from noc.sa.protocols.sae_pb2 import *
from noc.sa.models import Activator, ManagedObject
from noc.fm.models import IgnoreEventRules
from noc.sa.rpc import (get_nonce, get_digest, PROTOCOL_NAME,
                        PROTOCOL_VERSION, PUBLIC_KEYS, CIPHERS, MACS,
                        COMPRESSIONS, KEY_EXCHANGES)
from noc.lib.ip import IP


class Service(SAEService):
    """
    SAE RPC Service handler
    """
    def get_controller_activator(self, controller):
        """
        Get activator for given controller

        :param controller: Controller
        :type controller: Controller
        :return: Activator instance
        :rtype: Activator
        """
        return Activator.objects.get(name=controller.stream.pool_name)

    def get_activator(self, controller, name, done):
        """
        Get activator and check it is enabled
        """
        # Get activator
        try:
            activator = Activator.objects.get(name=name)
        except Activator.DoesNotExist:
            msg = "Unknown activator '%s'" % name
            logging.error(msg)
            done(controller, error=Error(code=ERR_UNKNOWN_ACTIVATOR,
                                         text=msg))
            return None
        # Check shard is match
        if activator.shard.name not in self.sae.shards:
            msg = "Shard mismatch for '%s'. '%s' is not in %s" % (
                        name, activator.shard.name, self.sae.shards)
            logging.error(msg)
            done(controller, error=Error(code=ERR_INVALID_SHARD,
                                         text=msg))
            return None
        # Check shard is active
        if not activator.shard.is_active:
            msg = "Shard is down: '%s'" % activator.shard.name
            logging.error(msg)
            done(controller, error=Error(code=ERR_SHARD_IS_DOWN,
                                         text=msg))
            return None
        return activator

    ##
    ## RPC interfaces
    ##
    def protocol(self, controller, request, done):
        """
        Protocol negotiation
        """
        if (request.protocol != PROTOCOL_NAME or
            request.version != PROTOCOL_VERSION):
            done(controller,
                 error=Error(code=ERR_PROTO_MISMATCH,
                             text="Protocol version mismatch"))
        else:
            done(controller,
                 response=ProtocolResponse(protocol=PROTOCOL_NAME,
                                           version=PROTOCOL_VERSION))
    
    def setup(self, controller, request, done):
        def first_match(iter1, iter2):
            for i in iter1:
                for j in iter2:
                    if i == j:
                        return i
            return "none"
        
        # Check whether encryption is disabled
        r_addr = IP.prefix(controller.stream.socket.getpeername()[0])
        force_plaintext = False
        for p in self.sae.force_plaintext:
            if p.contains(r_addr):
                force_plaintext = True
                break
        
        if force_plaintext:
            logging.info("Forcing plaintext transmission")
            kex = pk = cipher = mac = compression = "none"
        else:
            # Negotiate key exchange algorithm
            kex = first_match(KEY_EXCHANGES, request.key_exchanges)
            # Negotiate public key
            pk = first_match(PUBLIC_KEYS, request.public_keys)
            # Negotiate cipher
            cipher = first_match(CIPHERS, request.ciphers)
            # Negotiate mac
            mac = first_match(MACS, request.macs)
            # Negotiate compression
            compression = first_match(COMPRESSIONS, request.compressions)
            
            if kex == "none" or pk == "none" or cipher == "none" or mac == "none":
                done(
                    controller,
                    error=Error(error=ERR_SETUP_FAILED,
                                text="Cannot negotiate crypto algorithm"))
                return
            controller.stream.set_next_transform(kex, pk, cipher, mac, compression)
        done(
            controller,
            response=SetupResponse(key_exchange= kex, public_key=pk,
                                   cipher=cipher, mac=mac,
                                   compression=compression))

    def kex(self, controller, request, done):
        r = controller.stream.get_kex_response(request)
        if isinstance(r, Error):
            done(controller, error=r)
        else:
            done(controller, response=r)
            controller.stream.activate_next_transform()

    def ping(self, controller, request, done):
        """
        Handle RPC ping request.
        """
        done(controller, response=PingResponse())

    def register(self, controller, request, done):
        """
        Handle RPC register request
        """
        # Get activator
        activator = self.get_activator(controller, request.name, done)
        if not activator:
            return
        # Requesting digest
        logging.info("Requesting digest for activator '%s'" % request.name)
        r = RegisterResponse()
        r.nonce = get_nonce()
        controller.stream.nonce = r.nonce
        done(controller, response=r)

    def auth(self, controller, request, done):
        """
        Handle RPC auth request
        """
        # Get activator
        activator = self.get_activator(controller, request.name, done)
        if not activator:
            return
        # Authenticating
        logging.info("Authenticating activator '%s'" % request.name)
        if (controller.stream.nonce is None or
            get_digest(request.name, activator.auth, controller.stream.nonce) != request.digest):
            done(controller,
                 error=Error(code=ERR_AUTH_FAILED,
                 text="Authencication failed for activator '%s'" % request.name))
            return
        # Joining activator pool
        self.sae.join_activator_pool(request.name, controller.stream)
        # Setting caps
        logging.debug("Set capabilities: instance=%s, max_scripts=%d, can_ping=%s" % (
            request.instance, request.max_scripts, request.can_ping))
        controller.stream.max_scripts = request.max_scripts
        controller.stream.current_scripts = 0
        controller.stream.instance = request.instance
        controller.stream.can_ping = request.can_ping
        self.sae.update_activator_capabilities(controller.stream.pool_name)
        # Sending response
        r = AuthResponse()
        controller.stream.is_authenticated = True
        controller.stream.pool_name = request.name
        done(controller, response=r)

    def object_mappings(self, controller, request, done):
        """
        Handle RPC event_filter request
        """
        if not controller.stream.is_authenticated:
            done(controller,
                 error=Error(code=ERR_AUTH_REQUIRED,
                             text="Authentication required"))
            return
        activator = self.get_controller_activator(controller)
        r = ObjectMappingsResponse()
        r.expire = self.sae.config.getint("sae", "refresh_event_filter")
        # Build source filter
        for c in ManagedObject.objects.filter(activator=activator,
                    trap_source_ip__isnull=False, collector__isnull=True).only("id", "trap_source_ip"):
            if c.profile_name.startswith("NOC."):
                continue
            s = r.mappings.add()
            s.source = c.trap_source_ip
            s.object = str(c.id)
        # Ping settings
        for c in ManagedObject.objects.filter(activator=activator,
            trap_source_ip__isnull=False,
            object_profile__enable_ping=True,
            object_profile__ping_interval__gt=0
        ).only("trap_source_ip", "object_profile__ping_interval").select_related():
            if c.profile_name.startswith("NOC."):
                continue
            p = r.ping.add()
            p.address = c.trap_source_ip
            p.interval = c.object_profile.ping_interval
        # Build event filter
        for ir in IgnoreEventRules.objects.filter(is_active=True):
            i = r.ignore_rules.add()
            i.left_re = ir.left_re
            i.right_re = ir.right_re
        done(controller, response=r)

    def event(self, controller, request, done):
        """
        Handle RPC event request
        """
        if not controller.stream.is_authenticated:
            e = Error()
            e.code = ERR_AUTH_REQUIRED
            e.text = "Authentication required"
            done(controller, error=e)
            return
        # activator = self.get_controller_activator(controller)
        # Resolve managed object by request's IP
        # @todo: Speed optimization
        if request.object:
            mo = self.sae.map_object(request.object)
            if not mo:
                done(controller,
                     error=Error(code=ERR_UNKNOWN_EVENT_SOURCE,
                                 text="Unknown object '%s'" % request.object))
                return
        else:
            mo = None
        # Write event to database
        self.sae.write_event(
            data=[(b.key, b.value) for b in request.body],
            timestamp=datetime.datetime.fromtimestamp(request.timestamp),
            managed_object=mo
        )
        done(controller, EventResponse())

    def object_status(self, controller, request, done):
        """
        Handle RPC object_status request
        :param controller:
        :param request:
        :param done:
        :return:
        """
        if not controller.stream.is_authenticated:
            done(controller, error=Error(code=ERR_AUTH_REQUIRED,
                                         text="Authentication required"))
            return
        for s in request.status:
            try:
                mo = ManagedObject.objects.get(id=int(s.object))
            except ManagedObject.DoesNotExist:
                pass
            self.sae.object_status[mo.id] = s.status
            mo.set_status(s.status)
            # Save event to database
            result = "success" if s.status else "failed"
            self.sae.write_event(
               data=[("source", "system"),
                     ("activator", controller.stream.pool_name),
                     ("probe", "ping"),
                     ("ip", mo.address),
                     ("result", result)],
               managed_object=mo,
               timestamp=datetime.datetime.now())
