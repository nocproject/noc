//---------------------------------------------------------------------
// vc.l2domain application
//---------------------------------------------------------------------
// Copyright (C) 2007-2021 The NOC Project
// See LICENSE for details
//---------------------------------------------------------------------
console.debug("Defining NOC.vc.l2domain.Application");

Ext.define("NOC.vc.l2domain.Application", {
    extend: "NOC.core.ModelApplication",
    requires: [
        "NOC.core.label.LabelField",
        "NOC.vc.l2domain.Model",
        "NOC.core.StateField",
        "NOC.inv.resourcepool.LookupField",
        "NOC.vc.vlanfilter.LookupField",
        "NOC.vc.vlantemplate.LookupField",
        "NOC.vc.vlanprofile.LookupField",
        "NOC.vc.l2domainprofile.LookupField",
        "NOC.main.remotesystem.LookupField"
    ],
    model: "NOC.vc.l2domain.Model",
    search: true,
    helpId: "l2domain-profile",
    rowClassField: "row_class",

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
                    text: __("State"),
                    dataIndex: "state",
                    width: 150,
                    renderer: NOC.render.Lookup("state")
                },
                {
                    text: __("Obj."),
                    dataIndex: "count",
                    width: 30,
                    align: "right",
                    sortable: false,
                    renderer: NOC.render.Badge
                },
            ],

            fields: [
                {
                    name: "name",
                    xtype: "textfield",
                    fieldLabel: __("Name"),
                    allowBlank: false,
                    uiStyle: "large"
                },
                {
                    name: "description",
                    xtype: "textarea",
                    fieldLabel: __("Description"),
                    allowBlank: true
                },
                {
                    name: "profile",
                    xtype: "vc.l2domainprofile.LookupField",
                    fieldLabel: __("Profile"),
                    allowBlank: false
                },
                {
                    name: "state",
                    xtype: "statefield",
                    fieldLabel: __("State"),
                    allowBlank: false
                },
                {
                    name: "vlan_template",
                    xtype: "vc.vlantemplate.LookupField",
                    fieldLabel: __("VLAN Template"),
                    allowBlank: true
                },
                {
                    name: "default_vlan_profile",
                    xtype: "vc.vlanprofile.LookupField",
                    fieldLabel: __("Default VLAN Profile"),
                    allowBlank: true
                },
                {
                    name: "type",
                    xtype: "combobox",
                    fieldLabel: __("VLAN Discovery Policy"),
                    allowBlank: false,
                    uiStyle: "medium",
                    value: "P",
                    store: [
                        ["P", "Profile"],
                        ["D", "Disable"],
                        ["E", "Enable"],
                        ["S", "Status Only"]
                    ]
                },
                {
                    name: "vlan_discovery_filter",
                    xtype: "vc.vlanfilter.LookupField",
                    fieldLabel: __("VLAN Discovery Filter"),
                    allowBlank: true
                },
                {
                    name: "pools",
                    xtype: "gridfield",
                    fieldLabel: __("VLAN Pools"),
                    columns: [
                        {
                            text: __("Pool"),
                            dataIndex: "pool",
                            width: 200,
                            editor: {
                                xtype: "inv.resourcepool.LookupField"
                            },
                            renderer: NOC.render.Lookup("pool")
                        },
                        {
                            dataIndex: "description",
                            text: __("Description"),
                            editor: "textfield",
                            width: 150
                        },
                        {
                            text: __("VLAN Filter"),
                            dataIndex: "vlan_filter",
                            width: 200,
                            editor: {
                                xtype: "vc.vlanfilter.LookupField"
                            },
                            renderer: NOC.render.Lookup("vlan_filter")
                        }
                    ]
                },
                {
                    xtype: "fieldset",
                    layout: "hbox",
                    title: __("Integration"),
                    defaults: {
                        padding: 4,
                        labelAlign: "top"
                    },
                    items: [
                        {
                            name: "remote_system",
                            xtype: "main.remotesystem.LookupField",
                            fieldLabel: __("Remote System"),
                            allowBlank: true
                        },
                        {
                            name: "remote_id",
                            xtype: "textfield",
                            fieldLabel: __("Remote ID"),
                            allowBlank: true,
                            uiStyle: "medium"
                        },
                        {
                            name: "bi_id",
                            xtype: "displayfield",
                            fieldLabel: __("BI ID"),
                            allowBlank: true,
                            uiStyle: "medium"
                        }
                    ]
                },
                {
                    name: "labels",
                    xtype: "labelfield",
                    fieldLabel: __("Labels"),
                    allowBlank: true,
                    query: {
                        "allow_models": ["vc.L2Domain"]
                    }
                }
            ]
        });
        me.callParent();
    }
});
