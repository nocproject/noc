//---------------------------------------------------------------------
// inv.reportifacestatus application
//---------------------------------------------------------------------
// Copyright (C) 2007-2018 The NOC Project
// See LICENSE for details
//---------------------------------------------------------------------
console.debug("Defining NOC.inv.reportifacestatus.Application");

Ext.define("NOC.inv.reportifacestatus.Application", {
    extend: "NOC.core.Application",
    requires: [
        "NOC.core.ReportControl",
        "NOC.sa.administrativedomain.TreeCombo",
        "NOC.sa.managedobjectselector.LookupField",
        "NOC.inv.interfaceprofile.LookupField"
    ],

    items: {
        xtype: "report.control",
        url: "/inv/reportifacestatus",
        controls: [
            {
                name: "interface_profile",
                xtype: "inv.interfaceprofile.LookupField",
                fieldLabel: __("By Interface Profile"),
                listWidth: 1,
                listAlign: 'left',
                labelAlign: "left",
                margin: 0,
                width: 300,
                defaults: {
                    padding: "0 5"
                }
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
                name: "zero",
                xtype: "checkboxfield",
                boxLabel: __("Exclude ports in the status down"),
                value: true,
                allowBlank: false
            },
            {
                name: "def_profile",
                xtype: "checkboxfield",
                boxLabel: __("Exclude interfaces with the \"default\" name profile " +
                    "(for Selector and Administrative Domain filter)"),
                value: true,
                allowBlank: false
            }
        ],
        storeData: [
            ["object_name", __("Object Name"), true],
            ["object_address", __("IP address"), true],
            ["object_model", __("Object Model"), true],
            ["object_software", __("Object Software"), true],
            ["object_port_name", __("Port name"), true],
            ["object_port_profile_name", __("Port profile name"), true],
            ["object_port_status", __("Port status"), true],
            ["object_link_status", __("Link status"), true],
            ["object_port_speed", __("Port speed"), true],
            ["object_port_duplex", __("Port duplex"), true]
        ]
    }
});
