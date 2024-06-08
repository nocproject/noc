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
        "NOC.core.label.LabelField",
        "NOC.main.style.LookupField",
        "NOC.pm.metrictype.LookupField",
        "NOC.main.ref.windowfunction.LookupField",
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
                    allowBlank: true
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
                        "allow_models": ["sla.SLAProfile"]
                    },
                },
                {
                    xtype: "container",
                    layout: "hbox",
                    defaults: {
                        padding: "0 8 0 0"
                    },
                    items: [
                        {
                            name: "metrics_default_interval",
                            xtype: "numberfield",
                            fieldLabel: __("Default Interval, sec"),
                            labelWidth: 200,
                            allowBlank: false,
                            uiStyle: "small",
                            minValue: 0,
                            listeners: {
                                scope: me,
                                change: function(_item, newValue, oldValue, eOpts) {
                                    me.form.findField("metrics_default_interval_calculated").setValue(newValue);
                                }
                            }
                        },
                        {
                            name: 'metrics_default_interval_calculated',
                            xtype: 'displayfield',
                            renderer: NOC.render.Duration
                        }
                    ]
                },
                {
                  name: "metrics_interval_buckets",
                  xtype: "numberfield",
                  fieldLabel: __("Metrics interval Buckets"),
                  allowBlank: true,
                  uiStyle: "medium",
                  minValue: 0
                },
                {
                    name: "raise_alarm_to_target",
                    xtype: "checkbox",
                    boxLabel: __("Raise Alarm to target"),
                    allowBlank: true
                },
                {
                  name: "test_packets_num",
                  xtype: "numberfield",
                  fieldLabel: __("Number Packets on Test"),
                  allowBlank: true,
                  uiStyle: "medium",
                  minValue: 1,
                  maxValue: 60000
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
                            text: __("Stored"),
                            dataIndex: "is_stored",
                            width: 50,
                            renderer: NOC.render.Bool,
                            editor: "checkbox"
                        },
                        {
                            text: __("Interval"),
                            dataIndex: "interval",
                            editor: {
                                xtype: "numberfield",
                                minValue: 0,
                                defaultValue: 300,
                            }
                        }
                    ]
                }
            ]
        });
        me.callParent();
    }
});
