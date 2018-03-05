//---------------------------------------------------------------------
// vc.vpnprofile application
//---------------------------------------------------------------------
// Copyright (C) 2007-2017 The NOC Project
// See LICENSE for details
//---------------------------------------------------------------------
console.debug("Defining NOC.vc.vpnprofile.Application");

Ext.define("NOC.vc.vpnprofile.Application", {
    extend: "NOC.core.ModelApplication",
    requires: [
        "NOC.vc.vpnprofile.Model",
        "NOC.main.style.LookupField",
        "NOC.main.remotesystem.LookupField",
        "NOC.wf.workflow.LookupField",
        "NOC.ip.prefixprofile.LookupField"
    ],
    model: "NOC.vc.vpnprofile.Model",
    rowClassField: "row_class",
    search: true,

    initComponent: function () {
        var me = this;
        Ext.apply(me, {
            columns: [
                {
                    text: __("Name"),
                    dataIndex: "name",
                    width: 150
                },
                {
                    text: __("Type"),
                    dataIndex: "type",
                    width: 100
                },
                {
                    text: __("Workflow"),
                    dataIndex: "workflow",
                    width: 150,
                    renderer: NOC.render.Lookup("workflow")
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
                    name: "type",
                    xtype: "combobox",
                    fieldLabel: __("Type"),
                    store: [
                        ["vrf", "VRF"],
                        ["vxlan", "VxLAN"],
                        ["vpls", "VPLS"],
                        ["vll", "VLL"],
                        ["evpn", "EVPN"],
                        ["ipsec", "IPSec"],
                        ["gre", "GRE"],
                        ["ipip", "IP-IP"]
                    ],
                    allowBlank: false,
                    uiStyle: "medium"
                },
                {
                    name: "description",
                    xtype: "textarea",
                    fieldLabel: __("Description"),
                    allowBlank: true
                },
                {
                    name: "workflow",
                    xtype: "wf.workflow.LookupField",
                    fieldLabel: __("Workflow"),
                    allowBlank: false
                },
                {
                    name: "style",
                    xtype: "main.style.LookupField",
                    fieldLabel: __("Style"),
                    allowBlank: true
                },
                {
                    name: "default_prefix_profile",
                    xtype: "ip.prefixprofile.LookupField",
                    fieldLabel: __("Default Prefix Profile"),
                    allowBlank: true
                },
                {
                    xtype: "fieldset",
                    layout: "hbox",
                    title: __("Integration"),
                    defaults: {
                        padding: 4,
                        labelAlign: "right"
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
                    name: "tags",
                    xtype: "tagsfield",
                    fieldLabel: __("Tags"),
                    allowBlank: true
                }
            ]
        });
        me.callParent();
    }
});
