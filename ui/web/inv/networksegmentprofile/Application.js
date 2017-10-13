//---------------------------------------------------------------------
// inv.networksegmentprofile application
//---------------------------------------------------------------------
// Copyright (C) 2007-2017 The NOC Project
// See LICENSE for details
//---------------------------------------------------------------------
console.debug("Defining NOC.inv.networksegmentprofile.Application");

Ext.define("NOC.inv.networksegmentprofile.Application", {
    extend: "NOC.core.ModelApplication",
    requires: [
        "NOC.inv.networksegmentprofile.Model",
        "NOC.inv.networksegmentprofile.LookupField"
    ],
    model: "NOC.inv.networksegmentprofile.Model",
    initComponent: function() {
        var me = this;
        Ext.apply(me, {
            columns: [
                {
                    text: __("Name"),
                    dataIndex: "name",
                    flex: 1
                }
            ],

            fields: [
                {
                    name: "name",
                    xtype: "textfield",
                    fieldLabel: __("Name"),
                    allowBlank: false,
                    uiStyle: "medium"
                },
                {
                    name: "description",
                    xtype: "textarea",
                    fieldLabel: __("Description"),
                    allowBlank: false
                },
                {
                    name: "mac_discovery_interval",
                    xtype: "numberfield",
                    fieldLabel: __("MAC discovery interval"),
                    allowBlank: false,
                    uiStyle: "medium"
                },
                {
                    name: "autocreated_profile",
                    xtype: "inv.networksegmentprofile.LookupField",
                    fieldLabel: __("Autocreated Profile"),
                    allowBlank: true
                },
                {
                    name: "mac_restrict_to_management_vlan",
                    xtype: "checkbox",
                    boxLabel: __("Restrict MAC to management vlan"),
                    allowBlank: true
                },
                {
                    name: "management_vlan",
                    xtype: "numberfield",
                    fieldLabel: __("Management VLAN"),
                    allowBlank: true,
                    uiStyle: "medium",
                    emptyText: __("Not Configured"),
                    submitEmptyText: false,
                    minValue: 1,
                    maxValue: 4095
                },
                {
                    name: "multicast_vlan",
                    xtype: "numberfield",
                    fieldLabel: __("Multicast VLAN"),
                    allowBlank: true,
                    uiStyle: "medium",
                    emptyText: __("Not Configured"),
                    submitEmptyText: false,
                    minValue: 1,
                    maxValue: 4095
                },
                {
                    name: "enable_lost_redundancy",
                    xtype: "checkbox",
                    boxLabel: __("Enable lost redundancy check")
                },
                {
                    name: "horizontal_transit_policy",
                    xtype: "combobox",
                    fieldLabel: __("Horizontal Transit Policy"),
                    allowBlank: false,
                    store: [
                        ["E", __("Always Enable")],
                        ["C", __("Calculate")],
                        ["D", __("Disable")]
                    ],
                    uiStyle: "medium"
                },
                {
                    name: "topology_methods",
                    xtype: "gridfield",
                    fieldLabel: __("Topology methods"),
                    columns: [
                        {
                            text: __("Method"),
                            dataIndex: "method",
                            width: 100,
                            editor: {
                                xtype: "combobox",
                                store: [
                                    ["custom", "Custom ..."],
                                    ["handler", "Handler ..."],
                                    ["cdp", "CDP"],
                                    ["huawei_ndp", "Huawei NDP"],
                                    ["lacp", "LACP"],
                                    ["lldp", "LLDP"],
                                    ["oam", "OAM"],
                                    ["stp", "STP"],
                                    ["udld", "UDLD"],
                                    ["mac", "MAC"],
                                    ["nri", "NRI"]
                                ]
                            }
                        },
                        {
                            text: __("Active"),
                            dataIndex: "is_active",
                            editor: "checkbox",
                            renderer: NOC.render.Bool,
                            flex: 1
                        }
                    ]
                }
            ]
        });
        me.callParent();
    }
});
