//---------------------------------------------------------------------
// phone.phonerangeprofile application
//---------------------------------------------------------------------
// Copyright (C) 2007-2018 The NOC Project
// See LICENSE for details
//---------------------------------------------------------------------
console.debug("Defining NOC.phone.phonerangeprofile.Application");

Ext.define("NOC.phone.phonerangeprofile.Application", {
    extend: "NOC.core.ModelApplication",
    requires: [
        "NOC.phone.phonerangeprofile.Model",
        "NOC.main.style.LookupField",
        "NOC.wf.workflow.LookupField"
    ],
    model: "NOC.phone.phonerangeprofile.Model",
    search: true,
    helpId: "reference-phonerange-profile",
    rowClassField: "row_class",

    initComponent: function() {
        var me = this;
        Ext.apply(me, {
            columns: [
                {
                    text: "Name",
                    dataIndex: "name",
                    width: 100
                },
                {
                    text: __("Workflow"),
                    dataIndex: "workflow",
                    width: 150,
                    renderer: NOC.render.Lookup("workflow")
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
                    name: "cooldown",
                    xtype: "numberfield",
                    fieldLabel: __("Cooldown"),
                    uiStyle: "small",
                    minValue: 0,
                    maxValue: 9999,
                    allowBlank: false
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
                }
            ]
        });
        me.callParent();
    },
    filters: [
        {
            title: __("By Workflow"),
            name: "workflow",
            ftype: "lookup",
            lookup: "wf.workflow"
        }
    ]
});
