//---------------------------------------------------------------------
// sa.terminationgroup application
//---------------------------------------------------------------------
// Copyright (C) 2007-2014 The NOC Project
// See LICENSE for details
//---------------------------------------------------------------------
console.debug("Defining NOC.sa.terminationgroup.Application");

Ext.define("NOC.sa.terminationgroup.Application", {
    extend: "NOC.core.ModelApplication",
    requires: [
        "NOC.sa.terminationgroup.Model",
        "NOC.sa.terminationgroup.IPPoolModel",
        "NOC.ip.vrf.LookupField"
    ],
    model: "NOC.sa.terminationgroup.Model",
    search: true,

    initComponent: function() {
        var me = this;
        Ext.apply(me, {
            columns: [
                {
                    text: __("Name"),
                    dataIndex: "name",
                    width: 150
                },
                {
                    text: __("Terminators"),
                    dataIndex: "terminators",
                    width: 200,
                    sortable: false
                },
                {
                    text: __("Access"),
                    dataIndex: "n_access",
                    width: 50,
                    sortable: false
                },
                {
                    text: __("Description"),
                    dataIndex: "description",
                    flex: 1
                }
            ],
            fields: [
                {
                    name: "name",
                    xtype: "textfield",
                    fieldLabel: __("Name"),
                    allowBlank: false
                },
                {
                    name: "terminators",
                    xtype: "displayfield",
                    fieldLabel: __("Terminators"),
                    allowBlank: false
                },
                {
                    name: "description",
                    xtype: "textarea",
                    fieldLabel: __("Description"),
                    allowBlank: true
                }
            ]
        });
        me.callParent();
    },
    inlines: [
        {
            title: "IP Pools",
            model: "NOC.sa.terminationgroup.IPPoolModel",
            columns: [
                {
                    dataIndex: "name",
                    text: __("Pool Name"),
                    editor: "textfield",
                    width: 100
                },
                {
                    dataIndex: "type",
                    text: __("Type"),
                    editor: {
                        xtype: "combobox",
                        store: [
                            ["D", "Dynamic"],
                            ["S", "Static"]
                        ]
                    },
                    width: 70,
                    renderer: NOC.render.Choices({
                        "D": "Dynamic",
                        "S": "Static"
                    })
                },
                {
                    dataIndex: "vrf",
                    text: __("VRF"),
                    editor: "ip.vrf.LookupField",
                    width: 150,
                    renderer: NOC.render.Lookup("vrf")
                },
                {
                    dataIndex: "afi",
                    text: __("AFI"),
                    editor: {
                        xtype: "combobox",
                        store: [
                            ["4", "IPv4"],
                            ["6", "IPv6"]
                        ]
                    },
                    width: 50,
                    renderer: NOC.render.Choices({
                        "4": "IPv4",
                        "6": "IPv6"
                    })
                },
                {
                    dataIndex: "from_address",
                    text: __("From Address"),
                    editor: "textfield",
                    width: 100
                },
                {
                    dataIndex: "to_address",
                    text: __("To address"),
                    editor: "textfield",
                    width: 100
                },
                {
                    dataIndex: "technologies",
                    text: __("Technologies"),
                    editor: "textfield",
                    flex: 1
                }
            ]
        }
    ]
});
