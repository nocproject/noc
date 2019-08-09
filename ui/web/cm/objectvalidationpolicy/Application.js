//---------------------------------------------------------------------
// cm.objectvalidationpolicy application
//---------------------------------------------------------------------
// Copyright (C) 2007-2019 The NOC Project
// See LICENSE for details
//---------------------------------------------------------------------
console.debug("Defining NOC.cm.objectvalidationpolicy.Application");

Ext.define("NOC.cm.objectvalidationpolicy.Application", {
    extend: "NOC.core.ModelApplication",
    requires: [
        "NOC.cm.objectvalidationpolicy.Model",
        "NOC.cm.confdbquery.LookupField",
        "NOC.fm.alarmclass.LookupField"
    ],
    model: "NOC.cm.objectvalidationpolicy.Model",
    search: true,

    initComponent: function() {
        var me = this;
        Ext.apply(me, {
            columns: [
                {
                    text: __("Name"),
                    dataIndex: "name",
                    width: 150
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
                    name: "rules",
                    xtype: "gridfield",
                    fieldLabel: __("Rules"),
                    columns: [
                        {
                            text: __("Query"),
                            dataIndex: "query",
                            width: 200,
                            editor: {
                                xtype: "cm.confdbquery.LookupField",
                                allowBlank: false,
                                query: {
                                    allow_object_validation: true
                                }
                            },
                            renderer: NOC.render.Lookup("query")
                        },
                        {
                            text: __("Active"),
                            dataIndex: "is_active",
                            editor: "checkbox",
                            width: 50,
                            renderer: NOC.render.Bool
                        },
                        {
                            text: __("Code"),
                            dataIndex: "error_code",
                            editor: "textfield",
                            width: 70
                        },
                        {
                            text: __("Error template"),
                            dataIndex: "error_text_template",
                            editor: {
                                xtype: "textfield",
                                placeHolder: "{{error}}"
                            },
                            flex: 1
                        },
                        {
                            text: __("Alarm Class"),
                            dataIndex: "alarm_class",
                            editor: "fm.alarmclass.LookupField",
                            width: 120,
                            renderer: NOC.render.Lookup("alarm_class")
                        },
                        {
                            text: __("Fatal"),
                            dataIndex: "is_fatal",
                            editor: "checkbox",
                            width: 50,
                            renderer: NOC.render.Bool
                        }
                    ]
                }
            ]
        });
        me.callParent();
    }
});