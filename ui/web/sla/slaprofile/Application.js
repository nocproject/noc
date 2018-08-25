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
        "NOC.main.style.LookupField",
        "NOC.pm.metrictype.LookupField",
        "NOC.main.ref.windowfunction.LookupField",
        "NOC.pm.thresholdprofile.LookupField"
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
                    name: "style",
                    xtype: "main.style.LookupField",
                    fieldLabel: __("Style"),
                    allowBlank: true
                },
                {
                    name: "metrics",
                    xtype: "gridfield",
                    fieldLabel: __("Metrics"),
                    columns: [
                        {
                            text: __("Metric Type"),
                            dataIndex: "metric_type",
                            flex: 1,
                            editor: "pm.metrictype.LookupField",
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
                            text: __("Window"),
                            dataIndex: "window",
                            width: 50,
                            editor: "textfield"
                        },
                        {
                            text: __("Window Type"),
                            dataIndex: "window_type",
                            width: 70,
                            renderer: NOC.render.Choices({
                                m: __("Measurements"),
                                t: __("Seconds")
                            }),
                            editor: {
                                xtype: "combobox",
                                store: [
                                    ["m", __("Measurements")],
                                    ["t", __("Seconds")]
                                ]
                            }
                        },
                        {
                            text: __("Window Function"),
                            dataIndex: "window_function",
                            width: 70,
                            editor: {
                                xtype: "main.ref.windowfunction.LookupField"
                            }
                        },
                        {
                            text: __("Config"),
                            dataIndex: "window_config",
                            width: 70,
                            editor: "textfield"
                        },
                        {
                            text: __("Low Error"),
                            dataIndex: "low_error",
                            width: 60,
                            editor: "textfield",
                            align: "right",
                            renderer: NOC.render.Size
                        },
                        {
                            text: __("Low Warn"),
                            dataIndex: "low_warn",
                            width: 60,
                            editor: "textfield",
                            align: "right",
                            renderer: NOC.render.Size
                        },
                        {
                            text: __("High Warn"),
                            dataIndex: "high_warn",
                            width: 60,
                            editor: "textfield",
                            align: "right",
                            renderer: NOC.render.Size
                        },
                        {
                            text: __("High Error"),
                            dataIndex: "high_error",
                            width: 60,
                            editor: "textfield",
                            align: "right",
                            renderer: NOC.render.Size
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
