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
        "NOC.pm.metrictype.Model",
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
                            name: "compose_node",
                            xtype: "cmtext",
                            fieldLabel: __("Compose Node"),
                            labelAlign: "top",
                            allowBlank: false,
                            mode: "json"
                        },
                        {
                            name: "compose_inputs",
                            xtype: "gridfield",
                            fieldLabel: __("Compose Config"),
                            columns: [
                                {
                                    dataIndex: "input_name",
                                    text: __("Name"),
                                    width: 150
                                },
                                {
                                    dataIndex: "metric_type",
                                    text: __("Type"),
                                    width: 70
                                },
                            ]
                        },
                        {
                            name: "compose_metric_type",
                            xtype: "pm.metrictype.LookupField",
                            fieldLabel: __("Compose Metric Type"),
                            allowBlank: true
                        },
                        {
                            name: "activation_node",
                            xtype: "cmtext",
                            fieldLabel: __("Activation Node"),
                            labelAlign: "top",
                            allowBlank: false,
                            mode: "json"
                        },
                        {
                            name: "alarm_node",
                            xtype: "cmtext",
                            fieldLabel: __("Alarm Node"),
                            labelAlign: "top",
                            allowBlank: false,
                            mode: "json"
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
