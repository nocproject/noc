//---------------------------------------------------------------------
// inv.firmwarepolicy application
//---------------------------------------------------------------------
// Copyright (C) 2007-2016 The NOC Project
// See LICENSE for details
//---------------------------------------------------------------------
console.debug("Defining NOC.inv.firmwarepolicy.Application");

Ext.define("NOC.inv.firmwarepolicy.Application", {
    extend: "NOC.core.ModelApplication",
    requires: [
        "NOC.inv.firmwarepolicy.Model",
        "NOC.sa.managedobjectprofile.LookupField",
        "NOC.inv.firmware.LookupField"
    ],
    model: "NOC.inv.firmwarepolicy.Model",
    initComponent: function() {
        var me = this;
        Ext.apply(me, {
            columns: [
                {
                    text: "Profile",
                    dataIndex: "object_profile",
                    renderer: NOC.render.Lookup("object_profile"),
                    width: 150
                },
                {
                    text: "Platform",
                    dataIndex: "platform",
                    width: 150
                },
                {
                    text: "Firmware",
                    dataIndex: "firmware",
                    renderer: NOC.render.Lookup("firmware"),
                    width: 150
                },
                {
                    text: "Status",
                    dataIndex: "status",
                    width: 50,
                    renderer: NOC.render.Choices({
                        r: "Recommended",
                        a: "Acceptable",
                        n: "Not recommended",
                        d: "Denied"
                    })
                },
                {
                    text: "Management",
                    dataIndex: "management",
                    flex: 1,
                    renderer: function(v) {
                        return map((v || []).map(function(x) {return x.protocol;})).join(", ")
                    }
                }
            ],

            fields: [
                {
                    name: "object_profile",
                    xtype: "sa.managedobjectprofile.LookupField",
                    fieldLabel: "Profile",
                    allowBlank: false
                },
                {
                    name: "platform",
                    xtype: "textfield",
                    fieldLabel: "Platform",
                    allowBlank: false
                },
                {
                    name: "firmware",
                    xtype: "inv.firmware.LookupField",
                    fieldLabel: "Firmware",
                    allowBlank: false
                },
                {
                    name: "status",
                    xtype: "combobox",
                    fieldLabel: "Status",
                    allowBlank: false,
                    store: [
                        ["r", "Recommended"],
                        ["a", "Acceptable"],
                        ["n", "Not recommended"],
                        ["d", "Denied"]
                    ]
                },
                {
                    name: "description",
                    xtype: "textarea",
                    fieldLabel: "Description",
                    allowBlank: true
                },
                {
                    name: "management",
                    xtype: "gridfield",
                    fieldLabel: "Management",
                    columns: [
                        {
                            text: "Protocol",
                            dataIndex: "protocol",
                            flex: 1,
                            editor: {
                                xtype: "combobox",
                                store: [
                                    ["cli", "CLI"],
                                    ["snmp", "SNMP"],
                                    ["http", "HTTP"]
                                ]
                            }
                        }
                    ]
                }
            ]
        });
        me.callParent();
    }
});
