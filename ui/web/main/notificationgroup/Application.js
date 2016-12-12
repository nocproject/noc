//---------------------------------------------------------------------
// main.notificationgroup application
//---------------------------------------------------------------------
// Copyright (C) 2007-2012 The NOC Project
// See LICENSE for details
//---------------------------------------------------------------------
console.debug("Defining NOC.main.notificationgroup.Application");

Ext.define("NOC.main.notificationgroup.Application", {
    extend: "NOC.core.ModelApplication",
    requires: [
        "NOC.main.notificationgroup.Model",
        "NOC.main.notificationgroup.UsersModel",
        "NOC.main.notificationgroup.OtherModel",
        "NOC.main.timepattern.LookupField",
        "NOC.main.user.LookupField"
    ],
    model: "NOC.main.notificationgroup.Model",
    search: true,
    columns: [
        {
            text: __("Name"),
            dataIndex: "name",
            width: 150
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
            allowBlank: false
        },
        {
            name: "description",
            xtype: "textarea",
            fieldLabel: __("Description"),
            allowBlank: true
        }
    ],
    inlines: [
        {
            title: __("Users"),
            model: "NOC.main.notificationgroup.UsersModel",
            columns: [
                {
                    text: __("Time Pattern"),
                    dataIndex: "time_pattern",
                    width: 150,
                    renderer: NOC.render.Lookup("time_pattern"),
                    editor: "main.timepattern.LookupField"
                },
                {
                    text: __("User"),
                    dataIndex: "user",
                    flex: 1,
                    renderer: NOC.render.Lookup("user"),
                    editor: "main.user.LookupField"
                }
            ]
        },
        {
            title: __("Other"),
            model: "NOC.main.notificationgroup.OtherModel",
            columns: [
                {
                    text: __("Time Pattern"),
                    dataIndex: "time_pattern",
                    width: 150,
                    renderer: NOC.render.Lookup("time_pattern"),
                    editor: "main.timepattern.LookupField"
                },
                {
                    text: __("Method"),
                    dataIndex: "notification_method",
                    width: 75,
                    editor: {
                        xtype: "combobox",
                        store: [
                            ["mail", "Mail"],
                            ["tg", "Telegram"],
                            ["file", "File"],
                            ["xmpp", "Jabber"]
                        ]
                    }
                },
                {
                    text: __("Params"),
                    dataIndex: "params",
                    flex: 1,
                    editor: "textfield"
                }
            ]
        }
    ],
    actions: [
        {
            title: __("Test selected groups"),
            action: "test",
            form: [
                {
                    name: "subject",
                    xtype: "textfield",
                    fieldLabel: __("Subject"),
                    allowBlank: false,
                    width: 600
                },
                {
                    name: "body",
                    xtype: "textarea",
                    fieldLabel: __("Body"),
                    allowBlank: false,
                    width: 600
                }
            ]
        }
    ]
});
