//---------------------------------------------------------------------
// fm.alarmclass application
//---------------------------------------------------------------------
// Copyright (C) 2007-2013 The NOC Project
// See LICENSE for details
//---------------------------------------------------------------------
console.debug("Defining NOC.fm.alarmclass.Application");

Ext.define("NOC.fm.alarmclass.Application", {
    extend: "NOC.core.ModelApplication",
    uses: [
        "NOC.fm.alarmclass.Model",
        "NOC.fm.alarmclass.LookupField",
        "NOC.fm.alarmseverity.LookupField",
        "Ext.ux.form.JSONField",
        "Ext.ux.form.StringsField"
    ],
    model: "NOC.fm.alarmclass.Model",
    search: true,
    treeFilter: "category",
    rowClassField: "row_class",

    initComponent: function() {
        var me = this;

        me.jsonPanel = Ext.create("NOC.core.JSONPreview", {
            app: me,
            restUrl: "/fm/alarmclass/{{id}}/json/",
            previewName: "Alarm Class: {{name}}"
        });
        me.ITEM_JSON = me.registerItem(me.jsonPanel);

        Ext.apply(me, {
            columns: [
                {
                    text: __("Name"),
                    dataIndex: "name",
                    width: 250
                },
                {
                    text: __("Builtin"),
                    dataIndex: "is_builtin",
                    renderer: NOC.render.Bool,
                    width: 30
                },
                {
                    text: __("Description"),
                    dataIndex: "description",
                    flex: 1
                }
            ],
            fields: [
                {
                    xtype: "container",
                    layout: "hbox",
                    items: [
                        {
                            name: "name",
                            xtype: "textfield",
                            fieldLabel: __("Name"),
                            allowBlank: false,
                            uiStyle: "large"
                        },
                        {
                            name: "uuid",
                            xtype: "displayfield",
                            fieldLabel: __("UUID")
                        }
                    ]
                },
                {
                    xtype: "tabpanel",
                    layout: "fit",
                    autoScroll: true,
                    anchor: "-0, -50",
                    defaults: {
                        autoScroll: true,
                        layout: "anchor"
                    },
                    items: [
                        {
                            title: "Text",
                            items: [
                                {
                                    name: "description",
                                    xtype: "textarea",
                                    fieldLabel: __("Description"),
                                    uiStyle: "extra"
                                },
                                {
                                    name: "subject_template",
                                    xtype: "textfield",
                                    fieldLabel: __("Subject Template"),
                                    uiStyle: "extra",
                                    allowBlank: false
                                },
                                {
                                    name: "body_template",
                                    xtype: "textarea",
                                    fieldLabel: __("Body Template"),
                                    uiStyle: "extra",
                                    allowBlank: false
                                },
                                {
                                    name: "symptoms",
                                    xtype: "textarea",
                                    fieldLabel: __("Symptoms"),
                                    uiStyle: "extra",
                                    allowBlank: true
                                },
                                {
                                    name: "probable_causes",
                                    xtype: "textarea",
                                    fieldLabel: __("Probable Causes"),
                                    uiStyle: "extra",
                                    allowBlank: true
                                },
                                {
                                    name: "recommended_actions",
                                    xtype: "textarea",
                                    fieldLabel: __("Recommended Actions"),
                                    uiStyle: "extra",
                                    allowBlank: true
                                }
                            ]
                        },
                        {
                            title: "Severity",
                            items: [
                                {
                                    name: "default_severity",
                                    xtype: "fm.alarmseverity.LookupField",
                                    fieldLabel: __("Default Severity")
                                },
                                {
                                    name: "is_unique",
                                    xtype: "checkboxfield",
                                    boxLabel: __("Unique")
                                },
                                {
                                    name: "user_clearable",
                                    xtype: "checkboxfield",
                                    boxLabel: __("User Clearable")
                                },
                                {
                                    name: "discriminator",
                                    xtype: "stringsfield",
                                    fieldLabel: __("Discriminator")
                                }
                            ]
                        },
                        {
                            title: "Variables",
                            items: [
                                {
                                    name: "vars",
                                    xtype: "gridfield",
                                    columns: [
                                        {
                                            text: __("Name"),
                                            dataIndex: "name",
                                            width: 100,
                                            editor: "textfield"
                                        },
                                        {
                                            text: __("Description"),
                                            dataIndex: "description",
                                            flex: 1,
                                            editor: "textfield"
                                        },
                                        {
                                            text: __("Default"),
                                            dataIndex: "default",
                                            width: 150,
                                            editor: "textfield"
                                        }
                                    ]
                                }
                            ]
                        },
                        {
                            title: "Data Sources",
                            items: [
                                {
                                    name: "datasources",
                                    xtype: "gridfield",
                                    columns: [
                                        {
                                            text: __("Name"),
                                            dataIndex: "name",
                                            width: 100,
                                            editor: "textfield"
                                        },
                                        {
                                            text: __("Datasource"),
                                            dataIndex: "datasource",
                                            width: 100,
                                            editor: "textfield"
                                        },
                                        {
                                            text: __("Search"),
                                            dataIndex: "search",
                                            flex: 1,
                                            editor: "jsonfield",
                                            renderer: NOC.render.JSON
                                        }
                                    ]
                                }
                            ]
                        },
                        {
                            title: "Root Cause",
                            items: [
                                {
                                    name: "root_cause",
                                    xtype: "gridfield",
                                    columns: [
                                        {
                                            text: __("Name"),
                                            dataIndex: "name",
                                            width: 200,
                                            editor: "textfield"
                                        },
                                        {
                                            text: __("Root"),
                                            dataIndex: "root",
                                            renderer: NOC.render.Lookup("root"),
                                            editor: "fm.alarmclass.LookupField",
                                            width: 200
                                        },
                                        {
                                            text: __("Window"),
                                            dataIndex: "window",
                                            width: 50,
                                            editor: "numberfield"
                                        },
                                        {
                                            text: __("Condition"),
                                            dataIndex: "condition",
                                            editor: "textfield",
                                            width: 150
                                        },
                                        {
                                            text: __("Match Condition"),
                                            dataIndex: "match_condition",
                                            editor: "jsonfield",
                                            flex: 1,
                                            renderer: NOC.render.JSON
                                        }
                                    ]
                                }
                            ]
                        },
                        {
                            title: "Jobs",
                            items: [
                                {
                                    name: "jobs",
                                    xtype: "gridfield",
                                    columns: [
                                        {
                                            text: __("Job"),
                                            dataIndex: "job",
                                            width: 100,
                                            editor: "textfield"
                                        },
                                        {
                                            text: __("Interval"),
                                            dataIndex: "interval",
                                            width: 50,
                                            editor: "numberfield"
                                        },
                                        {
                                            text: __("Vars"),
                                            dataIndex: "vars",
                                            flex: 1,
                                            editor: "jsonfield",
                                            renderer: NOC.render.JSON
                                        }
                                    ]
                                }
                            ]
                        },
                        {
                            title: "Handlers",
                            items: [
                                {
                                    xtype: "stringsfield",
                                    name: "handlers",
                                    fieldLabel: __("Handlers")
                                }
                            ]
                        },
                        {
                            title: "Plugins",
                            items: [
                                {
                                    xtype: "gridfield",
                                    name: "plugins",
                                    fieldLabel: __("Plugins"),
                                    columns: [
                                        {
                                            text: __("Name"),
                                            dataIndex: "name",
                                            editor: "textfield",
                                            width: 150
                                        },
                                        {
                                            text: __("Config"),
                                            dataIndex: "config",
                                            editor: "jsonfield",
                                            flex: 1,
                                            renderer: NOC.render.JSON
                                        }
                                    ]
                                }
                            ]
                        },
                        {
                            title: "Timing",
                            items: [
                                {
                                    name: "flap_window",
                                    xtype: "numberfield",
                                    fieldLabel: __("Flap Window"),
                                    allowBlank: true,
                                    uiStyle: "small"
                                },
                                {
                                    name: "flap_threshold",
                                    xtype: "numberfield",
                                    fieldLabel: __("Flap Threshold"),
                                    allowBlank: true,
                                    uiStyle: "small"
                                },
                                {
                                    name: "notification_delay",
                                    xtype: "numberfield",
                                    fieldLabel: __("Notification Delay"),
                                    allowBlank: true,
                                    uiStyle: "small"
                                },
                                {
                                    name: "control_time0",
                                    xtype: "numberfield",
                                    fieldLabel: __("Control Time 0"),
                                    allowBlank: true,
                                    uiStyle: "small"
                                },
                                {
                                    name: "control_time1",
                                    xtype: "numberfield",
                                    fieldLabel: __("Control Time 1"),
                                    allowBlank: true,
                                    uiStyle: "small"
                                },
                                {
                                    name: "control_timeN",
                                    xtype: "numberfield",
                                    fieldLabel: __("Control Time N"),
                                    allowBlank: true,
                                    uiStyle: "small"
                                }

                            ]
                        }
                    ]
                }
            ],
            formToolbar: [
                {
                    text: __("JSON"),
                    glyph: NOC.glyph.file,
                    tooltip: "View as JSON",
                    hasAccess: NOC.hasPermission("read"),
                    scope: me,
                    handler: me.onJSON
                }
            ]
        });
        me.callParent();
    },
    //
    filters: [
        {
            title: "By Builtin",
            name: "is_builtin",
            ftype: "boolean"
        }
    ],
    //
    onJSON: function() {
        var me = this;
        me.showItem(me.ITEM_JSON);
        me.jsonPanel.preview(me.currentRecord);
    },
    //
    onSave: function() {
        NOC.info("Sorry! Not implemented still. Please apply changes to JSON files directly");
    }
});
