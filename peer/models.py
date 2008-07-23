from django.db import models
from noc.ip.models import VRF

class PeeringPoint(models.Model):
    hostname
    type

class Peer(models.Model):
    peering_point
    local_asn
    local_ip
    remote_asn
    remote_ip
    vrf
    remote_vpn
    import_filter
    export_filter
    contact
    tt
