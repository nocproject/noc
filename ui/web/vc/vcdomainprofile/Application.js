//---------------------------------------------------------------------
// vc.vcdomainprofile application
//---------------------------------------------------------------------
// Copyright (C) 2007-2017 The NOC Project
// See LICENSE for details
//---------------------------------------------------------------------
console.debug("Defining NOC.vc.vcdomainprofile.Application");

Ext.define("NOC.vc.vcdomainprofile.Application", {
    extend: "NOC.core.ModelApplication",
    requires: [
        "NOC.vc.vcdomainprofile.Model",
        "NOC.vc.vcfilter.LookupField",
        "NOC.main.style.LookupField",
        "NOC.wf.workflow.LookupField"
    ],
    model: "NOC.vc.vcdomainprofile.Model",
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
                    width: 120
                },
                {
                    text: __("Workflow"),
                    dataIndex: "default_vc_workflow",
                    width: 150,
                    renderer: NOC.render.Lookup("default_vc_workflow")
                },
                {
                    text: __("VLAN Discovery"),
                    dataIndex: "enable_vlan_discovery",
                    width: 50,
                    renderer: NOC.render.Bool
                },
                {
                    text: __("VLAN Provisioning"),
                    dataIndex: "enable_vlan_provisioning",
                    width: 50,
                    renderer: NOC.render.Bool
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
                    allowBlank: false,
                    uiStyle: "medium",
                    store: [
                        [
                            ["q", "802.1Q VLAN"],
                            ["Q", "802.1ad Q-in-Q"],
                            ["D", "FR DLCI"],
                            ["M", "MPLS"],
                            ["A", "ATM VCI/VPI"],
                            ["X", "X.25 group/channel"]
                        ]
                    ]
                },
                {
                    name: "description",
                    xtype: "textarea",
                    fieldLabel: __("Description"),
                    allowBlank: true
                },
                {
                    name: "default_vc_workflow",
                    xtype: "wf.workflow.LookupField",
                    fieldLabel: __("Default VC Workflow"),
                    allowBlank: false
                },
                {
                    name: "style",
                    xtype: "main.style.LookupField",
                    fieldLabel: __("Style"),
                    allowBlank: true
                },
                {
                    name: "enable_vlan_discovery",
                    xtype: "checkbox",
                    boxLabel: __("VLAN Discovery"),
                    allowBlank: true
                },
                {
                    name: "enable_vlan_provisioning",
                    xtype: "checkbox",
                    boxLabel: __("VLAN Provisioning"),
                    allowBlank: true
                },
                {
                    name: "vlan_provisioning_filter",
                    xtype: "vc.vcfilter.LookupField",
                    fieldLabel: __("VLAN Provisioning Filter"),
                    allowBlank: true
                }
            ]
        });
        me.callParent();
    }
});
