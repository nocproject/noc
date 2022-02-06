//---------------------------------------------------------------------
// pm.metricaction application
//---------------------------------------------------------------------
// Copyright (C) 2007-2022 The NOC Project
// See LICENSE for details
//---------------------------------------------------------------------
console.debug("Defining NOC.pm.metricaction.Application");

Ext.define("NOC.pm.metricaction.Application", {
    extend: "NOC.core.ModelApplication",
    requires: [
        "NOC.pm.metricaction.Model",
        "NOC.core.JSONPreview",
        "NOC.pm.metrictype.LookupField",
        "NOC.fm.alarmclass.LookupField",
        "NOC.core.ListFormField",
        "Ext.ux.form.GridField"
    ],
    model: "NOC.pm.metricaction.Model",
    search: true,

    initComponent: function() {
        var me = this;

        // JSON Panel
        me.jsonPanel = Ext.create("NOC.core.JSONPreview", {
            app: me,
            restUrl: new Ext.XTemplate('/pm/metricaction/{id}/json/'),
            previewName: new Ext.XTemplate('Metric Action: {name}')
        });

        me.ITEM_JSON = me.registerItem(me.jsonPanel);

        Ext.apply(me, {
            columns: [
                {
                    text: __("Name"),
                    dataIndex: "name",
                    width: 150
                },
                {
                    text: __("Builtin"),
                    dataIndex: "is_builtin",
                    renderer: NOC.render.Bool,
                    width: 50,
                    sortable: false
                },
                {
                    text: __("Description"),
                    dataIndex: "description",
                    flex: 1
                }
            ],

            fields: [
                {
                    name: "name",
                    xtype: "textfield",
                    fieldLabel: __("Name"),
                    regex: /^[a-zA-Z0-9\-\_ ]+( \| [a-zA-Z0-9\-\_ ]+)*$/
                },
                {
                    name: "uuid",
                    xtype: "displayfield",
                    fieldLabel: __("UUID")
                },
                {
                    name: "description",
                    xtype: "textarea",
                    fieldLabel: __("Description"),
                    allowBlank: true
                },
                {
                    name: "metric_type",
                    xtype: "pm.metrictype.LookupField",
                    fieldLabel: __("Metric Type"),
                    allowBlank: false
                },
                {
                    name: "params",
                    xtype: "gridfield",
                    fieldLabel: __("Parameters"),
                    labelAlign: "top",
                    columns: [
                        {
                            dataIndex: "name",
                            text: __("Name"),
                            editor: "textfield",
                            width: 150
                        },
                        {
                            dataIndex: "description",
                            text: __("Description"),
                            editor: "textfield",
                            flex: 1
                        }
                    ]
                },
                {
                    name: "actions",
                    xtype: "listform",
                    fieldLabel: __("Actions"),
                    labelAlign: "top",
                    items: [
                        {
                            xtype: "fieldset",
                            title: __("Compose Node"),
                            layout: "anchor",
                            defaults: {
                                labelAlign: "top",
                                collapsible: false,
                                collapsed: false,
                                padding: 4
                            },
                            items: [
                                {
                                    name: "compose_node",
                                    xtype: "combobox",
                                    fieldLabel: __("Activation Node"),
                                    allowBlank: true,
                                    defaultValue: "",
                                    store: [
                                        ["div", __("Divide")],
                                        ["", __("Disable")],
                                    ],
                                },
                                {
                                    name: "compose_inputs",
                                    xtype: "gridfield",
                                    fieldLabel: __("Compose Config"),
                                    columns: [
                                        {
                                            dataIndex: "metric_type",
                                            text: __("Type"),
                                            editor: {
                                                xtype: "pm.metrictype.LookupField"
                                            },
                                            renderer: NOC.render.Lookup("metric_type"),
                                            width: 200
                                        },
                                        {
                                            dataIndex: "input_name",
                                            text: __("Name"),
                                            editor: "textfield",
                                            width: 150
                                        },

                                    ]
                                },
                                {
                                    name: "compose_metric_type",
                                    xtype: "pm.metrictype.LookupField",
                                    fieldLabel: __("Compose Metric Type"),
                                    allowBlank: true
                                },
                            ]
                        },
                        {
                            xtype: "fieldset",
                            title: __("Activation Node"),
                            layout: "anchor",
                            allowBlank: true,
                            defaults: {
                                labelAlign: "top",
                                collapsible: false,
                                collapsed: false,
                                padding: 4
                            },
                            items: [
                                {
                                    name: "activation_node",
                                    xtype: "combobox",
                                    fieldLabel: __("Activation Node"),
                                    allowBlank: false,
                                    defaultValue: "",
                                    store: [
                                        ["percentile", __("Percentile")],
                                        ["", __("Disable")],
                                    ],
                                },
                                {
                                    name: "activation_config",
                                    xtype: "gridfield",
                                    fieldLabel: __("Activation Config"),
                                    columns: [
                                        {
                                            dataIndex: "name",
                                            text: __("Param"),
                                            editor: "textfield",
                                            width: 200
                                        },
                                        {
                                            dataIndex: "value",
                                            text: __("Value"),
                                            editor: "textfield",
                                            width: 150
                                        },

                                    ]
                                },
                            ]
                        },
                        {
                            xtype: "fieldset",
                            title: __("Alarm Node"),
                            layout: "hbox",
                            defaults: {
                                labelAlign: "top",
                                collapsible: false,
                                collapsed: false,
                                padding: 4
                            },
                            items: [
                                {
                                    name: "alarm_node",
                                    xtype: "combobox",
                                    fieldLabel: __("Alarm Node"),
                                    allowBlank: false,
                                    defaultValue: "",
                                    store: [
                                        ["alarm", __("Alarm")],
                                        ["", __("Disable")],
                                    ],
                                },
                                {
                                    name: "alarm_class",
                                    xtype: "fm.alarmclass.LookupField",
                                    fieldLabel: __("Alarm Class"),
                                    allowBlank: true
                                },
                                {
                                    name: "activation_level",
                                    xtype: "textfield",
                                    fieldLabel: __("Activation Level"),
                                    allowBlank: false,
                                    defaultValue: "1.0",
                                    vtype: "float"
                                },
                                {
                                    name: "deactivation_level",
                                    xtype: "textfield",
                                    fieldLabel: __("Deactivation Level"),
                                    allowBlank: true,
                                    vtype: "float"
                                },

                            ]
                        },
                    ]
                }
            ],
            formToolbar: [
                {
                    text: __("JSON"),
                    glyph: NOC.glyph.file,
                    tooltip: __("Show JSON"),
                    hasAccess: NOC.hasPermission("read"),
                    scope: me,
                    handler: me.onJSON
                }
            ]
        });
        me.callParent();
    },
    //
    onJSON: function() {
        var me = this;
        me.showItem(me.ITEM_JSON);
        me.jsonPanel.preview(me.currentRecord);
    }
});
