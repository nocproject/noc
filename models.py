# ---------------------------------------------------------------------
# NOC models lazy loading and utilities
# ---------------------------------------------------------------------
# Copyright (C) 2007-2020 The NOC Project
# See LICENSE for details
# ---------------------------------------------------------------------

# Python modules
import logging

# Third-party modules
from typing import Dict, Any

logger = logging.getLogger(__name__)


def is_document(object):
    """
    Check object is mongoengine document
    :param object:
    :return:
    """
    return getattr(object, "_is_document", False)


def get_model_id(object):
    """
    Returns model id for instance object
    """
    if is_document(object):
        # Document
        app = object.__module__.split(".")[1]
        model = object._class_name
    else:
        app = object._meta.app_label if object._meta.app_label != "auth" else "main"
        model = object._meta.object_name
    return f"{app}.{model}"


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


def iter_model_id():
    """
    Iterate all model ids
    """
    yield from _MODELS


# Model cache: model_id -> class
_MCACHE: Dict[str, Any] = {}

_MODELS = {
    # aaa models
    "aaa.APIKey": "noc.aaa.models.apikey.APIKey",
    "aaa.Group": "noc.aaa.models.group.Group",
    "aaa.ModelProtectionProfile": "noc.aaa.models.modelprotectionprofile.ModelProtectionProfile",
    "aaa.Permission": "noc.aaa.models.permission.Permission",
    "aaa.User": "noc.aaa.models.user.User",
    "aaa.UserContact": "noc.aaa.models.usercontact.UserContact",
    # main models
    "main.APIToken": "noc.main.models.apitoken.APIToken",
    "main.AuditTrail": "noc.main.models.audittrail.AuditTrail",
    "main.Avatar": "noc.main.models.avatar.Avatar",
    "main.Checkpoint": "noc.main.models.checkpoint.Checkpoint",
    "main.CHPolicy": "noc.main.models.chpolicy.CHPolicy",
    "main.CronTab": "noc.main.models.crontab.CronTab",
    "main.CustomField": "noc.main.models.customfield.CustomField",
    "main.CustomFieldEnumGroup": "noc.main.models.customfieldenumgroup.CustomFieldEnumGroup",
    "main.CustomFieldEnumValue": "noc.main.models.customfieldenumvalue.CustomFieldEnumValue",
    "main.DatabaseStorage": "noc.main.models.databasestorage.DatabaseStorage",
    "main.DataStreamConfig": "noc.main.models.datastreamconfig.DataStreamConfig",
    "main.DocCategory": "noc.main.models.doccategory.DocCategory",
    "main.ExtStorage": "noc.main.models.extstorage.ExtStorage",
    "main.Font": "noc.main.models.font.Font",
    "main.Favorites": "noc.main.models.favorites.Favorites",
    "main.Glyph": "noc.main.models.glyph.Glyph",
    "main.ImageStore": "noc.main.models.imagestore.ImageStore",
    "main.Handler": "noc.main.models.handler.Handler",
    "main.Language": "noc.main.models.language.Language",
    "main.MessageRoute": "noc.main.models.messageroute.MessageRoute",
    "main.MetricStream": "noc.main.models.metricstream.MetricStream",
    "main.MIMEType": "noc.main.models.mimetype.MIMEType",
    "main.NotificationGroup": "noc.main.models.notificationgroup.NotificationGroup",
    "main.NotificationGroupOther": "noc.main.models.notificationgroup.NotificationGroupOther",
    "main.NotificationGroupUser": "noc.main.models.notificationgroup.NotificationGroupUser",
    "main.Pool": "noc.main.models.pool.Pool",
    "main.PrefixTable": "noc.main.models.prefixtable.PrefixTable",
    "main.PyRule": "noc.main.models.pyrule.PyRule",
    "main.Label": "noc.main.models.label.Label",
    "main.RefBook": "noc.main.models.refbook.RefBook",
    "main.RefBookData": "noc.main.models.refbookdata.RefBookData",
    "main.RefBookField": "noc.main.models.refbookfield.RefBookField",
    "main.RemoteSystem": "noc.main.models.remotesystem.RemoteSystem",
    "main.Report": "noc.main.models.report.Report",
    "main.ReportSubscription": "noc.main.models.reportsubscription.ReportSubscription",
    "main.ResourceState": "noc.main.models.resourcestate.ResourceState",
    "main.SlowOp": "noc.main.models.slowop.SlowOp",
    "main.Style": "noc.main.models.style.Style",
    "main.SystemNotification": "noc.main.models.systemnotification.SystemNotification",
    "main.SystemTemplate": "noc.main.models.systemtemplate.SystemTemplate",
    "main.Template": "noc.main.models.template.Template",
    "main.TextIndex": "noc.main.models.textindex.TextIndex",
    "main.TimePattern": "noc.main.models.timepattern.TimePattern",
    "main.TimePatternTerm": "noc.main.models.timepatternterm.TimePatternTerm",
    "main.UserState": "noc.main.models.userstate.UserState",
    #
    "dev.Quiz": "noc.dev.models.quiz.Quiz",
    "dev.Spec": "noc.dev.models.spec.Spec",
    # project models
    "project.Project": "noc.project.models.project.Project",
    # gis models
    "gis.Address": "noc.gis.models.address.Address",
    "gis.Area": "noc.gis.models.area.Area",
    "gis.Building": "noc.gis.models.building.Building",
    "gis.Division": "noc.gis.models.division.Division",
    "gis.Layer": "noc.gis.models.layer.Layer",
    "gis.LayerUserSettings": "noc.gis.models.layerusersettings.LayerUserSettings",
    "gis.Overlay": "noc.gis.models.overlay.Overlay",
    "gis.Street": "noc.gis.models.street.Street",
    # inv models
    "inv.AllocationGroup": "noc.inv.models.allocationgroup.AllocationGroup",
    "inv.BioSegTrial": "noc.inv.models.biosegtrial.BioSegTrial",
    "inv.Capability": "noc.inv.models.capability.Capability",
    "inv.ConfiguredMap": "noc.inv.models.configuredmap.ConfiguredMap",
    "inv.ConnectionRule": "noc.inv.models.connectionrule.ConnectionRule",
    "inv.ConnectionType": "noc.inv.models.connectiontype.ConnectionType",
    "inv.Coverage": "noc.inv.models.coverage.Coverage",
    "inv.CoveredBuilding": "noc.inv.models.coveredbuilding.CoveredBuilding",
    "inv.CoveredObject": "noc.inv.models.coveredobject.CoveredObject",
    "inv.CPE": "noc.inv.models.cpe.CPE",
    "inv.CPEProfile": "noc.inv.models.cpeprofile.CPEProfile",
    "inv.DiscoveryID": "noc.inv.models.discoveryid.DiscoveryID",
    "inv.ExtNRILink": "noc.inv.models.extnrilink.ExtNRILink",
    "inv.Facade": "noc.inv.models.facade.Facade",
    "inv.Firmware": "noc.inv.models.firmware.Firmware",
    "inv.FirmwarePolicy": "noc.inv.models.firmwarepolicy.FirmwarePolicy",
    "inv.ForwardingInstance": "noc.inv.models.forwardinginstance.ForwardingInstance",
    "inv.IfDescPatterns": "noc.inv.models.ifdescpatterns.IfDescPatterns",
    "inv.Interface": "noc.inv.models.interface.Interface",
    "inv.InterfaceProfile": "noc.inv.models.interfaceprofile.InterfaceProfile",
    "inv.Link": "noc.inv.models.link.Link",
    "inv.MACBlacklist": "noc.inv.models.macblacklist.MACBlacklist",
    "inv.MACDB": "noc.inv.models.macdb.MACDB",
    "inv.MACLog": "noc.inv.models.maclog.MACLog",
    "inv.MapSettings": "noc.inv.models.mapsettings.MapSettings",
    "inv.ModelConnectionsCache": "noc.inv.models.objectmodel.ModelConnectionsCache",
    "inv.ModelInterface": "noc.inv.models.modelinterface.ModelInterface",
    "inv.ModelMapping": "noc.inv.models.modelmapping.ModelMapping",
    "inv.NetworkSegment": "noc.inv.models.networksegment.NetworkSegment",
    "inv.NetworkSegmentProfile": "noc.inv.models.networksegmentprofile.NetworkSegmentProfile",
    "inv.Object": "noc.inv.models.object.Object",
    "inv.ObjectConfigurationRule": "noc.inv.models.objectconfigurationrule.ObjectConfigurationRule",
    "inv.ObjectConnection": "noc.inv.models.objectconnection.ObjectConnection",
    "inv.ObjectFile": "noc.inv.models.objectfile.ObjectFile",
    "inv.ObjectLog": "noc.inv.models.objectlog.ObjectLog",
    "inv.ObjectModel": "noc.inv.models.objectmodel.ObjectModel",
    "inv.Platform": "noc.inv.models.platform.Platform",
    "inv.Protocol": "noc.inv.models.protocol.Protocol",
    "inv.ResourcePool": "noc.inv.models.resourcepool.ResourcePool",
    "inv.Sensor": "noc.inv.models.sensor.Sensor",
    "inv.SensorProfile": "noc.inv.models.sensor.SensorProfile",
    "inv.SubInterface": "noc.inv.models.subinterface.SubInterface",
    "inv.Technology": "noc.inv.models.technology.Technology",
    "inv.ResourceGroup": "noc.inv.models.resourcegroup.ResourceGroup",
    "inv.UnknownModel": "noc.inv.models.unknownmodel.UnknownModel",
    "inv.Vendor": "noc.inv.models.vendor.Vendor",
    # sa models
    "sa.Action": "noc.sa.models.action.Action",
    "sa.ActionCommands": "noc.sa.models.actioncommands.ActionCommands",
    "sa.AdministrativeDomain": "noc.sa.models.administrativedomain.AdministrativeDomain",
    "sa.AuthProfile": "noc.sa.models.authprofile.AuthProfile",
    "sa.CapsProfile": "noc.sa.models.capsprofile.CapsProfile",
    "sa.CommandSnippet": "noc.sa.models.commandsnippet.CommandSnippet",
    "sa.CPEStatus": "noc.sa.models.cpestatus.CPEStatus",
    "sa.CredentialCheckRule": "noc.sa.models.credentialcheckrule.CredentialCheckRule",
    "sa.DiscoveredObject": "noc.sa.models.discoveredobject.DiscoveredObject",
    "sa.GroupAccess": "noc.sa.models.groupaccess.GroupAccess",
    "sa.InteractionLog": "noc.sa.models.interactionlog.InteractionLog",
    "sa.Job": "noc.sa.models.job.Job",
    "sa.ManagedObject": "noc.sa.models.managedobject.ManagedObject",
    "sa.ManagedObjectAttribute": "noc.sa.models.managedobject.ManagedObjectAttribute",
    "sa.ManagedObjectProfile": "noc.sa.models.managedobjectprofile.ManagedObjectProfile",
    "sa.ObjectNotification": "noc.sa.models.objectnotification.ObjectNotification",
    "sa.ObjectDiagnosticConfig": "noc.sa.models.objectdiagnosticconfig.ObjectDiagnosticConfig",
    "sa.ObjectDiscoveryRule": "noc.sa.models.objectdiscoveryrule.ObjectDiscoveryRule",
    "sa.ObjectStatus": "noc.sa.models.objectstatus.ObjectStatus",
    "sa.Profile": "noc.sa.models.profile.Profile",
    "sa.ProfileCheckRule": "noc.sa.models.profilecheckrule.ProfileCheckRule",
    "sa.Service": "noc.sa.models.service.Service",
    "sa.ServiceProfile": "noc.sa.models.serviceprofile.ServiceProfile",
    "sa.ServiceSummary": "noc.sa.models.servicesummary.ServiceSummary",
    "sa.UserAccess": "noc.sa.models.useraccess.UserAccess",
    # fm models
    "fm.ActiveAlarm": "noc.fm.models.activealarm.ActiveAlarm",
    "fm.ActiveEvent": "noc.fm.models.activeevent.ActiveEvent",
    "fm.AlarmClass": "noc.fm.models.alarmclass.AlarmClass",
    "fm.AlarmClassCategory": "noc.fm.models.alarmclasscategory.AlarmClassCategory",
    "fm.AlarmClassConfig": "noc.fm.models.alarmclassconfig.AlarmClassConfig",
    "fm.AlarmDiagnosticConfig": "noc.fm.models.alarmdiagnosticconfig.AlarmDiagnosticConfig",
    "fm.AlarmEscalation": "noc.fm.models.alarmescalation.AlarmEscalation",
    "fm.AlarmRule": "noc.fm.models.alarmrule.AlarmRule",
    "fm.AlarmSeverity": "noc.fm.models.alarmseverity.AlarmSeverity",
    "fm.AlarmTrigger": "noc.fm.models.alarmtrigger.AlarmTrigger",
    "fm.ArchivedAlarm": "noc.fm.models.archivedalarm.ArchivedAlarm",
    "fm.ArchivedEvent": "noc.fm.models.archivedevent.ArchivedEvent",
    "fm.CloneClassificationRule": "noc.fm.models.cloneclassificationrule.CloneClassificationRule",
    "fm.Enumeration": "noc.fm.models.enumeration.Enumeration",
    "fm.Escalation": "noc.fm.models.escalation.Escalation",
    "fm.EscalationProfile": "noc.fm.models.escalationprofile.EscalationProfile",
    "fm.EventClass": "noc.fm.models.eventclass.EventClass",
    "fm.EventClassCategory": "noc.fm.models.eventclass.EventClassCategory",
    "fm.EventClassificationRule": "noc.fm.models.eventclassificationrule.EventClassificationRule",
    "fm.EventClassificationRuleCategory": "noc.fm.models.eventclassificationrule.EventClassificationRuleCategory",
    "fm.EventTrigger": "noc.fm.models.eventtrigger.EventTrigger",
    "fm.FailedEvent": "noc.fm.models.failedevent.FailedEvent",
    "fm.IgnoreEventRules": "noc.fm.models.ignoreeventrules.IgnoreEventRules",
    "fm.IgnorePattern": "noc.fm.models.ignorepattern.IgnorePattern",
    "fm.MIB": "noc.fm.models.mib.MIB",
    "fm.MIBAlias": "noc.fm.models.mibalias.MIBAlias",
    "fm.MIBData": "noc.fm.models.mibdata.MIBData",
    "fm.MIBPreference": "noc.fm.models.mibpreference.MIBPreference",
    "fm.OIDAlias": "noc.fm.models.oidalias.OIDAlias",
    "fm.Outage": "noc.fm.models.outage.Outage",
    "fm.Reboot": "noc.fm.models.reboot.Reboot",
    "fm.SyntaxAlias": "noc.fm.models.syntaxalias.SyntaxAlias",
    "fm.TTSystem": "noc.fm.models.ttsystem.TTSystem",
    "fm.Uptime": "noc.fm.models.uptime.Uptime",
    # pm models
    "pm.Agent": "noc.pm.models.agent.Agent",
    "pm.AgentProfile": "noc.pm.models.agent.AgentProfile",
    "pm.Scale": "noc.pm.models.scale.Scale",
    "pm.MeasurementUnits": "noc.pm.models.measurementunits.MeasurementUnits",
    "pm.MetricAction": "noc.pm.models.metricaction.MetricAction",
    "pm.MetricRule": "noc.pm.models.metricrule.MetricRule",
    "pm.MetricScope": "noc.pm.models.metricscope.MetricScope",
    "pm.MetricType": "noc.pm.models.metrictype.MetricType",
    "pm.ThresholdProfile": "noc.pm.models.thresholdprofile.ThresholdProfile",
    # cm models
    "cm.ConfDBQuery": "noc.cm.models.confdbquery.ConfDBQuery",
    "cm.InterfaceValidationPolicy": "noc.cm.models.interfacevalidationpolicy.InterfaceValidationPolicy",
    "cm.ObjectNotify": "noc.cm.models.objectnotify.ObjectNotify",
    "cm.ObjectValidationPolicy": "noc.cm.models.objectvalidationpolicy.ObjectValidationPolicy",
    "cm.ConfigurationScope": "noc.cm.models.configurationscope.ConfigurationScope",
    "cm.ConfigurationParam": "noc.cm.models.configurationparam.ConfigurationParam",
    # ip models
    "ip.Address": "noc.ip.models.address.Address",
    "ip.AddressProfile": "noc.ip.models.addressprofile.AddressProfile",
    "ip.AddressRange": "noc.ip.models.addressrange.AddressRange",
    "ip.Prefix": "noc.ip.models.prefix.Prefix",
    "ip.PrefixAccess": "noc.ip.models.prefixaccess.PrefixAccess",
    "ip.PrefixBookmark": "noc.ip.models.prefixbookmark.PrefixBookmark",
    "ip.PrefixProfile": "noc.ip.models.prefixprofile.PrefixProfile",
    "ip.VRF": "noc.ip.models.vrf.VRF",
    "ip.VRFGroup": "noc.ip.models.vrfgroup.VRFGroup",
    # vc models
    "vc.L2DomainProfile": "noc.vc.models.l2domainprofile.L2DomainProfile",
    "vc.L2Domain": "noc.vc.models.l2domain.L2Domain",
    "vc.VLANProfile": "noc.vc.models.vlanprofile.VLANProfile",
    "vc.VLANFilter": "noc.vc.models.vlanfilter.VLANFilter",
    "vc.VLANTemplate": "noc.vc.models.vlantemplate.VLANTemplate",
    "vc.VLAN": "noc.vc.models.vlan.VLAN",
    "vc.VPNProfile": "noc.vc.models.vpnprofile.VPNProfile",
    "vc.VPN": "noc.vc.models.vpn.VPN",
    # dns models
    "dns.DNSServer": "noc.dns.models.dnsserver.DNSServer",
    "dns.DNSZone": "noc.dns.models.dnszone.DNSZone",
    "dns.DNSZoneProfile": "noc.dns.models.dnszoneprofile.DNSZoneProfile",
    "dns.DNSZoneRecord": "noc.dns.models.dnszonerecord.DNSZoneRecord",
    # peer models
    "peer.ASProfile": "noc.peer.models.asprofile.ASProfile",
    "peer.AS": "noc.peer.models.asn.AS",
    "peer.ASSet": "noc.peer.models.asset.ASSet",
    "peer.Community": "noc.peer.models.community.Community",
    "peer.CommunityType": "noc.peer.models.communitytype.CommunityType",
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
    "kb.KBEntry": "noc.kb.models.kbentry.KBEntry",
    "kb.KBEntryAttachment": "noc.kb.models.kbentryattachment.KBEntryAttachment",
    "kb.KBEntryHistory": "noc.kb.models.kbentryhistory.KBEntryHistory",
    "kb.KBEntryPreviewLog": "noc.kb.models.kbentrypreviewlog.KBEntryPreviewLog",
    "kb.KBEntryTemplate": "noc.kb.models.kbentrytemplate.KBEntryTemplate",
    "kb.KBGlobalBookmark": "noc.kb.models.kbglobalbookmark.KBGlobalBookmark",
    "kb.KBUserBookmark": "noc.kb.models.kbuserbookmark.KBUserBookmark",
    # Maintenance
    "maintenance.Maintenance": "noc.maintenance.models.maintenance.Maintenance",
    "maintenance.MaintenanceType": "noc.maintenance.models.maintenancetype.MaintenanceType",
    # support models
    "support.Crashinfo": "noc.support.models.crashinfo.Crashinfo",
    # crm models
    "crm.SubscriberProfile": "noc.crm.models.subscriberprofile.SubscriberProfile",
    "crm.SupplierProfile": "noc.crm.models.supplierprofile.SupplierProfile",
    "crm.Subscriber": "noc.crm.models.subscriber.Subscriber",
    "crm.Supplier": "noc.crm.models.supplier.Supplier",
    # sla models
    "sla.SLAProfile": "noc.sla.models.slaprofile.SLAProfile",
    "sla.SLAProbe": "noc.sla.models.slaprobe.SLAProbe",
    # bi models
    "bi.DashboardLayout": "noc.bi.models.dashboardlayout.DashboardLayout",
    "bi.Dashboard": "noc.bi.models.dashboard.Dashboard",
    # phone models
    "phone.DialPlan": "noc.phone.models.dialplan.DialPlan",
    "phone.NumberCategory": "noc.phone.models.numbercategory.NumberCategory",
    "phone.PhoneNumber": "noc.phone.models.phonenumber.PhoneNumber",
    "phone.PhoneNumberProfile": "noc.phone.models.phonenumberprofile.PhoneNumberProfile",
    "phone.PhoneRange": "noc.phone.models.phonerange.PhoneRange",
    "phone.PhoneRangeProfile": "noc.phone.models.phonerangeprofile.PhoneRangeProfile",
    # wf models
    "wf.Workflow": "noc.wf.models.workflow.Workflow",
    "wf.State": "noc.wf.models.state.State",
    "wf.Transition": "noc.wf.models.transition.Transition",
    "wf.WFMigration": "noc.wf.models.wfmigration.WFMigration",
}

FTS_MODELS = ["ip.Address", "ip.Prefix", "ip.VRF", "sa.ManagedObject", "cpe.CPE"]

COLLECTIONS = [
    "main.Template",
    "main.Handler",
    "main.Label",
    "wf.Workflow",
    "wf.State",
    "wf.Transition",
    "wf.WFMigration",
    "main.Font",
    "main.Glyph",
    "fm.SyntaxAlias",
    "sa.Profile",
    "dev.Quiz",
    "dev.Spec",
    "sa.Action",
    "inv.Capability",
    "pm.Scale",
    "pm.MeasurementUnits",
    "pm.MetricScope",
    "pm.MetricType",
    "pm.MetricAction",
    "fm.Enumeration",
    "cm.ConfigurationScope",
    "cm.ConfigurationParam",
    "inv.Facade",
    "inv.ConnectionRule",
    "inv.ConnectionType",
    "inv.ObjectConfigurationRule",
    "inv.Vendor",
    "inv.Platform",
    "inv.Firmware",
    "inv.MACBlacklist",
    "fm.MIBAlias",
    "gis.Layer",
    "fm.OIDAlias",
    "inv.Technology",
    "inv.Protocol",
    "fm.MIBPreference",
    "inv.ModelInterface",
    "fm.AlarmSeverity",
    "sa.ActionCommands",
    "inv.ObjectModel",
    "fm.AlarmClass",
    "fm.EventClass",
    "fm.EventClassificationRule",
    "fm.CloneClassificationRule",
    "sa.ProfileCheckRule",
    "pm.ThresholdProfile",
    "bi.DashboardLayout",
    "bi.Dashboard",
    "cm.ConfDBQuery",
    "main.Report",
]

# Model -> Setting
LABEL_MODELS = {
    "pm.Agent": "enable_agent",
    "sa.Service": "enable_service",
    "sa.ServiceProfile": "enable_serviceprofile",
    "sa.ManagedObject": "enable_managedobject",
    "sa.ManagedObjectProfile": "enable_managedobjectprofile",
    "sa.AdministrativeDomain": "enable_administrativedomain",
    "sa.AuthProfile": "enable_authprofile",
    "sa.CommandSnippet": "enable_commandsnippet",
    #
    "inv.AllocationGroup": "enable_allocationgroup",
    "inv.NetworkSegment": "enable_networksegment",
    "inv.Object": "enable_object",
    "inv.ObjectModel": "enable_objectmodel",
    "inv.Platform": "enable_platform",
    "inv.ResourceGroup": "enable_resourcegroup",
    "inv.Sensor": "enable_sensor",
    "inv.SensorProfile": "enable_sensorprofile",
    "inv.Interface": "enable_interface",
    "inv.FirmwarePolicy": "enable_firmwarepolicy",
    #
    "crm.Subscriber": "enable_subscriber",
    "crm.SubscriberProfile": "enable_subscriber",
    "crm.Supplier": "enable_supplier",
    "crm.SupplierProfile": "enable_supplier",
    #
    "dns.DNSZone": "enable_dnszone",
    "dns.DNSZoneRecord": "enable_dnszonerecord",
    #
    "gis.Division": "enable_division",
    "kb.KBEntry": "enable_kbentry",
    #
    "ip.Address": "enable_ipaddress",
    "ip.AddressProfile": "enable_addressprofile",
    "ip.AddressRange": "enable_ipaddressrange",
    "ip.Prefix": "enable_ipprefix",
    "ip.PrefixProfile": "enable_prefixprofile",
    "ip.VRF": "enable_vrf",
    "ip.VRFGroup": "enable_vrfgroup",
    #
    "peer.AS": "enable_asn",
    "peer.ASSet": "enable_assetpeer",
    "peer.Peer": "enable_peer",
    #
    "vc.VLAN": "enable_vlan",
    "vc.VLANProfile": "enable_vlanprofile",
    "vc.VPN": "enable_vpn",
    "vc.VPNProfile": "enable_vpnprofile",
    #
    "sla.SLAProbe": "enable_slaprobe",
    "sla.SLAProfile": "enable_slaprofile",
    "fm.ActiveAlarm": "enable_alarm",
    #
    "wf.State": "enable_workflowstate",
}
