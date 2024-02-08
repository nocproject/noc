const apps = [
    // aaa
    '../../../ui/web/aaa/apikey/Application.js',
    '../../../ui/web/aaa/group/Application.js',
    '../../../ui/web/aaa/user/Application.js',
    // bi
    '../../../ui/web/bi/dashboardlayout/Application.js',
    // cm
    '../../../ui/web/cm/confdbquery/Application.js',
    '../../../ui/web/cm/configurationparam/Application.js',
    '../../../ui/web/cm/interfacevalidationpolicy/Application.js',
    '../../../ui/web/cm/objectnotify/Application.js',
    '../../../ui/web/cm/objectvalidationpolicy/Application.js',
    // crm
    '../../../ui/web/crm/subscriber/Application.js',
    '../../../ui/web/crm/subscriberprofile/Application.js',
    '../../../ui/web/crm/supplier/Application.js',
    '../../../ui/web/crm/supplierprofile/Application.js',
    // dev
    '../../../ui/web/dev/quiz/Application.js',
    '../../../ui/web/dev/spec/Application.js',
    // dns
    '../../../ui/web/dns/dnsserver/Application.js',
    '../../../ui/web/dns/dnszone/Application.js',
    '../../../ui/web/dns/dnszoneprofile/Application.js',
    // fm
    '../../../ui/web/fm/alarm/Application.js',
    '../../../ui/web/fm/alarmclass/Application.js',
    '../../../ui/web/fm/alarmclassconfig/Application.js',
    '../../../ui/web/fm/alarmdiagnosticconfig/Application.js',
    '../../../ui/web/fm/alarmescalation/Application.js',
    '../../../ui/web/fm/alarmseverity/Application.js',
    '../../../ui/web/fm/alarmtrigger/Application.js',
    '../../../ui/web/fm/classificationrule/Application.js',
    '../../../ui/web/fm/event/Application.js',
    '../../../ui/web/fm/eventclass/Application.js',
    '../../../ui/web/fm/eventtrigger/Application.js',
    '../../../ui/web/fm/ignoreeventrule/Application.js',
    '../../../ui/web/fm/ignorepattern/Application.js',
    '../../../ui/web/fm/mib/Application.js',
    '../../../ui/web/fm/mibpreference/Application.js',
    '../../../ui/web/fm/oidalias/Application.js',
    '../../../ui/web/fm/reportalarmdetail/Application.js',
    '../../../ui/web/fm/ttsystem/Application.js',
    // gis
    // '../../../ui/web/gis/area/Application.js', // not found in menu
    '../../../ui/web/gis/building/Application.js',
    '../../../ui/web/gis/division/Application.js',
    '../../../ui/web/gis/layer/Application.js',
    // '../../../ui/web/gis/overlay/Application.js', // not found in menu
    '../../../ui/web/gis/street/Application.js',
    // '../../../ui/web/gis/tms/Application.js', // not found in menu
    // inv
    '../../../ui/web/inv/allocationgroup/Application.js',
    '../../../ui/web/inv/capability/Application.js',
    '../../../ui/web/inv/connectionrule/Application.js',
    '../../../ui/web/inv/connectiontype/Application.js',
    '../../../ui/web/inv/coverage/Application.js',
    '../../../ui/web/inv/firmware/Application.js',
    '../../../ui/web/inv/firmwarepolicy/Application.js',
    '../../../ui/web/inv/interface/Application.js',
    '../../../ui/web/inv/interfaceprofile/Application.js',
    '../../../ui/web/inv/inv/Application.js',
    '../../../ui/web/inv/macdb/Application.js',
    '../../../ui/web/inv/map/Application.js',
    '../../../ui/web/inv/modelinterface/Application.js',
    '../../../ui/web/inv/modelmapping/Application.js',
    '../../../ui/web/inv/networksegment/Application.js',
    '../../../ui/web/inv/networksegmentprofile/Application.js',
    '../../../ui/web/inv/objectmodel/Application.js',
    '../../../ui/web/inv/platform/Application.js',
    '../../../ui/web/inv/reportifacestatus/Application.js',
    '../../../ui/web/inv/reportlinkdetail/Application.js',
    '../../../ui/web/inv/reportmetrics/Application.js',
    '../../../ui/web/inv/resourcegroup/Application.js',
    '../../../ui/web/inv/technology/Application.js',
    '../../../ui/web/inv/unknownmodel/Application.js',
    '../../../ui/web/inv/vendor/Application.js',
    // ip
    '../../../ui/web/ip/addressprofile/Application.js',
    '../../../ui/web/ip/addressrange/Application.js',
    '../../../ui/web/ip/ipam/Application.js',
    '../../../ui/web/ip/prefixaccess/Application.js',
    '../../../ui/web/ip/prefixprofile/Application.js',
    '../../../ui/web/ip/vrf/Application.js',
    '../../../ui/web/ip/vrfgroup/Application.js',
    // kb
    '../../../ui/web/kb/kbentry/Application.js',
    // main
    '../../../ui/web/main/audittrail/Application.js',
    '../../../ui/web/main/authldapdomain/Application.js',
    '../../../ui/web/main/chpolicy/Application.js',
    // '../../../ui/web/main/config/Application.js', // not found in menu
    '../../../ui/web/main/crontab/Application.js',
    '../../../ui/web/main/customfield/Application.js',
    '../../../ui/web/main/customfieldenumgroup/Application.js',
    '../../../ui/web/main/desktop/app.js',
    '../../../ui/web/main/extstorage/Application.js',
    '../../../ui/web/main/handler/Application.js',
    '../../../ui/web/main/jsonimport/Application.js',
    '../../../ui/web/main/language/Application.js',
    '../../../ui/web/main/mimetype/Application.js',
    '../../../ui/web/main/notificationgroup/Application.js',
    '../../../ui/web/main/pool/Application.js',
    '../../../ui/web/main/prefixtable/Application.js',
    '../../../ui/web/main/pyrule/Application.js',
    // '../../../ui/web/main/ref/Application.js', // not found in menu
    '../../../ui/web/main/refbookadmin/Application.js',
    '../../../ui/web/main/remotesystem/Application.js',
    '../../../ui/web/main/reportsubscription/Application.js',
    '../../../ui/web/main/resourcestate/Application.js',
    '../../../ui/web/main/search/Application.js',
    '../../../ui/web/main/style/Application.js',
    // '../../../ui/web/main/sync/Application.js', // not found in menu - deleted
    '../../../ui/web/main/systemnotification/Application.js',
    '../../../ui/web/main/systemtemplate/Application.js',
    '../../../ui/web/main/template/Application.js',
    '../../../ui/web/main/timepattern/Application.js',
    '../../../ui/web/main/userprofile/Application.js',
    '../../../ui/web/main/welcome/Application.js',
    // maintenance
    '../../../ui/web/maintenance/maintenance/Application.js',
    '../../../ui/web/maintenance/maintenancetype/Application.js',
    // peer
    '../../../ui/web/peer/as/Application.js',
    '../../../ui/web/peer/asprofile/Application.js',
    '../../../ui/web/peer/asset/Application.js',
    '../../../ui/web/peer/community/Application.js',
    '../../../ui/web/peer/communitytype/Application.js',
    '../../../ui/web/peer/maintainer/Application.js',
    '../../../ui/web/peer/organisation/Application.js',
    '../../../ui/web/peer/peer/Application.js',
    '../../../ui/web/peer/peergroup/Application.js',
    '../../../ui/web/peer/peeringpoint/Application.js',
    '../../../ui/web/peer/person/Application.js',
    '../../../ui/web/peer/prefixlistbuilder/Application.js',
    '../../../ui/web/peer/rir/Application.js',
    // phone
    '../../../ui/web/phone/dialplan/Application.js',
    '../../../ui/web/phone/numbercategory/Application.js',
    '../../../ui/web/phone/phonenumber/Application.js',
    '../../../ui/web/phone/phonenumberprofile/Application.js',
    '../../../ui/web/phone/phonerange/Application.js',
    '../../../ui/web/phone/phonerangeprofile/Application.js',
    // pm
    '../../../ui/web/pm/metricscope/Application.js',
    '../../../ui/web/pm/metrictype/Application.js',
    '../../../ui/web/pm/scale/Application.js',
    '../../../ui/web/pm/metricrule/Application.js',
    '../../../ui/web/pm/metricaction/Application.js',
    '../../../ui/web/pm/measurementunits/Application.js',
    '../../../ui/web/pm/agentprofile/Application.js',
    '../../../ui/web/pm/agent/Application.js',
    // project
    '../../../ui/web/project/project/Application.js',
    // sa
    '../../../ui/web/sa/action/Application.js',
    '../../../ui/web/sa/actioncommands/Application.js',
    '../../../ui/web/sa/administrativedomain/Application.js',
    '../../../ui/web/sa/authprofile/Application.js',
    '../../../ui/web/sa/capsprofile/Application.js',
    '../../../ui/web/sa/commandsnippet/Application.js',
    '../../../ui/web/sa/getnow/Application.js',
    '../../../ui/web/sa/groupaccess/Application.js',
    '../../../ui/web/sa/managedobject/Application.js',
    '../../../ui/web/sa/monitor/Application.js',
    '../../../ui/web/sa/managedobjectprofile/Application.js',
    // '../../../ui/web/sa/mrt/Application.js', // not found in menu
    '../../../ui/web/sa/objectnotification/Application.js',
    '../../../ui/web/sa/profile/Application.js',
    '../../../ui/web/sa/profilecheckrule/Application.js',
    '../../../ui/web/sa/reportobjectdetail/Application.js',
    '../../../ui/web/sa/runcommands/Application.js',
    '../../../ui/web/sa/service/Application.js',
    '../../../ui/web/sa/serviceprofile/Application.js',
    '../../../ui/web/sa/useraccess/Application.js',
    // sla
    '../../../ui/web/sla/slaprobe/Application.js',
    '../../../ui/web/sla/slaprofile/Application.js',
    // support
    '../../../ui/web/support/account/Application.js',
    '../../../ui/web/support/crashinfo/Application.js',
    // vc
    '../../../ui/web/vc/l2domain/Application.js',
    '../../../ui/web/vc/l2domainprofile/Application.js',
    '../../../ui/web/vc/vlanfilter/Application.js',
    '../../../ui/web/vc/vlan/Application.js',
    '../../../ui/web/vc/vlanprofile/Application.js',
    '../../../ui/web/vc/vpn/Application.js',
    '../../../ui/web/vc/vpnprofile/Application.js',
    // wf
    '../../../ui/web/wf/state/Application.js',
    '../../../ui/web/wf/transition/Application.js',
    '../../../ui/web/wf/wfmigration/Application.js',
    '../../../ui/web/wf/workflow/Application.js',
];

module.exports = apps;
