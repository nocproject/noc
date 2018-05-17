//---------------------------------------------------------------------
// dev.spec application
//---------------------------------------------------------------------
// Copyright (C) 2007-2018 The NOC Project
// See LICENSE for details
//---------------------------------------------------------------------
console.debug("Defining NOC.dev.spec.Application");

Ext.define("NOC.dev.spec.Application", {
    extend: "NOC.core.ModelApplication",
    requires: [
        "NOC.dev.spec.Model",
        "NOC.dev.quiz.LookupField",
        "NOC.sa.profile.LookupField",
        "NOC.core.ListFormField"
    ],
    model: "NOC.dev.spec.Model",
    search: true,

    initComponent: function() {
        var me = this;
        Ext.apply(me, {
            columns: [
                {
                    text: __("Name"),
                    dataIndex: "name",
                    width: 150
                },
                {
                    text: __("Quiz"),
                    dataIndex: "quiz",
                    width: 150,
                    renderer: NOC.render.Lookup("quiz")
                },
                {
                    text: __("Profile"),
                    dataIndex: "profile",
                    width: 150,
                    renderer: NOC.render.Lookup("profile")
                }
            ],

            fields: [
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
                    fieldLabel: __("UUID"),
                    allowBlank: true
                },
                {
                    name: "description",
                    xtype: "textarea",
                    fieldLabel: __("Description"),
                    allowBlank: false
                },
                {
                    name: "revision",
                    xtype: "numberfield",
                    fieldLabel: __("Revision"),
                    allowBlank: false,
                    minValue: 1,
                    uiStyle: "small"
                },
                {
                    name: "quiz",
                    xtype: "dev.quiz.LookupField",
                    fieldLabel: __("Quiz"),
                    allowBlank: false
                },
                {
                    name: "profile",
                    xtype: "sa.profile.LookupField",
                    fieldLabel: __("Profile"),
                    allowBlank: false
                },
                {
                    name: "author",
                    xtype: "textfield",
                    fieldLabel: __("Author"),
                    allowBlank: false
                },
                {
                    name: "changes",
                    xtype: "listform",
                    fieldLabel: __("Changes"),
                    items: [
                        {
                            name: "date",
                            xtype: "textfield",
                            fieldLabel: __("Date"),
                            allowBlank: false,
                            uiStyle: "medium"
                        },
                        {
                            name: "changes",
                            xtype: "textarea",
                            fieldLabel: __("Changes"),
                            allowBlank: false,
                            uiStyle: "extra"
                        }
                    ]
                },
                {
                    name: "answers",
                    xtype: "listform",
                    fieldLabel: __("Answers"),
                    allowBlank: false,
                    items: [
                        {
                            name: "name",
                            xtype: "textfield",
                            fieldLabel: __("Name"),
                            allowBlank: false,
                            uiStyle: "medium"
                        },
                        {
                            name: "type",
                            xtype: "combobox",
                            fieldLabel: __("Type"),
                            allowBlank: false,
                            uiStyle: "medium"
                        },
                        {
                            name: "value",
                            xtype: "textarea",
                            fieldLabel: __("Value"),
                            allowBlank: false,
                            uiStyle: "extra"
                        }
                    ]
                }
            ]
        });
        me.callParent();
    }
});
