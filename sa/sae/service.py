# -*- coding: utf-8 -*-
##----------------------------------------------------------------------
## SAE RPC Service
##----------------------------------------------------------------------
## Copyright (C) 2007-2015 The NOC Project
## See LICENSE for details
##----------------------------------------------------------------------

## Python modules
import logging
## Django modules
## NOC modules
from noc.sa.protocols.sae_pb2 import *
from noc.sa.models.activator import Activator
from noc.sa.rpc import (get_nonce, get_digest, PROTOCOL_NAME,
                        PROTOCOL_VERSION, PUBLIC_KEYS, CIPHERS, MACS,
                        COMPRESSIONS, KEY_EXCHANGES)
from noc.lib.ip import IP

logger = logging.getLogger(__name__)


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
        # Setting caps
        logging.debug("New activator in pool '%s': instance=%s, max_scripts=%d" % (
            request.name, request.instance, request.max_scripts))
        controller.stream.max_scripts = request.max_scripts
        controller.stream.current_scripts = 0
        controller.stream.instance = request.instance
        # Joining activator pool
        self.sae.join_activator_pool(request.name, controller.stream)
        # Sending response
        r = AuthResponse()
        controller.stream.is_authenticated = True
        controller.stream.pool_name = request.name
        done(controller, response=r)
