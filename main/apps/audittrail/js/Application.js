//---------------------------------------------------------------------
// main.audittrail application
//---------------------------------------------------------------------
// Copyright (C) 2007-2012 The NOC Project
// See LICENSE for details
//---------------------------------------------------------------------
console.debug("Defining NOC.main.audittrail.Application");

Ext.define("NOC.main.audittrail.Application", {
    extend: "NOC.core.ModelApplication",
    requires: [
        "NOC.main.audittrail.Model",
        "NOC.main.user.LookupField"
    ],
    model: "NOC.main.audittrail.Model",
    search: true,
    columns: [
        {
            text: "User",
            dataIndex: "user__label",
            flex: 1
        },
        {
            text: "Timestamp",
            dataIndex: "timestamp",
            width: 160
        },
        {
            text: "Model",
            dataIndex: "model",
            flex: 2
        },
        {
            text: "Table",
            dataIndex: "db_table",
            flex: 2
        },
        {
            text: "Operation",
            dataIndex: "operation",
            width: 60
        },
        {
            text: "Subject",
            dataIndex: "subject",
            flex: 2
        }
    ],
    fields: [
        {
            name: "user",
            xtype: "main.user.LookupField",
            fieldLabel: "User",
            allowBlank: false
        },
        {
            name: "model",
            xtype: "textfield",
            fieldLabel: "Model",
            allowBlank: false
        },
        {
            name: "db_table",
            xtype: "textfield",
            fieldLabel: "DB Table",
            allowBlank: false
        },
        {
            name: "operation",
            xtype: "combobox",
            fieldLabel: "Operation",
            allowBlank: false,
            store: [["C", "Create"], ["M", "Modify"], ["D", "Delete"]]
        },
        {
            name: "subject",   
            xtype: "textfield",
            fieldLabel: "Subject",   
            allowBlank: false 
        },
        {
            name: "body", 
            xtype: "textareafield",
            fieldLabel: "Body",
            anchor: "70%",
            allowBlank: false
        }
    ],
    filters: [
        {
            title: "By User",
            name: "user",
            ftype: "lookup",
            lookup: "main.user"
        }
    ]
});
