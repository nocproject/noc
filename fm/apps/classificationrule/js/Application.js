//---------------------------------------------------------------------
// fm.classificationrule application
//---------------------------------------------------------------------
// Copyright (C) 2007-2013 The NOC Project
// See LICENSE for details
//---------------------------------------------------------------------
console.debug("Defining NOC.fm.classificationrule.Application");

Ext.define("NOC.fm.classificationrule.Application", {
    extend: "NOC.core.ModelApplication",
    requires: [
        "NOC.fm.classificationrule.Model",
        "NOC.fm.eventclass.LookupField",
        "NOC.fm.classificationrule.templates.TestResult"
    ],
    model: "NOC.fm.classificationrule.Model",
    search: true,
    treeFilter: "category",
    columns: [
        {
            text: "Name",
            dataIndex: "name",
            width: 500
        },
        {
            text: "Builtin",
            dataIndex: "is_builtin",
            width: 50,
            renderer: NOC.render.Bool
        },
        {
            text: "Event Class",
            dataIndex: "event_class",
            flex: 1,
            renderer: NOC.render.Lookup("event_class")
        },
        {
            text: "Pref",
            dataIndex: "preference",
            width: 50
        }
    ],
    filters: [
        {
            title: "By Event Class",
            name: "event_class",
            ftype: "lookup",
            lookup: "fm.eventclass"
        }
    ],

    initComponent: function() {
        var me = this;
        me.jsonPanel = Ext.create("NOC.core.JSONPreview", {
            app: me,
            restUrl: "/fm/classificationrule/{{id}}/json/",
            previewName: "Classification Rule: {{name}}"
        });
        me.ITEM_JSON = me.registerItem(me.jsonPanel);
        //
        me.testForm = Ext.create("NOC.fm.classificationrule.TestForm", {
            app: me
        });
        me.ITEM_TEST_FORM = me.registerItem(me.testForm);
        //
        me.testResultPanel = Ext.create("NOC.core.TemplatePreview", {
            app: me,
            previewName: "Rule Test Result",
            template: me.templates.TestResult,
            onCloseItem: "ITEM_FORM"
        });
        me.ITEM_TEST_RESULT = me.registerItem(me.testResultPanel);
        //
        Ext.apply(me, {
            fields: [
                {
                    xtype: "textfield",
                    name: "name",
                    fieldLabel: "Name",
                    allowBlank: false
                },
                {
                    xtype: "displayfield",
                    name: "uuid",
                    fieldLabel: "UUID"
                },
                {
                    xtype: "textarea",
                    name: "description",
                    fieldLabel: "Description",
                    allowBlank: true
                },
                {
                    xtype: "numberfield",
                    name: "preference",
                    fieldLabel: "Preference",
                    allowBlank: false,
                    defaultValue: 1000,
                    minValue: 0,
                    maxValue: 10000
                },
                {
                    xtype: "fm.eventclass.LookupField",
                    name: "event_class",
                    fieldLabel: "Event Class",
                    allowBlank: false,
                    listeners: {
                        select: {
                            scope: me,
                            fn: me.onSelectEventClass
                        }
                    }
                },
                {
                    xtype: "gridfield",
                    name: "patterns",
                    fieldLabel: "Patterns",
                    allowBlank: false,
                    columns: [
                        {
                            text: "Key RE",
                            dataIndex: "key_re",
                            flex: 1,
                            editor: "textfield",
                            renderer: NOC.render.htmlEncode
                        },
                        {
                            text: "Value RE",
                            dataIndex: "value_re",
                            flex: 1,
                            editor: "textfield",
                            renderer: NOC.render.htmlEncode
                        }
                    ]
                },
                {
                    xtype: "gridfield",
                    name: "vars",
                    fieldLabel: "Vars",
                    allowBlank: true,
                    columns: [
                        {
                            text: "Name",
                            dataIndex: "name",
                            width: 100,
                            editor: "textfield",
                            renderer: NOC.render.htmlEncode
                        },
                        {
                            text: "Value",
                            dataIndex: "value",
                            flex: 1,
                            editor: "textfield",
                            renderer: NOC.render.htmlEncode
                        }
                    ]
                }
            ],
            formToolbar: [
                {
                    text: "JSON",
                    glyph: NOC.glyph.file,
                    tooltip: "Show JSON",
                    hasAccess: NOC.hasPermission("read"),
                    scope: me,
                    handler: me.onJSON
                },
                {
                    text: "Test",
                    glyph: NOC.glyph.question_circle,
                    tooltip: "Test rule",
                    hasAccess: NOC.hasPermission("test"),
                    scope: me,
                    handler: me.onTest
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
    //
    onTest: function() {
        var me = this;
        me.showItem(me.ITEM_TEST_FORM);
    },
    //
    getPatterns: function() {
        var me = this;
        return me.form.getFieldValues().patterns;
    },
    getVars: function() {
        var me = this;
        return me.form.getFieldValues().vars;
    },
    //
    onCmd_from_event: function(data) {
        var me = this;
        Ext.Ajax.request({
            url: "/fm/classificationrule/from_event/" + data.id + "/",
            method: "GET",
            scope: me,
            success: function(response) {
                var me = this,
                    data = Ext.decode(response.responseText);
                me.newRecord(data);
            },
            failure: function() {
                NOC.error("Failed to create rule from event");
            }
        });
    },
    //
    onSelectEventClass: function(combo, records, opts) {
        var me = this;
        if(!me.currentRecord) {
            var name = records[0].get("label"),
                f = me.form.findField("name"),
                v = f.getValue();
            if(v.match(/<name>/)) {
                f.setValue(v.replace("<name>", name));
            }
        }
    }
});
