//---------------------------------------------------------------------
// fm.ignorepattern application
//---------------------------------------------------------------------
// Copyright (C) 2007-2014 The NOC Project
// See LICENSE for details
//---------------------------------------------------------------------
console.debug("Defining NOC.fm.ignorepattern.Application");

Ext.define("NOC.fm.ignorepattern.Application", {
    extend: "NOC.core.ModelApplication",
    requires: [
        "NOC.fm.ignorepattern.Model"
    ],
    model: "NOC.fm.ignorepattern.Model",

    initComponent: function() {
        var me = this;
        Ext.apply(me, {
            columns: [
                {
                    text: "Source",
                    dataIndex: "source",
                    width: 75
                },
                {
                    text: "Active",
                    dataIndex: "is_active",
                    width: 25,
                    renderer: NOC.render.Bool
                },
                {
                    text: "Pattern",
                    dataIndex: "pattern",
                    flex: 1
                }
            ],
            fields: [
                {
                    name: "source",
                    xtype: "combobox",
                    fieldLabel: "Source",
                    allowBlank: false,
                    store: [
                        ["syslog", "SYSLOG"],
                        ["SNMP Trap", "SNMP Trap"]
                    ]
                },
                {
                    name: "is_active",
                    xtype: "checkbox",
                    boxLabel: "Active"
                },
                {
                    name: "pattern",
                    xtype: "textfield",
                    fieldLabel: "Pattern (RE)",
                    allowBlank: false
                },
                {
                    name: "description",
                    xtype: "textarea",
                    fieldLabel: "Description",
                    allowBlank: true
                }
            ]
        });
        me.callParent();
    }
});
