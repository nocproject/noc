//---------------------------------------------------------------------
// fm.dispositionrule application
//---------------------------------------------------------------------
// Copyright (C) 2007-2025 The NOC Project
// See LICENSE for details
//---------------------------------------------------------------------
console.debug("Defining NOC.fm.dispositionrule.Application");

Ext.define("NOC.fm.dispositionrule.Application", {
    extend: "NOC.core.ModelApplication",
    requires: [
        "NOC.core.JSONPreview",
        "NOC.core.TemplatePreview",
        "NOC.core.ListFormField",
        "NOC.core.StringListField",
        "NOC.core.tagfield.Tagfield",
        "NOC.core.label.LabelField",
        "NOC.core.combotree.ComboTree",
        "NOC.fm.eventclass.LookupField",
        "NOC.fm.alarmclass.LookupField",
        "NOC.fm.dispositionrule.LookupField",
        "NOC.main.handler.LookupField",
        "NOC.main.remotesystem.LookupField",
        'Ext.ux.form.JSONField',
        "Ext.ux.form.GridField",
    ],
    model: "NOC.fm.dispositionrule.Model",
    search: true,
    treeFilter: "category",
    columns: [
        {
            text: __("Name"),
            dataIndex: "name",
            width: 500
        },
        {
            text: __("Builtin"),
            dataIndex: "is_builtin",
            width: 50,
            renderer: NOC.render.Bool
        },
        {
            text: __("Alarm Disposition"),
            dataIndex: "alarm_disposition",
            flex: 1,
            renderer: NOC.render.Lookup("alarm_disposition")
        },
        {
            text: __("Pref"),
            dataIndex: "preference",
            width: 50
        }
    ],
    filters: [
        {
            title: __("By Event Class"),
            name: "event_class",
            ftype: "lookup",
            lookup: "fm.eventclass"
        },
        {
            title: __("By Alarm Class"),
            name: "alarm_disposition",
            ftype: "lookup",
            lookup: "fm.alarmclass"
        }
    ],

    initComponent: function() {
        var me = this;
        me.jsonPanel = Ext.create("NOC.core.JSONPreview", {
            app: me,
            restUrl: new Ext.XTemplate('/fm/dispositionrule/{id}/json/'),
            previewName: new Ext.XTemplate('Disposition Rule: {name}')
        });
        me.ITEM_JSON = me.registerItem(me.jsonPanel);

        //
        Ext.apply(me, {
            fields: [
                {
                    xtype: "textfield",
                    name: "name",
                    fieldLabel: __("Name"),
                    allowBlank: false
                },
                {
                    xtype: "displayfield",
                    name: "uuid",
                    fieldLabel: __("UUID")
                },
                {
                    xtype: "textarea",
                    name: "description",
                    fieldLabel: __("Description"),
                    allowBlank: true
                },
                {
                    name: "is_active",
                    xtype: "checkbox",
                    boxLabel: __("Active")
                },
                {
                    xtype: "numberfield",
                    name: "preference",
                    fieldLabel: __("Preference"),
                    allowBlank: false,
                    uiStyle: "small",
                    defaultValue: 1000,
                    minValue: 0,
                    maxValue: 10000
                },
                {
                    xtype: "fieldset",
                    layout: "hbox",
                    defaults: {
                      labelAlign: "top",
                      margin: 5
                    },
                    title: __("Combo Condition"),
                    items: [
                        {
                            name: "combo_condition",
                            xtype: "combobox",
                            fieldLabel: __("Combo Condition"),
                            store: [
                                ["none", __("None")],
                                ["frequency", __("Frequency")],
                                ["sequence", __("Sequence")],
                                ["all", __("All")],
                                ["any", __("Any")]
                            ],
                            value: "none",
                            uiStyle: "medium"
                        },
                        {
                          name: "combo_window",
                          xtype: "numberfield",
                          fieldLabel: __("Combo Window (sec)"),
                          allowBlank: true,
                          uiStyle: "medium",
                          defaultValue: 0,
                          minValue: 0
                        },
                        {
                          name: "combo_count",
                          xtype: "numberfield",
                          fieldLabel: __("Combo count"),
                          allowBlank: true,
                          uiStyle: "medium",
                          defaultValue: 0,
                          minValue: 0
                        }
                    ]
                },
                {
                    xtype: "fieldset",
                    title: __("Replace Rule"),
                    items: [
                        {
                            name: "replace_rule",
                            xtype: "fm.dispositionrule.LookupField",
                            fieldLabel: __("Dispose Rule"),
                            uiStyle: 'medium',
                            allowBlank: true
                        },
                        {
                            name: "replace_rule_policy",
                            xtype: "combobox",
                            fieldLabel: __("Replace Policy"),
                            store: [
                                ["D", __("Disable")],
                                ["w", __("Whole")],
                                ["c", __("Extend Condition")],
                                ["a", __("Action")]
                            ],
                            value: "none",
                            uiStyle: "medium"
                        }
                    ]
                },
                {
                    name: "alarm_disposition",
                    xtype: "fm.alarmclass.LookupField",
                    fieldLabel: __("Dispose Alarm"),
                    uiStyle: 'medium',
                    allowBlank: true
                },
                {
                    name: "stop_processing",
                    xtype: "checkbox",
                    boxLabel: __("Stop Processing Rules")
                },
                {
                    name: "match",
                    xtype: "listform",
                    fieldLabel: __("Match Rules"),
                    rows: 5,
                    items: [
                        {
                            name: "event_class_re",
                            xtype: "textfield",
                            fieldLabel: __("Event Class RE"),
                            uiStyle: 'medium',
                            allowBlank: true
                        },
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
                            xtype: "core.tagfield",
                            url: "/inv/resourcegroup/lookup/",
                            fieldLabel: __("Object Groups"),
                            name: "groups",
                            allowBlank: true,
                            uiStyle: "extra"
                        },
                        {
                            name: "remote_system",
                            xtype: "main.remotesystem.LookupField",
                            fieldLabel: __("Remote System"),
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

    onJSON: function() {
        var me = this;
        me.showItem(me.ITEM_JSON);
        me.jsonPanel.preview(me.currentRecord);
    },
});
