//---------------------------------------------------------------------
// inv.reportllinkdetail application
//---------------------------------------------------------------------
// Copyright (C) 2007-2016 The NOC Project
// See LICENSE for details
//---------------------------------------------------------------------
console.debug("Defining NOC.inv.reportlinkdetail.Application");

Ext.define("NOC.inv.reportlinkdetail.Application", {
    extend: "NOC.core.Application",
    requires: [
        "NOC.core.ReportControl",
        "NOC.inv.networksegment.TreeCombo",
        "NOC.sa.administrativedomain.TreeCombo",
        "NOC.sa.managedobjectselector.LookupField"
    ],

    items: {
        xtype: "report.control",
        url: "/inv/reportlinkdetail",
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
            ["admin_domain", __("Admin. Domain"), true],
            ["object1_name", __("Object1 Name"), true],
            ["object1_address", __("IP1"), true],
            ["object1_iface", __("Interface1"), true],
            ["object2_name", __("Object2 Name"), true],
            ["object2_address", __("IP2"), true],
            ["object2_iface", __("Interface2"), true],
            ["link_proto", __("Link Proto"), true],
            ["last_seen", __("Link Last Seen"), false]
        ]
    }
});
