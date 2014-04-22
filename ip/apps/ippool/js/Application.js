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
                    text: "Term. Group",
                    dataIndex: "termination_group",
                    width: 150,
                    renderer: NOC.render.Lookup("termination_group")
                },
                {
                    text: "Pool Name",
                    dataIndex: "name",
                    width: 100
                },
                {
                    text: "Type",
                    dataIndex: "type",
                    width: 70,
                    renderer: NOC.render.Choices({
                        "D": "Dynamic",
                        "S": "Static"
                    })
                },
                {
                    text: "VRF",
                    dataIndex: "vrf",
                    width: 150,
                    renderer: NOC.render.Lookup("vrf")
                },
                {
                    text: "AFI",
                    dataIndex: "afi",
                    width: 50,
                    renderer: NOC.render.Choices({
                        "4": "IPv4",
                        "6": "IPv6"
                    })
                },
                {
                    text: "From",
                    dataIndex: "from_address",
                    width: 100
                },
                {
                    text: "To",
                    dataIndex: "to_address",
                    width: 100
                },
                {
                    text: "Technologies",
                    dataIndex: "technologies",
                    flex: 1
                }
            ],
            fields: [
                {
                    name: "termination_group",
                    xtype: "sa.terminationgroup.LookupField",
                    fieldLabel: "Termination Group",
                    allowBlank: false
                },
                {
                    name: "name",
                    xtype: "textfield",
                    fieldLabel: "Pool Name",
                    allowBlank: false
                },
                {
                    name: "type",
                    xtype: "combobox",
                    fieldLabel: "Type",
                    allowBlank: false,
                    store: [
                        ["D", "Dynamic"],
                        ["S", "Static"]
                    ]
                },
                {
                    name: "vrf",
                    xtype: "ip.vrf.LookupField",
                    fieldLabel: "VRF",
                    allowBlank: false
                },
                {
                    name: "afi",
                    xtype: "combobox",
                    fieldLabel: "Address Family",
                    allowBlank: false,
                    store: [
                        ["4", "IPv4"],
                        ["6", "IPv6"]
                    ]
                },
                {
                    name: "from_address",
                    xtype: "textfield",
                    fieldLabel: "From Address",
                    allowBlank: false
                },
                {
                    name: "to_address",
                    xtype: "textfield",
                    fieldLabel: "To address",
                    allowBlank: false
                },
                {
                    name: "technologies",
                    xtype: "textfield",
                    fieldLabel: "Technologies",
                    allowBlank: true
                }
            ]
        });
        me.callParent();
    },
    filters: [
        {
            title: "By Termination Group",
            name: "termination_group",
            ftype: "lookup",
            lookup: "sa.terminationgroup"
        },
        {
            title: "By VRF",
            name: "vrf",
            ftype: "lookup",
            lookup: "ip.vrf"
        }
    ]
});
