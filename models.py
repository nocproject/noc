## -*- coding: utf-8 -*-
##----------------------------------------------------------------------
## NOC models lazy loading and utilities
##----------------------------------------------------------------------
## Copyright (C) 2007-2015 The NOC Project
## See LICENSE for details
##----------------------------------------------------------------------

## Python modules
import logging


logger = logging.getLogger(__name__)


def get_model_id(object):
    """
    Returns model id for instance object
    """
    if isinstance(object._meta, dict):
        # Document
        return u"%s.%s" % (object.__module__.split(".")[1],
                           object.__class__.__name__)
    else:
        # Model
        return u"%s.%s" % (object._meta.app_label,
                           object._meta.object_name)


def get_model(model_id):
    """
    Returns model/document class for given model id
    """
    m = _MCACHE.get(model_id)
    if not m:
        assert model_id in _MODELS, "Invalid model id: %s" % model_id
        logger.debug("Loading model %s", model_id)
        mp = _MODELS[model_id]
        mod_name, cls_name = mp.rsplit(".", 1)
        mod = __import__(mod_name, {}, {}, [cls_name])
        m = getattr(mod, cls_name)
        _MCACHE[model_id] = m
    return m


def get_object(model_id, object_id):
    """
    Return an object instance or None
    """
    m = get_model(model_id)
    try:
        return m.objects.get(id=object_id)
    except m.DoesNotExist:
        return None


def load_models():
    for alias in _MODELS:
        get_model(alias)


## Model cache: model_id -> class
_MCACHE = {}

_MODELS = {
    # main models
    "main.AuditTrail": "noc.main.models.audittrail.AuditTrail",
    "main.Checkpoint": "noc.main.models.Checkpoint",
    "main.CollectionCache": "noc.main.models.collectioncache.CollectionCache",
    "main.CustomField": "noc.main.models.customfield.CustomField",
    "main.CustomFieldEnumGroup": "noc.main.models.customfieldenumgroup.CustomFieldEnumGroup",
    "main.CustomFieldEnumValue": "noc.main.models.customfieldenumvalue.CustomFieldEnumValue",
    "main.DBTrigger": "noc.main.models.dbtrigger.DBTrigger",
    "main.DatabaseStorage": "noc.main.models.DatabaseStorage",
    "main.DocCategory": "noc.main.models.doccategory.DocCategory",
    "main.FTSQueue": "noc.main.models.fts_queue.FTSQueue",
    "main.Favorites": "noc.main.models.favorites.Favorites",
    "main.Language": "noc.main.models.language.Language",
    "main.MIMEType": "noc.main.models.MIMEType",
    "main.Notification": "noc.main.models.notification.Notification",
    "main.NotificationGroup": "noc.main.models.notificationgroup.NotificationGroup",
    "main.NotificationGroupOther": "noc.main.models.notificationgroup.NotificationGroupOther",
    "main.NotificationGroupUser": "noc.main.models.notificationgroup.NotificationGroupUser",
    "main.Permission": "noc.main.models.permission.Permission",
    "main.Pool": "noc.main.models.pool.Pool",
    "main.PrefixTable": "noc.main.models.prefixtable.PrefixTable",
    "main.PyRule": "noc.main.models.pyrule.PyRule",
    "main.RefBook": "noc.main.models.RefBook",
    "main.RefBookData": "noc.main.models.RefBookData",
    "main.RefBookField": "noc.main.models.RefBookField",
    "main.ResourceState": "noc.main.models.resourcestate.ResourceState",
    "main.Schedule": "noc.main.models.Schedule",
    "main.Shard": "noc.main.models.Shard",
    "main.SlowOp": "noc.main.models.slowop.SlowOp",
    "main.Style": "noc.main.models.style.Style",
    "main.Sync": "noc.main.models.sync.Sync",
    "main.SyncCache": "noc.main.models.synccache.SyncCache",
    "main.SystemNotification": "noc.main.models.SystemNotification",
    "main.SystemTemplate": "noc.main.models.SystemTemplate",
    "main.Tag": "noc.main.models.tag.Tag",
    "main.Template": "noc.main.models.Template",
    "main.TimePattern": "noc.main.models.timepattern.TimePattern",
    "main.TimePatternTerm": "noc.main.models.timepatternterm.TimePatternTerm",
    "main.UserProfile": "noc.main.models.userprofile.UserProfile",
    "main.UserProfileContact": "noc.main.models.userprofilecontact.UserProfileContact",
    "main.UserSession": "noc.main.models.UserSession",
    "main.UserState": "noc.main.models.UserState",
    # project models
    "project.Project": "noc.project.models.project.Project",
    # gis models
    "gis.Address": "noc.gis.models.address.Address",
    "gis.Area": "noc.gis.models.Area",
    "gis.Building": "noc.gis.models.building.Building",
    "gis.Division": "noc.gis.models.division.Division",
    "gis.FontSet": "noc.gis.models.FontSet",
    "gis.GeoData": "noc.gis.models.geodata.GeoData",
    "gis.Layer": "noc.gis.models.layer.Layer",
    "gis.LayerUserSettings": "noc.gis.models.layerusersettings.LayerUserSettings",
    "gis.Map": "noc.gis.models.Map",
    "gis.Overlay": "noc.gis.models.Overlay",
    "gis.Street": "noc.gis.models.street.Street",
    "gis.Style": "noc.gis.models.Style",
    "gis.TileCache": "noc.gis.models.TileCache",
    "gis._Layer": "noc.gis.models._Layer",
    # inv models
    "inv.Capability": "noc.inv.models.capability.Capability",
    "inv.ConnectionRule": "noc.inv.models.connectionrule.ConnectionRule",
    "inv.ConnectionType": "noc.inv.models.connectiontype.ConnectionType",
    "inv.Coverage": "noc.inv.models.coverage.Coverage",
    "inv.CoveredBuilding": "noc.inv.models.coveredbuilding.CoveredBuilding",
    "inv.CoveredObject": "noc.inv.models.coveredobject.CoveredObject",
    "inv.DiscoveryJob": "noc.inv.models.discoveryjob.DiscoveryJob",
    "inv.ForwardingInstance": "noc.inv.models.forwardinginstance.ForwardingInstance",
    "inv.Interface": "noc.inv.models.interface.Interface",
    "inv.InterfaceClassificationRule": "noc.inv.models.interfaceclassificationrule.InterfaceClassificationRule",
    "inv.InterfaceProfile": "noc.inv.models.interfaceprofile.InterfaceProfile",
    "inv.Link": "noc.inv.models.link.Link",
    "inv.MACDB": "noc.inv.models.macdb.MACDB",
    "inv.MACLog": "noc.inv.models.maclog.MACLog",
    "inv.MapSettings": "noc.inv.models.mapsettings.MapSettings",
    "inv.ModelConnectionsCache": "noc.inv.models.objectmodel.ModelConnectionsCache",
    "inv.ModelInterface": "noc.inv.models.modelinterface.ModelInterface",
    "inv.ModelMapping": "noc.inv.models.modelmapping.ModelMapping",
    "inv.NetworkSegment": "noc.inv.models.networksegment.NetworkSegment",
    "inv.NewAddressDiscoveryLog": "noc.inv.models.newaddressdiscoverylog.NewAddressDiscoveryLog",
    "inv.NewPrefixDiscoveryLog": "noc.inv.models.newprefixdiscoverylog.NewPrefixDiscoveryLog",
    "inv.Object": "noc.inv.models.object.Object",
    "inv.ObjectConnection": "noc.inv.models.objectconnection.ObjectConnection",
    "inv.ObjectFile": "noc.inv.models.objectfile.ObjectFile",
    "inv.ObjectLog": "noc.inv.models.objectlog.ObjectLog",
    "inv.ObjectModel": "noc.inv.models.objectmodel.ObjectModel",
    "inv.PendingLinkCheck": "noc.inv.models.pendinglinkcheck.PendingLinkCheck",
    "inv.SubInterface": "noc.inv.models.subinterface.SubInterface",
    "inv.Technology": "noc.inv.models.technology.Technology",
    "inv.UnknownModel": "noc.inv.models.unknownmodel.UnknownModel",
    "inv.Vendor": "noc.inv.models.vendor.Vendor",
    # sa models
    "sa.Activator": "noc.sa.models.activator.Activator",
    "sa.AdministrativeDomain": "noc.sa.models.administrativedomain.AdministrativeDomain",
    "sa.AuthProfile": "noc.sa.models.authprofile.AuthProfile",
    "sa.Collector": "noc.sa.models.collector.Collector",
    "sa.FailedScriptLog": "noc.sa.models.failedscriptlog.FailedScriptLog",
    "sa.GroupAccess": "noc.sa.models.groupaccess.GroupAccess",
    "sa.InteractionLog": "noc.sa.models.interactionlog.InteractionLog",
    "sa.MRTConfig": "noc.sa.models.mrtconfig.MRTConfig",
    "sa.ManagedObject": "noc.sa.models.managedobject.ManagedObject",
    "sa.ManagedObjectAttribute": "noc.sa.models.managedobject.ManagedObjectAttribute",
    "sa.ManagedObjectProfile": "noc.sa.models.managedobjectprofile.ManagedObjectProfile",
    "sa.ManagedObjectSelector": "noc.sa.models.managedobjectselector.ManagedObjectSelector",
    "sa.ManagedObjectSelectorByAttribute": "noc.sa.models.managedobjectselector.ManagedObjectSelectorByAttribute",
    "sa.MapTask": "noc.sa.models.maptask.MapTask",
    "sa.ObjectNotification": "noc.sa.models.objectnotification.ObjectNotification",
    "sa.ReduceTask": "noc.sa.models.reducetask.ReduceTask",
    "sa.TerminationGroup": "noc.sa.models.terminationgroup.TerminationGroup",
    "sa.UserAccess": "noc.sa.models.useraccess.UserAccess",
    # fm models
    "fm.ActiveAlarm": "noc.fm.models.activealarm.ActiveAlarm",
    "fm.ActiveEvent": "noc.fm.models.activeevent.ActiveEvent",
    "fm.AlarmClass": "noc.fm.models.alarmclass.AlarmClass",
    "fm.AlarmClassCategory": "noc.fm.models.alarmclasscategory.AlarmClassCategory",
    "fm.AlarmClassConfig": "noc.fm.models.alarmclassconfig.AlarmClassConfig",
    "fm.AlarmSeverity": "noc.fm.models.alarmseverity.AlarmSeverity",
    "fm.AlarmTrigger": "noc.fm.models.AlarmTrigger",
    "fm.ArchivedAlarm": "noc.fm.models.archivedalarm.ArchivedAlarm",
    "fm.ArchivedEvent": "noc.fm.models.archivedevent.ArchivedEvent",
    "fm.CloneClassificationRule": "noc.fm.models.cloneclassificationrule.CloneClassificationRule",
    "fm.Enumeration": "noc.fm.models.enumeration.Enumeration",
    "fm.EventClass": "noc.fm.models.eventclass.EventClass",
    "fm.EventClassCategory": "noc.fm.models.eventclass.EventClassCategory",
    "fm.EventClassificationRule": "noc.fm.models.eventclassificationrule.EventClassificationRule",
    "fm.EventClassificationRuleCategory": "noc.fm.models.eventclassificationrule.EventClassificationRuleCategory",
    "fm.EventTrigger": "noc.fm.models.EventTrigger",
    "fm.FailedEvent": "noc.fm.models.failedevent.FailedEvent",
    "fm.IgnoreEventRules": "noc.fm.models.IgnoreEventRules",
    "fm.IgnorePattern": "noc.fm.models.ignorepattern.IgnorePattern",
    "fm.MIB": "noc.fm.models.mib.MIB",
    "fm.MIBAlias": "noc.fm.models.mibalias.MIBAlias",
    "fm.MIBData": "noc.fm.models.mibdata.MIBData",
    "fm.MIBPreference": "noc.fm.models.mibpreference.MIBPreference",
    "fm.NewEvent": "noc.fm.models.newevent.NewEvent",
    "fm.OIDAlias": "noc.fm.models.oidalias.OIDAlias",
    "fm.Outage": "noc.fm.models.outage.Outage",
    "fm.Reboot": "noc.fm.models.reboot.Reboot",
    "fm.SyntaxAlias": "noc.fm.models.syntaxalias.SyntaxAlias",
    # pm models
    "pm.GrafanaDashboard": "noc.pm.models.grafanadashboard.GrafanaDashboard",
    "pm.Metric": "noc.pm.models.metric.Metric",
    "pm.MetricConfig": "noc.pm.models.metricconfig.MetricConfig",
    "pm.MetricSet": "noc.pm.models.metricset.MetricSet",
    "pm.MetricSettings": "noc.pm.models.metricsettings.MetricSettings",
    "pm.MetricType": "noc.pm.models.metrictype.MetricType",
    "pm.ProbeConfig": "noc.pm.models.probeconfig.ProbeConfig",
    # cm models
    "cm.ErrorType": "noc.cm.models.errortype.ErrorType",
    "cm.ObjectFact": "noc.cm.models.objectfact.ObjectFact",
    "cm.ObjectNotify": "noc.cm.models.objectnotify.ObjectNotify",
    "cm.PrefixList": "noc.cm.models.prefixlist.PrefixList",
    "cm.RPSL": "noc.cm.models.rpsl.RPSL",
    "cm.ValidationPolicy": "noc.cm.models.validationpolicy.ValidationPolicy",
    "cm.ValidationPolicySettings": "noc.cm.models.validationpolicysettings.ValidationPolicySettings",
    "cm.ValidationRule": "noc.cm.models.validationrule.ValidationRule",
    # ip models
    "ip.Address": "noc.ip.models.address.Address",
    "ip.AddressRange": "noc.ip.models.addressrange.AddressRange",
    "ip.IPPool": "noc.ip.models.ippool.IPPool",
    "ip.Prefix": "noc.ip.models.prefix.Prefix",
    "ip.PrefixAccess": "noc.ip.models.prefixaccess.PrefixAccess",
    "ip.PrefixBookmark": "noc.ip.models.prefixbookmark.PrefixBookmark",
    "ip.VRF": "noc.ip.models.vrf.VRF",
    "ip.VRFGroup": "noc.ip.models.vrfgroup.VRFGroup",
    # vc models
    "vc.VC": "noc.vc.models.vc.VC",
    "vc.VCBindFilter": "noc.vc.models.vcbindfilter.VCBindFilter",
    "vc.VCDomain": "noc.vc.models.vcdomain.VCDomain",
    "vc.VCDomainProvisioningConfig": "noc.vc.models.vcdomainprovisioningconfig.VCDomainProvisioningConfig",
    "vc.VCFilter": "noc.vc.models.vcfilter.VCFilter",
    "vc.VCType": "noc.vc.models.vctype.VCType",
    # dns models
    "dns.DNSServer": "noc.dns.models.dnsserver.DNSServer",
    "dns.DNSZone": "noc.dns.models.dnszone.DNSZone",
    "dns.DNSZoneProfile": "noc.dns.models.dnszoneprofile.DNSZoneProfile",
    "dns.DNSZoneRecord": "noc.dns.models.dnszonerecord.DNSZoneRecord",
    # peer models
    "peer.AS": "noc.peer.models.asn.AS",
    "peer.ASSet": "noc.peer.models.asset.ASSet",
    "peer.Community": "noc.peer.models.Community",
    "peer.CommunityType": "noc.peer.models.CommunityType",
    "peer.Maintainer": "noc.peer.models.maintainer.Maintainer",
    "peer.Organisation": "noc.peer.models.organisation.Organisation",
    "peer.Peer": "noc.peer.models.peer.Peer",
    "peer.PeerGroup": "noc.peer.models.peergroup.PeerGroup",
    "peer.PeeringPoint": "noc.peer.models.peeringpoint.PeeringPoint",
    "peer.Person": "noc.peer.models.person.Person",
    "peer.PrefixListCache": "noc.peer.models.prefixlistcache.PrefixListCache",
    "peer.RIR": "noc.peer.models.rir.RIR",
    "peer.WhoisASSetMembers": "noc.peer.models.whoisassetmembers.WhoisASSetMembers",
    "peer.WhoisOriginRoute": "noc.peer.models.whoisoriginroute.WhoisOriginRoute",
    # kb models
    "kb.KBEntry": "noc.kb.models.KBEntry",
    "kb.KBEntryAttachment": "noc.kb.models.KBEntryAttachment",
    "kb.KBEntryHistory": "noc.kb.models.KBEntryHistory",
    "kb.KBEntryPreviewLog": "noc.kb.models.KBEntryPreviewLog",
    "kb.KBEntryTemplate": "noc.kb.models.KBEntryTemplate",
    "kb.KBGlobalBookmark": "noc.kb.models.KBGlobalBookmark",
    "kb.KBUserBookmark": "noc.kb.models.KBUserBookmark",
    # support models
    "support.Crashinfo": "noc.support.models.crashinfo.Crashinfo"
}
