//---------------------------------------------------------------------
// pm.metricset application
//---------------------------------------------------------------------
// Copyright (C) 2007-2014 The NOC Project
// See LICENSE for details
//---------------------------------------------------------------------
console.debug("Defining NOC.pm.metricset.Application");

Ext.define("NOC.pm.metricset.Application", {
    extend: "NOC.core.ModelApplication",
    requires: [
        "NOC.pm.metricset.Model",
        "NOC.pm.storagerule.LookupField",
        "NOC.pm.metrictype.LookupField",
        "NOC.pm.metricset.templates.Effective"
    ],
    model: "NOC.pm.metricset.Model",
    search: true,

    initComponent: function() {
        var me = this;
        Ext.apply(me, {
            columns: [
                {
                    text: "Name",
                    dataIndex: "name",
                    width: 150                },
                {
                    text: "Active",
                    dataIndex: "is_active",
                    renderer: NOC.render.Bool,
                    width: 35
                },
                {
                    text: "Storage Rule",
                    dataIndex: "storage_rule",
                    width: 150,
                    renderer: NOC.render.Lookup("storage_rule")
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
                    fieldLabel: "Name",
                    allowBlank: false
                },
                {
                    name: "is_active",
                    xtype: "checkbox",
                    boxLabel: "Active"
                },
                {
                    name: "storage_rule",
                    xtype: "pm.storagerule.LookupField",
                    fieldLabel: "Storage Rule",
                    allowBlank: false
                },
                {
                    name: "description",
                    xtype: "textarea",
                    fieldLabel: "Description"
                },
                {
                    name: "metrics",
                    xtype: "gridfield",
                    fieldLabel: "Metrics",
                    columns: [
                        {
                            text: "Type",
                            dataIndex: "metric_type",
                            width: 150,
                            renderer: NOC.render.Lookup("metric_type"),
                            editor: "pm.metrictype.LookupField"
                        },
                        {
                            text: "Active",
                            dataIndex: "is_active",
                            width: 50,
                            renderer: NOC.render.Bool,
                            editor: "checkbox"
                        },
                        {
                            text: "Low. Error",
                            dataIndex: "low_error",
                            width: 100,
                            align: "right",
                            editor: "numberfield"
                        },
                        {
                            text: "Low. Warn",
                            dataIndex: "low_warn",
                            width: 100,
                            align: "right",
                            editor: "numberfield"
                        },
                        {
                            text: "High. Warn",
                            dataIndex: "high_warn",
                            width: 100,
                            align: "right",
                            editor: "numberfield"
                        },
                        {
                            text: "High. Error",
                            dataIndex: "high_error",
                            width: 100,
                            align: "right",
                            editor: "numberfield"
                        }
                    ]
                }
            ],
            preview: {
                xtype: "NOC.core.RestTemplatePreview",
                previewName: "Effective metrics for {{name}}",
                restUrl: "/pm/metricset/{{id}}/effective/",
                template: me.templates.Effective
            }
        });
        me.callParent();
    }
});
