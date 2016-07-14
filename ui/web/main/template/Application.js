//---------------------------------------------------------------------
// main.template application
//---------------------------------------------------------------------
// Copyright (C) 2007-2012 The NOC Project
// See LICENSE for details
//---------------------------------------------------------------------
console.debug("Defining NOC.main.template.Application");

Ext.define("NOC.main.template.Application", {
    extend: "NOC.core.ModelApplication",
    requires: [
        "NOC.main.template.Model"
    ],
    model: "NOC.main.template.Model",
    search: true,
    columns: [
        {
            text: __("Name"),
            dataIndex: "name",
            flex: 1
        },

        {
            text: __("Subject"),
            dataIndex: "subject",
            flex: 1
        }
    ],
    fields: [
        {
            name: "name",
            xtype: "textfield",
            fieldLabel: __("Name"),
            anchor: "50%",
            allowBlank: false
        },
        {
            name: "subject",
            xtype: "textareafield",
            fieldLabel: __("Subject"),
            allowBlank: false,
            anchor: "100%",
            height: 100,
            fieldStyle: {
                fontFamily: "Courier"
            }
        },
        {
            name: "body",
            xtype: "textareafield",
            fieldLabel: __("Body"),
            allowBlank: false,
            anchor: "100%",
            height: 200,
            fieldStyle: {
                fontFamily: "Courier"
            }
        }
    ],
    filters: [
    ]
});
