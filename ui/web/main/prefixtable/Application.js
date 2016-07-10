//---------------------------------------------------------------------
// main.prefixtable application
//---------------------------------------------------------------------
// Copyright (C) 2007-2013 The NOC Project
// See LICENSE for details
//---------------------------------------------------------------------
console.debug("Defining NOC.main.prefixtable.Application");

Ext.define("NOC.main.prefixtable.Application", {
    extend: "NOC.core.ModelApplication",
    uses: [
        "NOC.main.prefixtable.Model",
        "NOC.main.prefixtable.PrefixModel",
        "NOC.main.prefixtable.templates.TestResultTemplate"
    ],
    model: "NOC.main.prefixtable.Model",
    search: true,
    columns: [
        {
            text: "Name",
            dataIndex: "name",
            width: 200
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
    inlines: [{
        title: "Prefixes",
        model: "NOC.main.prefixtable.PrefixModel",
        columns: [
            {
                text: "Prefix",
                dataIndex: "prefix",
                flex: 1,
                editor: "textfield"
            }
        ]
    }],
    actions: [
        {
            title: "Test selected prefix tables ...",
            action: "test",
            resultTemplate: "TestResultTemplate",
            form: [
                {
                    name: "ip",
                    xtype: "textfield",
                    fieldLabel: "IP",
                    allowBlank: false
                }
            ]
        }
    ]
});
