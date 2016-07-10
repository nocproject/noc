//---------------------------------------------------------------------
// main.customfield application
//---------------------------------------------------------------------
// Copyright (C) 2007-2012 The NOC Project
// See LICENSE for details
//---------------------------------------------------------------------
console.debug("Defining NOC.main.customfield.Application");

Ext.define("NOC.main.customfield.Application", {
    extend: "NOC.core.ModelApplication",
    requires: [
        "NOC.main.customfield.Model",
        "NOC.main.ref.modcol.LookupField",
        "NOC.main.customfieldenumgroup.LookupField"
    ],
    model: "NOC.main.customfield.Model",
    search: true,
    columns: [
        {
            text: "Table",
            dataIndex: "table"
        },
        {
            text: "Name",
            dataIndex: "name"
        },
        {
            text: "Active",
            dataIndex: "is_active",
            renderer: NOC.render.Bool
        },
        {
            text: "Label",
            dataIndex: "label"
        },
        {
            text: "Type",
            dataIndex: "type"
        },
        {
            text: "Enum Group",
            dataIndex: "enum_group",
            renderer: NOC.render.Lookup("enum_group")
        },
        {
            text: "Indexed",
            dataIndex: "is_indexed",
            renderer: NOC.render.Bool
        },
        {
            text: "Searchable",
            dataIndex: "is_searchable",
            renderer: NOC.render.Bool
        },
        {
            text: "Filtered",
            dataIndex: "is_filtered",
            renderer: NOC.render.Bool
        },
        {
            text: "Hidden",
            dataIndex: "is_hidden",
            renderer: NOC.render.Bool
        }
    ],
    fields: [
        {
            name: "table",
            xtype: "main.ref.modcol.LookupField",
            fieldLabel: "Table",
            allowBlank: false
        },
        {
            name: "name",
            xtype: "textfield",
            fieldLabel: "Name",
            allowBlank: false,
            regex: /^[a-zA-Z0-9_]+$/
        },
        {
            name: "is_active",
            xtype: "checkboxfield",
            boxLabel: "Is Active",
            allowBlank: false
        },
        {
            name: "label",
            xtype: "textfield",
            fieldLabel: "Label",
            allowBlank: false
        },
        {
            name: "type",
            xtype: "combobox",
            fieldLabel: "Type",
            allowBlank: false,
            queryMode: "local",
            displayField: "label",
            valueField: "id",
            store: {
                fields: ["id", "label"],
                data: [
                    {id: "str", label: "String"},
                    {id: "int", label: "Integer"},
                    {id: "bool", label: "Boolean"},
                    {id: "date", label: "Date"},
                    {id: "datetime", label: "Date&Time"}
                ]
            }
        },
        {
            name: "enum_group",
            xtype: "main.customfieldenumgroup.LookupField",
            fieldLabel: "Enum Group",
            allowBlank: true,
            query: {
                is_active: true
            }
        },
        {
            name: "description",
            xtype: "textarea",
            fieldLabel: "Description",
            allowBlank: true
        },
        {
            name: "max_length",
            xtype: "numberfield",
            fieldLabel: "Max. Length",
            allowBlank: true
        },
        {
            name: "regexp",
            xtype: "textfield",
            fieldLabel: "Regexp",
            allowBlank: true
        },
        {
            name: "is_indexed",
            xtype: "checkboxfield",
            boxLabel: "Is Indexed",
            allowBlank: false
        },
        {
            name: "is_searchable",
            xtype: "checkboxfield",
            boxLabel: "Is Searchable",
            allowBlank: false
        },
        {
            name: "is_filtered",
            xtype: "checkboxfield",
            boxLabel: "Is Filtered",
            allowBlank: false
        },
        {
            name: "is_hidden",
            xtype: "checkboxfield",
            boxLabel: "Is Hidden",
            allowBlank: false
        }
    ],
    filters: [
        {
            title: "By Active",
            name: "is_active",
            ftype: "boolean"
        },
        {
            title: "By Searchable",
            name: "is_searchable",
            ftype: "boolean"
        },
        {
            title: "By Filtered",
            name: "is_filtered",
            ftype: "boolean"
        },
        {
            title: "By Hidden",
            name: "is_hidden",
            ftype: "boolean"
        }
    ]
});
