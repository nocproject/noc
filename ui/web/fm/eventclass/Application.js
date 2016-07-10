//---------------------------------------------------------------------
// fm.eventclass application
//---------------------------------------------------------------------
// Copyright (C) 2007-2013 The NOC Project
// See LICENSE for details
//---------------------------------------------------------------------
console.debug("Defining NOC.fm.eventclass.Application");

Ext.define("NOC.fm.eventclass.Application", {
    extend: "NOC.core.ModelApplication",
    uses: [
        "NOC.fm.eventclass.Model",
        "NOC.fm.eventclass.LookupField",
        "NOC.fm.alarmclass.LookupField",
        "Ext.ux.form.JSONField",
        "Ext.ux.form.StringsField"
    ],
    model: "NOC.fm.eventclass.Model",
    search: true,
    treeFilter: "category",
    //
    initComponent: function() {
        var me = this;

        me.actionStore = Ext.create("Ext.data.Store", {
            fields: ["id", "label"],
            data: [
                {id: "D", label: "Drop"},
                {id: "L", label: "Log"},
                {id: "A", label: "Archive"}
            ]
        });
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
                            title: "Action",
                            items: [
                                {
                                    name: "action",
                                    xtype: "combobox",
                                    fieldLabel: "Action",
                                    allowBlank: false,
                                    store: me.actionStore,
                                    queryMode: "local",
                                    displayField: "label",
                                    valueField: "id"
                                },
                                {
                                    name: "link_event",
                                    xtype: "checkboxfield",
                                    boxLabel: "Link Event"
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
                                            text: "Type",
                                            dataIndex: "type",
                                            width: 100,
                                            editor: {
                                                xtype: "combobox",
                                                store: [
                                                    "str",
                                                    "int", "float",
                                                    "ipv4_address", "ipv6_address", "ip_address",
                                                    "ipv4_prefix", "ipv6_prefix", "ip_prefix",
                                                    "mac", "interface_name", "oid"
                                                ]
                                            }
                                        },
                                        {
                                            text: "Required",
                                            dataIndex: "required",
                                            width: 50,
                                            editor: "checkboxfield",
                                            renderer: NOC.render.Bool
                                        },
                                        {
                                            text: "Description",
                                            dataIndex: "description",
                                            flex: 1,
                                            editor: "textfield"
                                        }
                                    ]
                                }
                            ]
                        },
                        {
                            title: "Disposition",
                            items: [
                                {
                                    name: "disposition",
                                    xtype: "gridfield",
                                    fieldLabel: "Disposition",
                                    columns: [
                                        {
                                            text: "Name",
                                            dataIndex: "name",
                                            width: 100,
                                            editor: "textfield"
                                        },
                                        {
                                            text: "Condition",
                                            dataIndex: "condition",
                                            width: 100,
                                            editor: "textfield"
                                        },
                                        {
                                            text: "Action",
                                            dataIndex: "action",
                                            width: 70,
                                            editor: {
                                                xtype: "combobox",
                                                store: [
                                                    "drop",
                                                    "ignore",
                                                    "raise",
                                                    "clear"
                                                ]
                                            }
                                        },
                                        {
                                            text: "Alarm",
                                            dataIndex: "alarm_class",
                                            renderer: NOC.render.Lookup("alarm_class"),
                                            width: 200,
                                            editor: "fm.alarmclass.LookupField"
                                        },
                                        {
                                            text: "Stop",
                                            dataIndex: "stop_disposition",
                                            renderer: NOC.render.Bool,
                                            width: 50,
                                            editor: "checkbox"
                                        },
                                        {
                                            text: "Managed Object",
                                            dataIndex: "managed_object",
                                            editor: "textfield",
                                            width: 100
                                        },
                                        {
                                            text: "Var.  Map.",
                                            dataIndex: "var_mapping",
                                            renderer: NOC.render.JSON,
                                            editor: "jsonfield",
                                            flex: 1
                                        }
                                    ]
                                }
                            ]
                        },
                        {
                            title: "Suppression",
                            items: [
                                {
                                    name: "deduplication_window",
                                    xtype: "numberfield",
                                    uiStyle: "small",
                                    fieldLabel: "Deduplication Window",
                                    allowBlank: false
                                },
                                {
                                    name: "ttl",
                                    xtype: "numberfield",
                                    uiStyle: "small",
                                    fieldLabel: "Event TTL",
                                    allowBlank: false
                                },
                                {
                                    name: "repeat_suppression",
                                    xtype: "gridfield",
                                    fieldLabel: "Repeat Suppression",
                                    columns: [
                                        {
                                            text: "Name",
                                            dataIndex: "name",
                                            width: 150,
                                            editor: "textfield"
                                        },
                                        {
                                            text: "Window",
                                            dataIndex: "window",
                                            width: 50,
                                            editor: "numberfield"
                                        },
                                        {
                                            text: "Suppress",
                                            dataIndex: "suppress",
                                            width: 50,
                                            editor: "checkbox",
                                            renderer: NOC.render.Bool
                                        },
                                        {
                                            text: "Event Class",
                                            dataIndex: "event_class",
                                            width: 200,
                                            editor: "fm.eventclass.LookupField",
                                            renderer: NOC.render.Lookup("event_class")
                                        },
                                        {
                                            text: "Condition",
                                            dataIndex: "condition",
                                            width: 150,
                                            editor: "textfield"
                                        },
                                        {
                                            text: "Match Condition",
                                            dataIndex: "match_condition",
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
        me.jsonPanel = Ext.create("NOC.core.JSONPreview", {
            app: me,
            restUrl: "/fm/eventclass/{{id}}/json/",
            previewName: "Event Class: {{name}}"
        });
        me.ITEM_JSON = me.registerItem(me.jsonPanel);
        me.callParent();
    },
    filters: [
        {
            title: "By Link Event",
            name: "link_event",
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
