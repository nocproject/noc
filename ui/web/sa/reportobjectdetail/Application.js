//---------------------------------------------------------------------
// fm.reportalarmdetail application
//---------------------------------------------------------------------
// Copyright (C) 2007-2018 The NOC Project
// See LICENSE for details
//---------------------------------------------------------------------
console.debug("Defining NOC.sa.reportobjectdetail.Application");

Ext.define("NOC.sa.reportobjectdetail.Application", {
    extend: "NOC.core.Application",
    requires: [
        "NOC.core.ReportControl",
        "NOC.inv.networksegment.TreeCombo",
        "NOC.sa.administrativedomain.TreeCombo",
        "NOC.sa.managedobjectselector.LookupField"
    ],

    items: {
        xtype: "report.control",
        url: "/sa/reportobjectdetail",
        controls: [
            {
                name: "segment",
                xtype: "inv.networksegment.TreeCombo",
                fieldLabel: __("Segment"),
                listWidth: 1,
                listAlign: 'left',
                labelAlign: "left",
                width: 500
            },
            {
                name: "administrative_domain",
                xtype: "sa.administrativedomain.TreeCombo",
                fieldLabel: __("By Adm. domain"),
                listWidth: 1,
                listAlign: 'left',
                labelAlign: "left",
                width: 500,
                allowBlank: true
            },
            {
                name: "selector",
                xtype: "sa.managedobjectselector.LookupField",
                fieldLabel: __("By Selector"),
                listWidth: 1,
                listAlign: 'left',
                labelAlign: "left",
                width: 500,
                allowBlank: true
            }
        ],
        storeData: [
            ["id", __("ID"), false],
            ["object_name", __("Object Name"), true],
            ["object_address", __("IP"), true],
            ["object_hostname", __("Object Hostname"), true],
            ["object_status", __("Object Status"), true],
            ["profile_name", __("Profile"), true],
            ["object_profile", __("Object Profile"), false],
            ["object_vendor", __("Vendor"), false],
            ["object_platform", __("Platform"), false],
            ["object_version", __("SW Version"), false],
            ["object_serial", __("Serial Number"), false],
            ["auth_profile", __("Auth Profile"), false],
            ["avail", __("Avail"), false],
            ["admin_domain", __("Admin. Domain"), true],
            ["container", __("Container"), false],
            ["segment", __("Segment"), true],
            ["phys_interface_count", __("Physical Iface Count"), false],
            ["link_count", __("Link Count"), false],
            ["last_config_ts", __("Last Config get Timestamp"), false],
            ["adm_path", __("Adm Path"), true],
            ["interface_type_count", __("Interface count by type"), false],
            ["object_caps", __("Object capabilities"), false],
            ["object_tags", __("Object Tags"), false],
            ["sorted_tags", __("Sorted Tags"), false],
            ["discovery_problem", __("Discovery Problem"), false]
        ]
    }
});
