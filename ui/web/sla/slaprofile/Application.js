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
        "NOC.pm.metrictype.LookupField"
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
                        }
                    ]
                }
            ]
        });
        me.callParent();
    }
});
