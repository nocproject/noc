//---------------------------------------------------------------------
// ip.ippool application
//---------------------------------------------------------------------
// Copyright (C) 2007-2014 The NOC Project
// See LICENSE for details
//---------------------------------------------------------------------
console.debug("Defining NOC.ip.ippool.Application");

Ext.define("NOC.ip.ippool.Application", {
    extend: "NOC.core.ModelApplication",
    requires: [
        "NOC.ip.ippool.Model",
        "NOC.sa.terminationgroup.LookupField",
        "NOC.ip.vrf.LookupField"
    ],
    model: "NOC.ip.ippool.Model",
    initComponent: function() {
        var me = this;
        Ext.apply(me, {
            columns: [
                {
                    text: __("Term. Group"),
                    dataIndex: "termination_group",
                    width: 150,
                    renderer: NOC.render.Lookup("termination_group")
                },
                {
                    text: __("Pool Name"),
                    dataIndex: "name",
                    width: 100
                },
                {
                    text: __("Type"),
                    dataIndex: "type",
                    width: 70,
                    renderer: NOC.render.Choices({
                        "D": "Dynamic",
                        "S": "Static"
                    })
                },
                {
                    text: __("VRF"),
                    dataIndex: "vrf",
                    width: 150,
                    renderer: NOC.render.Lookup("vrf")
                },
                {
                    text: __("AFI"),
                    dataIndex: "afi",
                    width: 50,
                    renderer: NOC.render.Choices({
                        "4": "IPv4",
                        "6": "IPv6"
                    })
                },
                {
                    text: __("From"),
                    dataIndex: "from_address",
                    width: 100
                },
                {
                    text: __("To"),
                    dataIndex: "to_address",
                    width: 100
                },
                {
                    text: __("Technologies"),
                    dataIndex: "technologies",
                    flex: 1
                }
            ],
            fields: [
                {
                    name: "termination_group",
                    xtype: "sa.terminationgroup.LookupField",
                    fieldLabel: __("Termination Group"),
                    allowBlank: false
                },
                {
                    name: "name",
                    xtype: "textfield",
                    fieldLabel: __("Pool Name"),
                    allowBlank: false
                },
                {
                    name: "type",
                    xtype: "combobox",
                    fieldLabel: __("Type"),
                    allowBlank: false,
                    store: [
                        ["D", "Dynamic"],
                        ["S", "Static"]
                    ]
                },
                {
                    name: "vrf",
                    xtype: "ip.vrf.LookupField",
                    fieldLabel: __("VRF"),
                    allowBlank: false
                },
                {
                    name: "afi",
                    xtype: "combobox",
                    fieldLabel: __("Address Family"),
                    allowBlank: false,
                    store: [
                        ["4", "IPv4"],
                        ["6", "IPv6"]
                    ]
                },
                {
                    name: "from_address",
                    xtype: "textfield",
                    fieldLabel: __("From Address"),
                    allowBlank: false
                },
                {
                    name: "to_address",
                    xtype: "textfield",
                    fieldLabel: __("To address"),
                    allowBlank: false
                },
                {
                    name: "technologies",
                    xtype: "textfield",
                    fieldLabel: __("Technologies"),
                    allowBlank: true
                }
            ]
        });
        me.callParent();
    },
    filters: [
        {
            title: __("By Termination Group"),
            name: "termination_group",
            ftype: "lookup",
            lookup: "sa.terminationgroup"
        },
        {
            title: __("By VRF"),
            name: "vrf",
            ftype: "lookup",
            lookup: "ip.vrf"
        }
    ]
});
