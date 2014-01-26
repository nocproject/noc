# -*- coding: utf-8 -*-
##----------------------------------------------------------------------
## SNMP provider
##----------------------------------------------------------------------
## Copyright (C) 2007-2011 The NOC Project
## See LICENSE for details
##----------------------------------------------------------------------

## Python modules
from threading import Lock, Event
## Third-party modules
from pyasn1.codec.ber import encoder, decoder
from pysnmp.proto import api
## NOC modules
from noc.lib.nbsocket import UDPSocket, SocketTimeoutError
from noc.lib.debug import BQ


class SNMPProvider(object):
    TimeOutError = SocketTimeoutError

    def __init__(self, script):
        self.script = script
        self.access_profile = self.script.access_profile
        self.factory = script.activator.factory
        self.community_suffix = None
        self.to_save_output = self.script.activator.to_save_output

    def get(self, oid, community_suffix=None, cached=False):
        if self.script.activator.use_canned_session:
            r = self.script.activator.snmp_get(oid)
            if r is None:
                raise self.TimeOutError()
            return r
        cache = self.script.root.cmd_cache
        cached = cached or self.script.root.is_cached
        cc = "GET:" + oid
        if cached and cc in cache:
            return cache[cc]
        self.community_suffix = community_suffix
        s = SNMPGetSocket(self, oid)
        r = s.get_result().next()
        s.close()
        if self.to_save_output:
            self.script.activator.save_snmp_get(oid, r)
        if cached or self.script.root.is_cached:
            cache[cc] = r
        if r is None:
            raise self.TimeOutError()
        return r

    def getnext(self, oid, community_suffix=None, bulk=False, min_index=None,
                max_index=None, cached=False):
        """
        SNMP GETNEXT generator. Usage:
        for oid, v in self.getnext("<oid>"):
            ....
        """
        if self.script.activator.use_canned_session:
            r = self.script.activator.snmp_getnext(oid)
            if r is None:
                raise self.TimeOutError()
            for l in r:
                yield l
            raise StopIteration
        cache = self.script.root.cmd_cache
        cached = cached or self.script.root.is_cached
        cc = "GET:" + oid
        if cached and cc in cache:
            for r in cache[cc]:
                yield r
        out = []
        self.community_suffix = community_suffix
        sock = SNMPGetNextSocket(self, oid, bulk=bulk, min_index=min_index, max_index=max_index)
        for r in sock.get_result():
            if cached:
                try:
                    cache[cc] += [r]
                except KeyError:
                    cache[cc] = [r]
            if r is None:
                if self.script.activator.to_save_output:
                    self.script.activator.save_snmp_getnext(oid, None)
                raise self.TimeOutError()
            elif self.script.activator.to_save_output:
                out += [r]
            yield r
        if self.script.activator.to_save_output:
            self.script.activator.save_snmp_getnext(oid, out)

    def get_table(self, oid, community_suffix=None, bulk=False,
                  min_index=None, max_index=None, cached=False):
        """
        GETNEXT wrapper. Returns a hash of <index> -> <value>
        """
        r = {}
        for o, v in self.getnext(oid, community_suffix=community_suffix,
                                 bulk=bulk, min_index=min_index,
                                 max_index=max_index, cached=cached):
            r[int(o.split(".")[-1])] = v
        return r

    def join_tables(self, oid1, oid2, community_suffix=None, bulk=False,
                    min_index=None, max_index=None, cached=False):
        """
        Generator returning a rows of two snmp tables joined by index
        """
        t1 = self.get_table(oid1, community_suffix=community_suffix, bulk=bulk,
                            min_index=min_index, max_index=max_index,
                            cached=cached)
        t2 = self.get_table(oid2, community_suffix=community_suffix, bulk=bulk,
                            min_index=min_index, max_index=max_index,
                            cached=cached)
        for k1, v1 in t1.items():
            try:
                yield (v1, t2[k1])
            except KeyError:
                pass

    def get_tables(self, oids, community_suffix=None, bulk=False,
                      min_index=None, max_index=None, cached=False):
        """
        Query list of SNMP tables referenced by oids and yields
        tuples of (key, value1, ..., valueN)

        :param oids: List of OIDs
        :param community_suffix: Optional suffix to be added to community
        :param bulk: Use BULKGETNEXT if true
        :param min_index:
        :param max_index:
        :param cached:
        :return:
        """
        def gen_table(oid):
            l = len(oid) + 1
            for o, v in self.getnext(oid, community_suffix=community_suffix,
                                     bulk=bulk, min_index=min_index,
                                     max_index=max_index, cached=cached):
                yield tuple([int(x) for x in o[l:].split(".")]), v

        # Retrieve tables
        tables = [dict(gen_table(oid)) for oid in oids]
        # Generate index
        index = set()
        for t in tables:
            index.update(t)
        # Yield result
        for i in sorted(index):
            yield [".".join([str(x) for x in i])] + [t.get(i) for t in tables]

    def close(self):
        pass


class SNMPGetSocket(UDPSocket):
    TTL = 3

    def __init__(self, provider, oid):
        self.got_result = False
        self.provider = provider
        self.oid = oid
        self.address = self.provider.access_profile.address
        self.result = []
        self.event = Event()
        self.lock = Lock()
        super(SNMPGetSocket, self).__init__(provider.factory)

    def create_socket(self):
        super(SNMPGetSocket, self).create_socket()
        self.sendto(self.get_snmp_request(), (self.address, 161))

    def get_community(self):
        """Build full community, appending suffix when necessary"""
        c = self.provider.access_profile.snmp_ro
        if self.provider.community_suffix:
            c += self.provider.community_suffix
        return c

    def feed_result(self, r):
        with self.lock:
            self.result += [r]
            self.got_result = True
        self.event.set()

    def get_result(self):
        got_result = False
        while not self.closing:
            # Wait until data ready
            self.event.wait()
            # Copy collected data
            with self.lock:
                result, self.result = self.result, []
            # Yield result
            if result:
                got_result = True
                for r in result:
                    yield r
            self.event.clear()
        if not got_result:
             # Raise TimeOutError when closed without result
            yield None

    def oid_to_tuple(self, oid):
        """Convert oid from string to a list of integers"""
        return [int(x) for x in oid.split(".")]

    def get_snmp_request(self):
        """Returns string containing SNMP GET requests to self.oids"""
        self.provider.script.debug("%s SNMP GET %s" % (self.address, self.oid))
        p_mod = api.protoModules[api.protoVersion2c]
        req_PDU = p_mod.GetRequestPDU()
        p_mod.apiPDU.setDefaults(req_PDU)
        p_mod.apiPDU.setVarBinds(req_PDU, [(self.oid_to_tuple(self.oid), p_mod.Null())])
        req_msg = p_mod.Message()
        p_mod.apiMessage.setDefaults(req_msg)
        p_mod.apiMessage.setCommunity(req_msg, self.get_community())
        p_mod.apiMessage.setPDU(req_msg, req_PDU)
        self.req_PDU = req_PDU
        return encoder.encode(req_msg)

    def on_read(self, data, address, port):
        """
        Read and parse reply. Calls set_data for all returned values
        :param data: Incoming data
        :param address: UDP packet source address
        :param port: UDP packet source port
        :return:
        """
        p_mod = api.protoModules[api.protoVersion2c]
        while data:
            rsp_msg, data = decoder.decode(data, asn1Spec=p_mod.Message())
            rsp_pdu = p_mod.apiMessage.getPDU(rsp_msg)
            if p_mod.apiPDU.getRequestID(self.req_PDU) == p_mod.apiPDU.getRequestID(rsp_pdu):
                errorStatus = p_mod.apiPDU.getErrorStatus(rsp_pdu)
                if errorStatus:
                    self.provider.script.error("%s SNMP GET ERROR: %s" % (self.address, errorStatus.prettyPrint()))
                    break
                else:
                    for oid, val in p_mod.apiPDU.getVarBinds(rsp_pdu):
                        self.provider.script.debug('%s SNMP GET REPLY: %s %s' % (
                            self.address, oid.prettyPrint(),
                            BQ(val.prettyPrint())))
                        self.feed_result(str(val))
                        break
        self.close()

    def on_close(self):
        super(SNMPGetSocket, self).on_close()
        self.event.set()


class SNMPGetNextSocket(SNMPGetSocket):
    TTL = 5

    def __init__(self, provider, oid, bulk=False, min_index=None, max_index=None):
        self.bulk = bulk
        self.min_index = min_index
        self.max_index = max_index
        super(SNMPGetNextSocket, self).__init__(provider, oid)

    def get_snmp_request(self):
        """Returns string containing SNMP GET requests to self.oids"""
        self.provider.script.debug(
            "%s SNMP %s %s" % (self.address, "GETBULK" if self.bulk else "GETNEXT", str(self.oid)))
        p_mod = api.protoModules[api.protoVersion2c]
        req_PDU = p_mod.GetBulkRequestPDU() if self.bulk else p_mod.GetNextRequestPDU()
        self.api_pdu = p_mod.apiBulkPDU if self.bulk else p_mod.apiPDU
        self.api_pdu.setDefaults(req_PDU)
        if self.bulk:
            self.api_pdu.setNonRepeaters(req_PDU, 0)   # @todo: Configurable?
            self.api_pdu.setMaxRepetitions(req_PDU, 20)  # @todo: Configurable?
        self.api_pdu.setVarBinds(req_PDU, [(p_mod.ObjectIdentifier(self.oid_to_tuple(self.oid)), p_mod.Null())])
        req_msg = p_mod.Message()
        p_mod.apiMessage.setDefaults(req_msg)
        p_mod.apiMessage.setCommunity(req_msg, self.get_community())
        p_mod.apiMessage.setPDU(req_msg, req_PDU)
        self.req_PDU = req_PDU
        self.req_msg = req_msg
        return encoder.encode(req_msg)

    def on_read(self, data, address, port):
        self.update_status()
        p_mod = api.protoModules[api.protoVersion2c]
        while data:
            self.provider.script.debug("SNMP PDU RECEIVED")
            rsp_msg, data = decoder.decode(data, asn1Spec=p_mod.Message())
            rsp_pdu = p_mod.apiMessage.getPDU(rsp_msg)
            # Match response to request
            if self.api_pdu.getRequestID(self.req_PDU) == p_mod.apiPDU.getRequestID(rsp_pdu):
                # Check for SNMP errors reported
                errorStatus = self.api_pdu.getErrorStatus(rsp_pdu)
                if errorStatus and errorStatus != 2:
                    raise errorStatus
                    # Format var-binds table
                var_bind_table = self.api_pdu.getVarBindTable(self.req_PDU, rsp_pdu)
                # Report SNMP table
                for table_row in var_bind_table:
                    for name, val in table_row:
                        if val is None:
                            continue
                        oid = name.prettyPrint()
                        if not oid.startswith(self.oid):
                            self.close()
                            return
                            # Check index range if given
                        if self.min_index is not None or self.max_index is not None:
                            index = int(oid.split(".")[-1])
                            if self.min_index is not None and index < self.min_index:
                                # Skip values below min_index
                                continue
                            if self.max_index and index > self.max_index:
                                # Finish processing
                                self.close()
                                return
                        if self.bulk:
                            self.provider.script.debug("SNMP BULK DATA: %s %s" % (oid, BQ(val.prettyPrint())))
                        else:
                            self.provider.script.debug(
                                '%s SNMP GETNEXT REPLY: %s %s' % (self.address, oid, BQ(val.prettyPrint())))
                        self.feed_result((oid, str(val)))
                # Stop on EOM
                for oid, val in var_bind_table[-1]:
                    if val is not None:
                        break
                    else:
                        self.close()
                        return
                self.api_pdu.setVarBinds(self.req_PDU, map(lambda (x, y), n=p_mod.Null(): (x, n), var_bind_table[-1]))
                self.api_pdu.setRequestID(self.req_PDU, p_mod.getNextRequestID())
                self.sendto(encoder.encode(self.req_msg), (self.address, 161))
