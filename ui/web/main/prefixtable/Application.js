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
            text: __("Name"),
            dataIndex: "name",
            width: 200
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
    inlines: [{
        title: __("Prefixes"),
        model: "NOC.main.prefixtable.PrefixModel",
        columns: [
            {
                text: __("Prefix"),
                dataIndex: "prefix",
                flex: 1,
                editor: "textfield"
            }
        ]
    }],
    actions: [
        {
            title: __("Test selected prefix tables ..."),
            action: "test",
            resultTemplate: "TestResultTemplate",
            form: [
                {
                    name: "ip",
                    xtype: "textfield",
                    fieldLabel: __("IP"),
                    allowBlank: false
                }
            ]
        }
    ]
});
