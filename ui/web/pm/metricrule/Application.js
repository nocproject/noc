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
                    name: "actions",
                    xtype: "listform",
                    fieldLabel: __("Actions"),
                    labelAlign: "top",
                    items: [
                        {
                            name: "metric_action",
                            xtype: "pm.metricaction.LookupField",
                            fieldLabel: __("Metric Action"),
                            listeners: {
                                scope: me,
                                select: me.onSelectQuery
                            },
                            allowBlank: false
                        },
                        {
                            name: "is_active",
                            xtype: "checkbox",
                            boxLabel: __("Active")
                        },
                        {
                            name: "metric_action_params",
                            xtype: "gridfield",
                            fieldLabel: __("Action Params"),
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
                                {
                                    dataIndex: "min_value",
                                    text: __("Min.Value"),
                                    width: 70
                                },
                                {
                                    dataIndex: "max_value",
                                    text: __("Max.Value"),
                                    width: 70
                                },
                                {
                                    dataIndex: "default",
                                    text: __("Default"),
                                    width: 100
                                },
                                {
                                    dataIndex: "description",
                                    text: __("Description"),
                                    flex: 1
                                }
                            ]
                        }
                    ]
                },
                {
                    name: "match",
                    xtype: "listform",
                    fieldLabel: __("Match Rules"),
                    labelAlign: "top",
                    rows: 5,
                    items: [
                        {
                            name: "labels",
                            xtype: "labelfield",
                            fieldLabel: __("Match Labels"),
                            allowBlank: true,
                            isTree: true,
                            filterProtected: false,
                            pickerPosition: "down",
                            uiStyle: "extra",
                            query: {
                                "allow_matched": true
                            }
                        },
                        {
                            name: "exclude_labels",
                            xtype: "labelfield",
                            fieldLabel: __("Exclude Match Labels"),
                            allowBlank: true,
                            isTree: true,
                            filterProtected: false,
                            pickerPosition: "down",
                            uiStyle: "extra",
                            query: {
                                "allow_matched": true
                            }
                        }
                    ]
                }
            ]
        });
        me.callParent();
    },
    //
    onSelectQuery: function(field, record) {
        var me = this,
          queryParamsField = field.up().getForm().findField("metric_action_params");
        if(record && record.isModel) {
            Ext.Ajax.request({
                url: "/pm/metricaction/" + record.get("id") + "/",
                scope: me,
                success: function(response) {
                    var data = Ext.decode(response.responseText);
                    queryParamsField.setValue(data.params);
                }
            })
        } else {
            field.up().up().up().deleteRecord();
        }
    }
});
