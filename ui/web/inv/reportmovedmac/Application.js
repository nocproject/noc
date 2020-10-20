// fm.reportmovedmac application
//---------------------------------------------------------------------
// Copyright (C) 2007-2016 The NOC Project
// See LICENSE for details
//---------------------------------------------------------------------
console.debug("Defining NOC.inv.reportmovedmac.Application");

Ext.define("NOC.inv.reportmovedmac.Application", {
    extend: "NOC.core.Application",
    requires: [
        "NOC.core.ReportControl",
        "NOC.inv.networksegment.TreeCombo",
        "NOC.inv.interfaceprofile.LookupField",
        "NOC.sa.administrativedomain.TreeCombo",
        "NOC.sa.managedobjectselector.LookupField",
        "NOC.fm.alarm.view.grids.Tagfield"
    ],

    items: {
        xtype: "report.control",
        url: "/inv/reportmovedmac",
        controls: [
            {
                name: "from_date",
                xtype: "datefield",
                startDay: 1,
                fieldLabel: __("From"),
                allowBlank: false,
                format: "d.m.Y",
                submitFormat: "d.m.Y"
            },
            {
                name: "to_date",
                xtype: "datefield",
                startDay: 1,
                fieldLabel: __("To"),
                allowBlank: false,
                format: "d.m.Y",
                submitFormat: "d.m.Y"
            },
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
            },
            {
                name: "interface_profile",
                xtype: "inv.interfaceprofile.LookupField",
                fieldLabel: __("By Interface Profile"),
                listWidth: 1,
                listAlign: 'left',
                labelAlign: "left",
                width: 500,
                allowBlank: true
            },
            {
                name: "enable_autowidth",
                xtype: "checkboxfield",
                boxLabel: __("Enable Excel column autowidth"),
                allowBlank: false
            },
        ],
        storeData: [
            ["vendor_mac", __("Vendor MAC"), true],
            ["mac", __("MAC"), true],
            ["object_name", __("Object Name"), true],
            ["object_address", __("Object  Address"), true],
            ["object_adm_domain", __("Object Adm. Domain"), true],
            ["ifaces", __("Moved interfaces"), true],
        ]
    }
});
