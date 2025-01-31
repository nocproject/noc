//---------------------------------------------------------------------
// vc.vlanprofile application
//---------------------------------------------------------------------
// Copyright (C) 2007-2018 The NOC Project
// See LICENSE for details
//---------------------------------------------------------------------
console.debug("Defining NOC.vc.vlanprofile.Application");

Ext.define("NOC.vc.vlanprofile.Application", {
    extend: "NOC.core.ModelApplication",
    requires: [
        "NOC.core.label.LabelField",
        "NOC.vc.vlanprofile.Model",
        "NOC.wf.workflow.LookupField",
        "NOC.main.style.LookupField",
        "NOC.main.ref.vlanrole.LookupField",
        "NOC.main.remotesystem.LookupField"
    ],
    model: "NOC.vc.vlanprofile.Model",
    search: true,
    helpId: "vlan-profile",
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
                    text: __("Workflow"),
                    dataIndex: "workflow",
                    width: 100,
                    renderer: NOC.render.Lookup("workflow")
                },
                {
                    text: __("Provisioning"),
                    dataIndex: "enable_provisioning",
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
                    name: "enable_provisioning",
                    xtype: "checkbox",
                    boxLabel: __("Enable Provisioning")
                },
                {
                    name: "role",
                    xtype: "main.ref.vlanrole.LookupField",
                    fieldLabel: __("Workflow"),
                    allowBlank: false
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
                        "allow_models": "vc.VLANProfile"
                    },
                }
            ]
        });
        me.callParent();
    }
});
