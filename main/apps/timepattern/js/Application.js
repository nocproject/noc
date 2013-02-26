//---------------------------------------------------------------------
// main.timepattern application
//---------------------------------------------------------------------
// Copyright (C) 2007-2013 The NOC Project
// See LICENSE for details
//---------------------------------------------------------------------
console.debug("Defining NOC.main.timepattern.Application");

Ext.define("NOC.main.timepattern.Application", {
    extend: "NOC.core.ModelApplication",
    uses: [
        "NOC.main.timepattern.Model",
        "NOC.main.timepattern.TermModel",
        "NOC.main.timepattern.templates.TestResultTemplate"
    ],
    model: "NOC.main.timepattern.Model",
    search: true,
    columns: [
        {
            text: "Name",
            dataIndex: "name",
            width: 100
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
            fieldLabel: "Name",
            allowBlank: false
        },
        {
            name: "description",
            xtype: "textarea",
            fieldLabel: "Description",
            allowBlank: true
        }
    ],
    inlines: [
        {
            title: "Time Patterns",
            model: "NOC.main.timepattern.TermModel",
            columns: [
                {
                    text: "Pattern",
                    dataIndex: "term",
                    flex: 1,
                    editor: "textfield"
                }
            ]
        }
    ],
    "actions": [
        {
            title: "Test selected patterns",
            action: "test",
            resultTemplate: "TestResultTemplate",
            form: [
                {
                    name: "date",
                    xtype: "datefield",
                    fieldLabel: "Date",
                    allowBlank: false,
                    format: "Y-m-d"
                },
                {
                    name: "time",
                    xtype: "timefield",
                    fieldLabel: "Time",
                    allowBlank: true,
                    format: "H:i"
                }
            ]
        }
    ]
});
