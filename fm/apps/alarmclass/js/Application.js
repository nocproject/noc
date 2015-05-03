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
                    text: "Name",
                    dataIndex: "name",
                    width: 250
                },
                {
                    text: "Builtin",
                    dataIndex: "is_builtin",
                    renderer: NOC.render.Bool,
                    width: 30
                },
                {
                    text: "Description",
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
                            fieldLabel: "Name",
                            allowBlank: false,
                            uiStyle: "large"
                        },
                        {
                            name: "uuid",
                            xtype: "displayfield",
                            fieldLabel: "UUID"
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
                                    fieldLabel: "Description",
                                    uiStyle: "extra"
                                },
                                {
                                    name: "subject_template",
                                    xtype: "textfield",
                                    fieldLabel: "Subject Template",
                                    uiStyle: "extra",
                                    allowBlank: false
                                },
                                {
                                    name: "body_template",
                                    xtype: "textarea",
                                    fieldLabel: "Body Template",
                                    uiStyle: "extra",
                                    allowBlank: false
                                },
                                {
                                    name: "symptoms",
                                    xtype: "textarea",
                                    fieldLabel: "Symptoms",
                                    uiStyle: "extra",
                                    allowBlank: true
                                },
                                {
                                    name: "probable_causes",
                                    xtype: "textarea",
                                    fieldLabel: "Probable Causes",
                                    uiStyle: "extra",
                                    allowBlank: true
                                },
                                {
                                    name: "recommended_actions",
                                    xtype: "textarea",
                                    fieldLabel: "Recommended Actions",
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
                                    fieldLabel: "Default Severity"
                                },
                                {
                                    name: "is_unique",
                                    xtype: "checkboxfield",
                                    boxLabel: "Unique"
                                },
                                {
                                    name: "user_clearable",
                                    xtype: "checkboxfield",
                                    boxLabel: "User Clearable"
                                },
                                {
                                    name: "discriminator",
                                    xtype: "stringsfield",
                                    fieldLabel: "Discriminator"
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
                                            text: "Name",
                                            dataIndex: "name",
                                            width: 100,
                                            editor: "textfield"
                                        },
                                        {
                                            text: "Description",
                                            dataIndex: "description",
                                            flex: 1,
                                            editor: "textfield"
                                        },
                                        {
                                            text: "Default",
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
                                            text: "Name",
                                            dataIndex: "name",
                                            width: 100,
                                            editor: "textfield"
                                        },
                                        {
                                            text: "Datasource",
                                            dataIndex: "datasource",
                                            width: 100,
                                            editor: "textfield"
                                        },
                                        {
                                            text: "Search",
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
                                            text: "Name",
                                            dataIndex: "name",
                                            width: 200,
                                            editor: "textfield"
                                        },
                                        {
                                            text: "Root",
                                            dataIndex: "root",
                                            renderer: NOC.render.Lookup("root"),
                                            editor: "fm.alarmclass.LookupField",
                                            width: 200
                                        },
                                        {
                                            text: "Window",
                                            dataIndex: "window",
                                            width: 50,
                                            editor: "numberfield"
                                        },
                                        {
                                            text: "Condition",
                                            dataIndex: "condition",
                                            editor: "textfield",
                                            width: 150
                                        },
                                        {
                                            text: "Match Condition",
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
                                            text: "Job",
                                            dataIndex: "job",
                                            width: 100,
                                            editor: "textfield"
                                        },
                                        {
                                            text: "Interval",
                                            dataIndex: "interval",
                                            width: 50,
                                            editor: "numberfield"
                                        },
                                        {
                                            text: "Vars",
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
                                    fieldLabel: "Handlers"
                                }
                            ]
                        },
                        {
                            title: "Plugins",
                            items: [
                                {
                                    xtype: "gridfield",
                                    name: "plugins",
                                    fieldLabel: "Plugins",
                                    columns: [
                                        {
                                            text: "Name",
                                            dataIndex: "name",
                                            editor: "textfield",
                                            width: 150
                                        },
                                        {
                                            text: "Config",
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
                                    fieldLabel: "Flap Window",
                                    allowBlank: true,
                                    uiStyle: "small"
                                },
                                {
                                    name: "flap_threshold",
                                    xtype: "numberfield",
                                    fieldLabel: "Flap Threshold",
                                    allowBlank: true,
                                    uiStyle: "small"
                                },
                                {
                                    name: "notification_delay",
                                    xtype: "numberfield",
                                    fieldLabel: "Notification Delay",
                                    allowBlank: true,
                                    uiStyle: "small"
                                },
                                {
                                    name: "control_time0",
                                    xtype: "numberfield",
                                    fieldLabel: "Control Time 0",
                                    allowBlank: true,
                                    uiStyle: "small"
                                },
                                {
                                    name: "control_time1",
                                    xtype: "numberfield",
                                    fieldLabel: "Control Time 1",
                                    allowBlank: true,
                                    uiStyle: "small"
                                },
                                {
                                    name: "control_timeN",
                                    xtype: "numberfield",
                                    fieldLabel: "Control Time N",
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
                    text: "JSON",
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
