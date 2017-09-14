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
        "NOC.inv.firmware.LookupField",
        "NOC.inv.platform.LookupField"
    ],
    model: "NOC.inv.firmwarepolicy.Model",
    initComponent: function() {
        var me = this;
        Ext.apply(me, {
            columns: [
                {
                    text: __("Profile"),
                    dataIndex: "object_profile",
                    renderer: NOC.render.Lookup("object_profile"),
                    width: 150
                },
                {
                    text: __("Platform"),
                    dataIndex: "platform",
                    renderer: NOC.render.Lookup("platform"),
                    width: 150
                },
                {
                    text: __("Firmware"),
                    dataIndex: "firmware",
                    renderer: NOC.render.Lookup("firmware"),
                    width: 150
                },
                {
                    text: __("Status"),
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
                    text: __("Management"),
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
                    fieldLabel: __("Profile"),
                    allowBlank: false
                },
                {
                    name: "platform",
                    xtype: "inv.platform.LookupField",
                    fieldLabel: __("Platform"),
                    allowBlank: false
                },
                {
                    name: "firmware",
                    xtype: "inv.firmware.LookupField",
                    fieldLabel: __("Firmware"),
                    allowBlank: false
                },
                {
                    name: "status",
                    xtype: "combobox",
                    fieldLabel: __("Status"),
                    allowBlank: false,
                    store: [
                        ["r", "Recommended"],
                        ["a", "Acceptable"],
                        ["n", "Not recommended"],
                        ["d", "Denied"]
                    ],
                    uiStyle: "medium"
                },
                {
                    name: "description",
                    xtype: "textarea",
                    fieldLabel: __("Description"),
                    allowBlank: true
                },
                {
                    name: "management",
                    xtype: "gridfield",
                    fieldLabel: __("Management"),
                    columns: [
                        {
                            text: __("Protocol"),
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
