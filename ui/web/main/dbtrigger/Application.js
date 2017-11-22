//---------------------------------------------------------------------
// main.dbtrigger application
//---------------------------------------------------------------------
// Copyright (C) 2007-2012 The NOC Project
// See LICENSE for details
//---------------------------------------------------------------------
console.debug("Defining NOC.main.dbtrigger.Application");

Ext.define("NOC.main.dbtrigger.Application", {
    extend: "NOC.core.ModelApplication",
    requires: [
        "NOC.main.dbtrigger.Model",
        "NOC.main.pyrule.LookupField",
        "NOC.main.ref.model.LookupField"
    ],
    model: "NOC.main.dbtrigger.Model",
    columns: [
        {
            text: __("Model"),
            dataIndex: "model"
        },
        {
            text: __("Name"),
            dataIndex: "name"
        },
        {
            text: __("Active"),
            dataIndex: "is_active",
            width: 50,
            renderer: NOC.render.Bool
        },
        {
            text: __("Order"),
            dataIndex: "order",
            width: 70,
            align: "right"
        },
        {
            text: __("PreSave"),
            dataIndex: "pre_save_rule",
            renderer: NOC.render.Lookup("pre_save_rule")
        },
        {
            text: __("PostSave"),
            dataIndex: "post_save_rule",
            renderer: NOC.render.Lookup("post_save_rule")
        },
        {
            text: __("PreDelete"),
            dataIndex: "pre_delete_rule",
            renderer: NOC.render.Lookup("pre_delete_rule")
        },
        {
            text: __("PostDelete"),
            dataIndex: "post_delete_rule",
            renderer: NOC.render.Lookup("post_delete_rule")
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
            name: "model",
            xtype: "main.ref.model.LookupField",
            fieldLabel: __("Model"),
            allowBlank: false
        },
        {
            name: "is_active",
            xtype: "checkboxfield",
            boxLabel: __("Is Active"),
            allowBlank: false
        },
        {
            name: "order",
            xtype: "numberfield",
            fieldLabel: __("Order"),
            allowBlank: false
        },
        {
            name: "description",
            xtype: "textarea",
            fieldLabel: __("Description"),
            allowBlank: true
        },
        {
            name: "pre_save_rule",
            xtype: "main.pyrule.LookupField",
            fieldLabel: __("Pre-Save Rule"),
            allowBlank: true,
            query: {
                interface: "IDBPreSave"
            }
        },
        {
            name: "post_save_rule",
            xtype: "main.pyrule.LookupField",
            fieldLabel: __("Post-Save Rule"),
            allowBlank: true,
            query: {
                interface: "IDBPostSave"
            }
        },
        {
            name: "pre_delete_rule",
            xtype: "main.pyrule.LookupField",
            fieldLabel: __("Pre-Delete Rule"),
            allowBlank: true,
            query: {
                interface: "IDBPreDelete"
            }
        },
        {
            name: "post_delete_rule",
            xtype: "main.pyrule.LookupField",
            fieldLabel: __("Post-Delete Rule"),
            allowBlank: true,
            query: {
                interface: "IDBPostDelete"
            }
        }
    ],
    filters: [
        {
            title: __("By Active"),
            name: "is_active",
            ftype: "boolean"
        }
    ]
});
