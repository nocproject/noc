# ----------------------------------------------------------------------
# Domain Expiration tools
# ----------------------------------------------------------------------
# Copyright (C) 2007-2019 The NOC Project
# See LICENSE for details
# ----------------------------------------------------------------------

# Python modules
import logging
import datetime

# NOC modules
from noc.config import config
from noc.core.ioloop.whois import whois
from noc.dns.models.dnszone import DNSZone, ZONE_FORWARD
from noc.main.models.systemnotification import SystemNotification
from noc.core.dateutils import humanize_timedelta

logger = logging.getLogger(__name__)


def update():
    """
    Update domains expiration
    :return:
    """
    for zone in DNSZone.objects.filter(type=ZONE_FORWARD):
        wdata = whois(zone.name, {"paid-till"})
        if not wdata or len(wdata) != 1:
            logger.info("[%s] Cannot check domain expiration", zone.name)
            continue
        ts = wdata[0][1]
        if "T" in ts:
            ts = ts.split("T", 1)[0]
        paid_till = datetime.datetime.strptime(ts, "%Y-%m-%d").date()
        if zone.paid_till == paid_till:
            continue
        logger.info("[%s] Changing expiry time: %s -> %s", zone.name, zone.paid_till, paid_till)
        zone.paid_till = paid_till
        zone.save()


def notify():
    """
    Notify domain expiration
    :return:
    """

    def get_table(data):
        # Format table
        max_w = max(len(z) for z, x in data)
        mask = "%%%d | %%s" % max_w
        return "\n".join(mask % (z, str(x)) for z, x in data)

    today = datetime.date.today()
    delta = datetime.timedelta(seconds=config.dns.warn_before_expired)
    shutoff = today + delta
    expiring = [
        (z.name, z.paid_till)
        for z in DNSZone.objects.filter(
            type=ZONE_FORWARD, paid_till__isnull=False, paid_till__lte=shutoff
        ).order_by("paid_till")
    ]
    if not expiring:
        return
    # Send notification
    h_delta = humanize_timedelta(delta)
    SystemNotification.notify(
        "dns.domain_expiration_warning",
        subject="%d domains to be expired in %d" % (len(expiring), h_delta),
        body="Following domains are to be expired in %d:\n%s\n" % (h_delta, get_table(expiring)),
    )
    # Get expired domains
    expired = [r for r in expiring if r[1] <= today]
    SystemNotification.notify(
        "dns.domain_expired",
        subject="%d domains are expiring" % len(expired),
        body="Following domains are expired:\n%s\n" % get_table(expired),
    )
