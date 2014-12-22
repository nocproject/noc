//---------------------------------------------------------------------
// inv.interfaceclassificationrule application
//---------------------------------------------------------------------
// Copyright (C) 2007-2014 The NOC Project
// See LICENSE for details
//---------------------------------------------------------------------
console.debug("Defining NOC.inv.interfaceclassificationrule.Application");

Ext.define("NOC.inv.interfaceclassificationrule.Application", {
    extend: "NOC.core.ModelApplication",
    requires: [
        "NOC.inv.interfaceclassificationrule.Model",
        "NOC.sa.managedobjectselector.LookupField",
        "NOC.inv.interfaceprofile.LookupField",
        "NOC.main.prefixtable.LookupField",
        "NOC.vc.vcfilter.LookupField"
    ],
    model: "NOC.inv.interfaceclassificationrule.Model",
    search: true,
    rowClassField: "row_class",
    initComponent: function() {
        var me = this;
        Ext.apply(me, {
            columns: [
                {
                    text: "Name",
                    dataIndex: "name",
                    width: 150
                },
                {
                    text: "Active",
                    dataIndex: "is_active",
                    renderer: NOC.render.Bool,
                    width: 50
                },
                {
                    text: "Order",
                    dataIndex: "order",
                    width: 50,
                    textAlign: "right"
                },
                {
                    text: "Selector",
                    dataIndex: "selector",
                    width: 150,
                    renderer: NOC.render.Lookup("selector")
                },
                {
                    text: "Profile",
                    dataIndex: "profile",
                    width: 150,
                    renderer: NOC.render.Lookup("profile")
                },
                {
                    text: "Match",
                    dataIndex: "match_expr",
                    width: 200
                },
                {
                    text: "Description",
                    dataIndex: "description",
                    flex: 1
                }
            ],
            fields: [
                {
                    name: "name",
                    xtype: "textfield",
                    fieldLabel: "Name",
                    allowBlank: false
                },
                {
                    name: "is_active",
                    xtype: "checkbox",
                    boxLabel: "Active"
                },
                {
                    name: "order",
                    xtype: "numberfield",
                    fieldLabel: "Order",
                    allowBlank: false,
                    value: 100
                },
                {
                    name: "description",
                    xtype: "textarea",
                    fieldLabel: "Description",
                    allowBlank: true
                },
                {
                    name: "selector",
                    xtype: "sa.managedobjectselector.LookupField",
                    fieldLabel: "Selector",
                    allowBlank: false
                },
                {
                    name: "profile",
                    xtype: "inv.interfaceprofile.LookupField",
                    fieldLabel: "Interface Profile",
                    allowBlank: false
                },
                {
                    name: "match",
                    xtype: "gridfield",
                    fieldLabel: "Match Rules",
                    columns: [
                        {
                            text: "Field",
                            dataIndex: "field",
                            width: 100,
                            editor: {
                                xtype: "combobox",
                                store: [
                                    ["name", "Name"],
                                    ["description", "Description"],
                                    ["ip", "IP Address"],
                                    ["tagged", "Tagged VLAN"],
                                    ["untagged", "Untagged VLAN"]
                                ]
                            }
                        },
                        {
                            text: "Operation",
                            dataIndex: "op",
                            width: 75,
                            editor: {
                                xtype: "combobox",
                                store: [
                                    ["eq", "eq"],
                                    ["regexp", "regexp"],
                                    ["in", "in"],
                                ]
                            }
                        },
                        {
                            text: "Value",
                            dataIndex: "value",
                            width: 150,
                            editor: "textfield"
                        },
                        {
                            text: "Prefix",
                            dataIndex: "prefix_table",
                            editor: {
                                xtype: "main.prefixtable.LookupField",
                                allowBlank: true
                            },
                            renderer: NOC.render.Lookup("prefix_table"),
                            width: 150
                        },
                        {
                            text: "VC Filter",
                            dataIndex: "vc_filter",
                            editor: {
                                xtype: "vc.vcfilter.LookupField",
                                allowBlank: true
                            },
                            renderer: NOC.render.Lookup("vc_filter"),
                            width: 150
                        },
                        {
                            text: "Description",
                            dataIndex: "description",
                            editor: {
                                xtype: "textfield",
                                allowBlank: true
                            },
                            flex: 1
                        }
                    ]
                }
            ]
        });
        me.callParent();
    },
    //
    onMatchSelect: function(field, records, eOpts) {
        var me = this;
        console.log("Field", field);
    }
});
