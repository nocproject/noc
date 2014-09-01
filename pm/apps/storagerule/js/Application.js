//---------------------------------------------------------------------
// pm.storagerule application
//---------------------------------------------------------------------
// Copyright (C) 2007-2014 The NOC Project
// See LICENSE for details
//---------------------------------------------------------------------
console.debug("Defining NOC.pm.storagerule.Application");

Ext.define("NOC.pm.storagerule.Application", {
    extend: "NOC.core.ModelApplication",
    requires: [
        "NOC.pm.storagerule.Model",
        "NOC.pm.storage.LookupField"
    ],
    model: "NOC.pm.storagerule.Model",
    precisionUnits: [
        ["s", "Seconds"],
        ["m", "Minutes"],
        ["h", "Hours"],
        ["d", "Day"],
        ["w", "Week"],
        ["y", "Year"]
    ],
    search: true,
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
                    text: "Storage",
                    dataIndex: "storage",
                    width: 100,
                    renderer: NOC.render.Lookup("storage")
                },
                {
                    text: "Aggregation",
                    dataIndex: "aggregation_method",
                    width: 100
                },
                {
                    text: "Retention",
                    dataIndex: "retention_text",
                    sortable: false,
                    flex: 1
                },
                {
                    text: "Interval",
                    dataIndex: "interval",
                    width: 50,
                    sortable: false,
                    align: "right"
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
                    name: "storage",
                    xtype: "pm.storage.LookupField",
                    fieldLabel: "Storage",
                    allowBlank: false
                },
                {
                    name: "aggregation_method",
                    xtype: "combobox",
                    fieldLabel: "Aggregation",
                    store: [
                        ["average", "Average"],
                        ["min", "Min"],
                        ["max", "Max"],
                        ["last", "Last"],
                        ["sum", "Sum"]
                    ]
                },
                {
                    name: "description",
                    xtype: "textarea",
                    fieldLabel: "Description",
                    allowBlank: true
                },
                {
                    name: "xfilesfactor",
                    xtype: "numberfield",
                    fieldLabel: "XFilesFactor",
                    minValue: 0.0,
                    maxValue: 1.0,
                    step: 0.1
                },
                {
                    name: "retentions",
                    xtype: "gridfield",
                    fieldLabel: "Retentions",
                    columns: [
                        {
                            text: "Precision",
                            dataIndex: "precision",
                            width: 100,
                            editor: {
                                xtype: "numberfield",
                                minValue: 0,
                                allowDecimals: false
                            }
                        },
                        {
                            text: "Units",
                            dataIndex: "precision_unit",
                            width: 100,
                            editor: {
                                xtype: "combobox",
                                store: me.precisionUnits
                            },
                            renderer: NOC.render.ArrayChoices(me.precisionUnits)
                        },
                        {
                            text: "Duration",
                            dataIndex: "duration",
                            width: 100,
                            editor: {
                                xtype: "numberfield",
                                minValue: 0,
                                allowDecimals: false
                            }
                        },
                        {
                            text: "Units",
                            dataIndex: "duration_unit",
                            width: 100,
                            editor: {
                                xtype: "combobox",
                                store: me.precisionUnits
                            },
                            renderer: NOC.render.ArrayChoices(me.precisionUnits)
                        }
                    ]
                }
            ]
        });
        me.callParent();
    }
});
