//---------------------------------------------------------------------
// crm.subscriberprofile application
//---------------------------------------------------------------------
// Copyright (C) 2007-2017 The NOC Project
// See LICENSE for details
//---------------------------------------------------------------------
console.debug("Defining NOC.crm.subscriberprofile.Application");

Ext.define("NOC.crm.subscriberprofile.Application", {
    extend: "NOC.core.ModelApplication",
    requires: [
        "NOC.core.label.LabelField",
        "NOC.crm.subscriberprofile.Model",
        "NOC.main.style.LookupField",
        "NOC.main.ref.glyph.LookupField",
        "NOC.wf.workflow.LookupField",
        "NOC.main.remotesystem.LookupField"
    ],
    model: "NOC.crm.subscriberprofile.Model",
    search: true,
    helpId: "reference-subscriber-profile",
    rowClassField: "row_class",

    initComponent: function() {
        var me = this;
        Ext.apply(me, {
            columns: [
                {
                    text: __("Glyph"),
                    dataIndex: "glyph",
                    width: 25,
                    renderer: function(v) {
                        if(v !== undefined && v !== "")
                        {
                            return "<i class='" + v + "'></i>";
                        } else {
                            return "";
                        }
                    }
                },
                {
                    text: __("Name"),
                    dataIndex: "name",
                    flex: 1
                },
                {
                    text: __("Workflow"),
                    dataIndex: "workflow",
                    width: 150,
                    renderer: NOC.render.Lookup("workflow")
                },
                {
                    text: __("Labels"),
                    dataIndex: "labels",
                    width: 150,
                    render: NOC.render.LabelField
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
                    allowBlank: true,
                    uiStyle: "expand"
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
                    name: "glyph",
                    xtype: "main.ref.glyph.LookupField",
                    fieldLabel: __("Icon"),
                    allowBlank: true,
                    uiStyle: "large"
                },
                {
                    name: "display_order",
                    xtype: "numberfield",
                    fieldLabel: __("Display Order"),
                    uiStyle: "small",
                    minValue: 0,
                    allowBlank: false
                },
                {
                    name: "show_in_summary",
                    xtype: "checkbox",
                    boxLabel: __("Show in summary"),
                    allowBlank: true
                },
                {
                    name: "weight",
                    xtype: "numberfield",
                    fieldLabel: __("Alarm weight"),
                    allowBlank: true,
                    uiStyle: "small"
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
                    name: "labels",
                    xtype: "labelfield",
                    fieldLabel: __("Labels"),
                    allowBlank: true,
                    query: {
                        "allow_models": ["crm.SubscriberProfile", "crl.Subscriber"]
                    },
                }
            ]
        });
        me.callParent();
    }
});
