//---------------------------------------------------------------------
// pm.metricrule application
//---------------------------------------------------------------------
// Copyright (C) 2007-2022 The NOC Project
// See LICENSE for details
//---------------------------------------------------------------------
console.debug("Defining NOC.pm.metricrule.Application");

Ext.define("NOC.pm.metricrule.Application", {
    extend: "NOC.core.ModelApplication",
    requires: [
        "NOC.pm.metricrule.Model",
        "NOC.pm.metricaction.LookupField",
        "NOC.core.label.LabelField",
        "NOC.core.ListFormField",
        "Ext.ux.form.GridField"
    ],
    model: "NOC.pm.metricrule.Model",
    search: true,

    initComponent: function() {
        var me = this;
        Ext.apply(me, {
            columns: [
                {
                    text: __("Name"),
                    dataIndex: "name",
                    width: 100,
                    align: "left"
                },
                {
                    text: __("Active"),
                    dataIndex: "is_active",
                    renderer: NOC.render.Bool,
                    width: 100,
                    align: "left"
                }
            ],

            fields: [
                {
                    name: 'name',
                    xtype: 'textfield',
                    fieldLabel: __('Name'),
                    allowBlank: false,
                    uiStyle: 'large'
                },
                {
                    name: "is_active",
                    xtype: "checkbox",
                    boxLabel: __("Active")
                },
                {
                    name: 'description',
                    xtype: 'textarea',
                    fieldLabel: __('Description'),
                    uiStyle: 'large'
                },
                {
                    name: "match_labels",
                    xtype: "labelfield",
                    fieldLabel: __("Match Labels"),
                    allowBlank: true,
                    isTree: true,
                    pickerPosition: "down",
                    uiStyle: "extra",
                    query: {
                        "allow_matched": true
                    }
                },
                {
                    name: "items",
                    xtype: "listform",
                    fieldLabel: __("Items"),
                    labelAlign: "top",
                    items: [
                        {
                            name: "metric_action",
                            xtype: "pm.metricaction.LookupField",
                            fieldLabel: __("Metric Action"),
                            allowBlank: false
                        },
                        {
                            name: "match_labels",
                            xtype: "labelfield",
                            fieldLabel: __("Match Labels"),
                            allowBlank: true,
                            isTree: true,
                            pickerPosition: "down",
                            uiStyle: "extra",
                            query: {
                                "allow_matched": true
                            }
                        },
                        {
                            name: "is_active",
                            xtype: "checkbox",
                            boxLabel: __("Active")
                        },
                        {
                            name: "query_params",
                            xtype: "gridfield",
                            fieldLabel: __("Query Parameters"),
                            columns: [
                                {
                                    dataIndex: "name",
                                    text: __("Name"),
                                    width: 150
                                },
                                {
                                    dataIndex: "type",
                                    text: __("Type"),
                                    width: 70
                                },
                                {
                                    dataIndex: "value",
                                    text: __("Value"),
                                    editor: "textfield",
                                    width: 200
                                },
                            ]
                        }
                    ]
                }
            ]
        });
        me.callParent();
    },
    //
});
