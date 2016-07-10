//---------------------------------------------------------------------
// main.dbtrigger application
//---------------------------------------------------------------------
// Copyright (C) 2007-2012 The NOC Project
// See LICENSE for details
//---------------------------------------------------------------------
console.debug("Defining NOC.main.dbtrigger.Application");

Ext.define("NOC.main.dbtrigger.Application", {
    extend: "NOC.core.ModelApplication",
    uses: [
        "NOC.main.dbtrigger.Model",
        "NOC.main.pyrule.LookupField",
        "NOC.main.ref.model.LookupField"
    ],
    model: "NOC.main.dbtrigger.Model",
    columns: [
        {
            text: "Model",
            dataIndex: "model"
        },
        {
            text: "Name",
            dataIndex: "name"
        },
        {
            text: "Active",
            dataIndex: "is_active",
            width: 50,
            renderer: NOC.render.Bool
        },
        {
            text: "Order",
            dataIndex: "order",
            width: 70,
            align: "right"
        },
        {
            text: "PreSave",
            dataIndex: "pre_save_rule",
            renderer: NOC.render.Lookup("pre_save_rule")
        },
        {
            text: "PostSave",
            dataIndex: "post_save_rule",
            renderer: NOC.render.Lookup("post_save_rule")
        },
        {
            text: "PreDelete",
            dataIndex: "pre_delete_rule",
            renderer: NOC.render.Lookup("pre_delete_rule")
        },
        {
            text: "PostDelete",
            dataIndex: "post_delete_rule",
            renderer: NOC.render.Lookup("post_delete_rule")
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
            name: "model",
            xtype: "main.ref.model.LookupField",
            fieldLabel: "Model",
            allowBlank: false
        },
        {
            name: "is_active",
            xtype: "checkboxfield",
            boxLabel: "Is Active",
            allowBlank: false
        },
        {
            name: "order",
            xtype: "numberfield",
            fieldLabel: "Order",
            allowBlank: false
        },
        {
            name: "description",
            xtype: "textarea",
            fieldLabel: "Description",
            allowBlank: true
        },
        {
            name: "pre_save_rule",
            xtype: "main.pyrule.LookupField",
            fieldLabel: "Pre-Save Rule",
            allowBlank: true,
            query: {
                interface: "IDBPreSave"
            }
        },
        {
            name: "post_save_rule",
            xtype: "main.pyrule.LookupField",
            fieldLabel: "Post-Save Rule",
            allowBlank: true,
            query: {
                interface: "IDBPostSave"
            }
        },
        {
            name: "pre_delete_rule",
            xtype: "main.pyrule.LookupField",
            fieldLabel: "Pre-Delete Rule",
            allowBlank: true,
            query: {
                interface: "IDBPreDelete"
            }
        },
        {
            name: "post_delete_rule",
            xtype: "main.pyrule.LookupField",
            fieldLabel: "Post-Delete Rule",
            allowBlank: true,
            query: {
                interface: "IDBPostDelete"
            }
        }
    ],
    filters: [
        {
            title: "By Active",
            name: "is_active",
            ftype: "boolean"
        }
    ]
});
