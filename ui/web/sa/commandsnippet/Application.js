//---------------------------------------------------------------------
// sa.commandsnippet application
//---------------------------------------------------------------------
// Copyright (C) 2007-2012 The NOC Project
// See LICENSE for details
//---------------------------------------------------------------------
console.debug("Defining NOC.sa.commandsnippet.Application");

Ext.define("NOC.sa.commandsnippet.Application", {
    extend: "NOC.core.ModelApplication",
    requires: [
        "NOC.sa.commandsnippet.Model",
        "NOC.sa.managedobjectselector.LookupField"
    ],
    model: "NOC.sa.commandsnippet.Model",
    search: true,
    columns: [
        {
            text: "Name",
            dataIndex: "name"
        },
        {
            dataIndex: "is_enabled",
            text: "Enabled",
            renderer: NOC.render.Bool
        },
        {
            text: "Object Selector",
            dataIndex: "selector",
            renderer: NOC.render.Lookup("selector")
        },
        {
            text: "Description",
            dataIndex: "description"
        },
        {
            dataIndex: "require_confirmation",
            text: "Require Confirmation",
            renderer: NOC.render.Bool
        },
        {
            dataIndex: "ignore_cli_errors",
            text: "Ignore CLI Errors",
            renderer: NOC.render.Bool 
        },
        {
            text: "Permission",    
            dataIndex: "permission_name"
        },
        {   
            dataIndex: "display_in_menu",   
            text: "Show in menu", 
            renderer: NOC.render.Bool
        },
        {
            text: "Tags",
            dataIndex: "tags",
            renderer: NOC.render.Tags
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
            xtype: "textareafield",
            fieldLabel: "Description",
            allowBlank: false,
            anchor: "100%",
            fieldStyle: {
                fontFamily: "Courier"
            }
        },
        {
            name: "snippet",
            xtype: "textareafield",
            fieldLabel: "Snippet",
            allowBlank: false,
            anchor: "100%",
            height: 200,
            fieldStyle: {
                fontFamily: "Courier"
            }
        },
        {
            name: "change_configuration",
            xtype: "checkboxfield",
            boxLabel: "Change configuration"
        },
        {
            name: "selector",
            xtype: "sa.managedobjectselector.LookupField",
            fieldLabel: "Object Selector",
            allowBlank: false
        },
        {
            name: "is_enabled",
            xtype: "checkboxfield",
            boxLabel: "Is Enabled"
        },
        {
            name: "timeout",
            xtype: "numberfield",
            fieldLabel: "Timeout(sec)",
            allowBlank: false
        },
        {
            name: "require_confirmation",
            xtype: "checkboxfield",
            boxLabel: "Require Confirmation"
        },
        {
            name: "ignore_cli_errors",
            xtype: "checkboxfield",
            boxLabel: "Ignore CLI Errors"
        },
        {
            name: "permission_name",
            xtype: "textfield",
            fieldLabel: "Permission Name"
        },
        {
            name: "display_in_menu",
            xtype: "checkboxfield",
            boxLabel: "Show in menu"
        },
        {
            name: "tags",
            xtype: "tagsfield",
            fieldLabel: "Tags",
            allowBlank: true
        }
    ],
    filters: [
        {
            title: "By Is Enabled",
            name: "is_enabled",
            ftype: "boolean"
        },
        {
            title: "By Require Confirmation",
            name: "require_confirmation",
            ftype: "boolean"
        },
        {
            title: "By Ignore CLI Errors",
            name: "ignore_cli_errors",
            ftype: "boolean"
        } 
    ]
});
