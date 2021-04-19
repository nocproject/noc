//---------------------------------------------------------------------
// sla.slaprofile application
//---------------------------------------------------------------------
// Copyright (C) 2007-2016 The NOC Project
// See LICENSE for details
//---------------------------------------------------------------------
console.debug("Defining NOC.sla.slaprofile.Application");

Ext.define("NOC.sla.slaprofile.Application", {
    extend: "NOC.core.ModelApplication",
    requires: [
        "NOC.sla.slaprofile.Model",
        "NOC.core.LabelField",
        "NOC.main.style.LookupField",
        "NOC.pm.metrictype.LookupField",
        "NOC.main.ref.windowfunction.LookupField",
        "NOC.pm.thresholdprofile.LookupField",
        "NOC.wf.workflow.LookupField",
        "Ext.ux.form.GridField"
    ],
    model: "NOC.sla.slaprofile.Model",
    rowClassField: "row_class",

    initComponent: function() {
        var me = this;
        Ext.apply(me, {
            columns: [
                {
                    text: __("Name"),
                    dataIndex: "name",
                    flex: 1
                },
                {
                    text: __("Labels"),
                    dataIndex: "labels",
                    renderer: NOC.render.LabelField,
                    width: 100
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
                    fieldLabel: __("WorkFlow"),
                    allowBlank: false
                },
                {
                    name: "style",
                    xtype: "main.style.LookupField",
                    fieldLabel: __("Style"),
                    allowBlank: true
                },
                {
                    name: "labels",
                    xtype: "labelfield",
                    fieldLabel: __("Labels"),
                    allowBlank: true,
                    uiStyle: "medium",
                    query: {
                        "enable_slaprofile": true
                    },
                },
                {
                    name: "metrics",
                    xtype: "gridfield",
                    fieldLabel: __("Metrics"),
                    columns: [
                        {
                            text: __("Metric Type"),
                            dataIndex: "metric_type",
                            width: 200,
                            editor: {
                                xtype: "pm.metrictype.LookupField",
                                query: {
                                    "name__startswith": "SLA"
                                }
                            },
                            renderer: NOC.render.Lookup("metric_type")
                        },
                        {
                            text: __("Box"),
                            dataIndex: "enable_box",
                            width: 50,
                            renderer: NOC.render.Bool,
                            editor: "checkbox"
                        },
                        {
                            text: __("Periodic"),
                            dataIndex: "enable_periodic",
                            width: 50,
                            renderer: NOC.render.Bool,
                            editor: "checkbox"
                        },
                        {
                            text: __("Stored"),
                            dataIndex: "is_stored",
                            width: 50,
                            renderer: NOC.render.Bool,
                            editor: "checkbox"
                        },
                        {
                            text: __("Profile"),
                            dataIndex: "threshold_profile",
                            width: 150,
                            editor: {
                                xtype: "pm.thresholdprofile.LookupField"
                            },
                            renderer: NOC.render.Lookup("threshold_profile")
                        }
                    ]
                }
            ]
        });
        me.callParent();
    }
});
