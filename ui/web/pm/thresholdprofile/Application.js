//---------------------------------------------------------------------
// pm.thresholdprofile application
//---------------------------------------------------------------------
// Copyright (C) 2007-2018 The NOC Project
// See LICENSE for details
//---------------------------------------------------------------------
console.debug("Defining NOC.pm.thresholdprofile.Application");

Ext.define("NOC.pm.thresholdprofile.Application", {
    extend: "NOC.core.ModelApplication",
    requires: [
        "NOC.core.JSONPreview",
        "NOC.pm.thresholdprofile.Model",
        "NOC.main.ref.windowfunction.LookupField",
        "NOC.core.ListFormField",
        "NOC.fm.alarmclass.LookupField",
        "NOC.fm.eventclass.LookupField",
        "NOC.main.template.LookupField",
        "NOC.main.handler.LookupField"
    ],
    model: "NOC.pm.thresholdprofile.Model",
    search: true,

    initComponent: function() {
        var me = this;

        // JSON Panel
        me.jsonPanel = Ext.create("NOC.core.JSONPreview", {
            app: me,
            restUrl: new Ext.XTemplate('/pm/thresholdprofile/{id}/json/'),
            previewName: new Ext.XTemplate('Threshold Profile: {name}')
        });

        me.ITEM_JSON = me.registerItem(me.jsonPanel);

        Ext.apply(me, {
            columns: [
                {
                    text: "Name",
                    dataIndex: "name",
                    flex: 1
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
                    name: "umbrella_filter_handler",
                    xtype: "textfield",
                    fieldLabel: __("Umbrella Filter Handler"),
                    allowBlank: true,
                    uiStyle: "large"
                    // vtype: "handler"
                },
                {
                    xtype: "fieldset",
                    title: __("Window Settings"),
                    layout: "hbox",
                    defaults: {
                        padding: 4,
                        labelAlign: "right"
                    },
                    items: [
                        {
                            name: "window_type",
                            xtype: "combobox",
                            fieldLabel: __("Window Type"),
                            allowBlank: false,
                            store: [
                                ["m", __("Measurements")],
                                ["t", __("Seconds")]
                            ]
                        },
                        {
                            name: "window",
                            xtype: "numberfield",
                            fieldLabel: __("Window"),
                            minValue: 1,
                            allowBlank: false,
                            uiStyle: "small"
                        },
                        {
                            name: "window_function",
                            xtype: "main.ref.windowfunction.LookupField",
                            fieldLabel: __("Window Function"),
                            allowBlank: false
                        },
                        {
                            name: "window_config",
                            xtype: "textfield",
                            fieldLabel: __("Config"),
                            allowBlank: true
                        },
                        {
                            name: "value_handler",
                            xtype: "textfield",
                            fieldLabel: __("Value Handler"),
                            allowBlank: true
                        }
                    ]
                },
                {
                    name: "thresholds",
                    xtype: "listform",
                    fieldLabel: __("Thresholds"),
                    items: [
                        {
                            name: "op",
                            xtype: "combobox",
                            fieldLabel: __("Operation"),
                            store: [
                                ["<", "<"],
                                ["<=", "<="],
                                [">=", ">="],
                                [">", ">"]
                            ],
                            allowBlank: false,
                            uiStyle: "small"
                        },
                        {
                            name: "value",
                            xtype: "textfield",
                            fieldLabel: __("Value"),
                            allowBlank: false,
                            vtype: "float"
                        },
                        {
                            name: "clear_op",
                            xtype: "combobox",
                            fieldLabel: __("Clear Operation"),
                            store: [
                                ["<", "<"],
                                ["<=", "<="],
                                [">=", ">="],
                                [">", ">"]
                            ],
                            allowBlank: true,
                            uiStyle: "small"
                        },
                        {
                            name: "clear_value",
                            xtype: "textfield",
                            fieldLabel: __("Clear Value"),
                            allowBlank: true,
                            vtype: "float"
                        },
                        {
                            name: "alarm_class",
                            xtype: "fm.alarmclass.LookupField",
                            fieldLabel: __("Alarm Class"),
                            allowBlank: true
                        },
                        {
                            name: "open_event_class",
                            xtype: "fm.eventclass.LookupField",
                            fieldLabel: __("Open Event Class"),
                            allowBlank: true
                        },
                        {
                            name: "close_event_class",
                            xtype: "fm.eventclass.LookupField",
                            fieldLabel: __("Close Event Class"),
                            allowBlank: true
                        },
                        {
                            name: "open_handler",
                            xtype: "main.handler.LookupField",
                            fieldLabel: __("Open Handler"),
                            allowBlank: true,
                            groupEdit: true,
                            query: {
                                allow_threshold: true
                            }
                        },
                        {
                            name: "close_handler",
                            xtype: "main.handler.LookupField",
                            fieldLabel: __("Close Handler"),
                            allowBlank: true,
                            groupEdit: true,
                            query: {
                                allow_threshold: true
                            }
                        },
                        {
                            name: "template",
                            xtype: "main.template.LookupField",
                            fieldLabel: __("Template"),
                            allowBlank: true
                        }
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
