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
    "NOC.core.label.LabelField",
    "NOC.sa.commandsnippet.Model",
    "NOC.core.combotree.ComboTree",
  ],
  model: "NOC.sa.commandsnippet.Model",
  search: true,
  columns: [
    {
      text: __("Name"),
      dataIndex: "name",
    },
    {
      dataIndex: "is_enabled",
      text: __("Enabled"),
      renderer: NOC.render.Bool,
    },
    {
      text: __("Resource Group"),
      dataIndex: "resource_group",
      renderer: NOC.render.Lookup("resource_group"),
      width: 200,
    },
    {
      text: __("Description"),
      dataIndex: "description",
    },
    {
      dataIndex: "require_confirmation",
      text: __("Require Confirmation"),
      renderer: NOC.render.Bool,
    },
    {
      dataIndex: "ignore_cli_errors",
      text: __("Ignore CLI Errors"),
      renderer: NOC.render.Bool, 
    },
    {
      text: __("Permission"),    
      dataIndex: "permission_name",
    },
    {   
      dataIndex: "display_in_menu",   
      text: __("Show in menu"), 
      renderer: NOC.render.Bool,
    },
    {
      text: __("Tags"),
      dataIndex: "tags",
      renderer: NOC.render.Tags,
    },
  ],
  fields: [
    {
      name: "name",
      xtype: "textfield",
      fieldLabel: __("Name"),
      allowBlank: false,
    },
    {
      name: "description",
      xtype: "textareafield",
      fieldLabel: __("Description"),
      allowBlank: false,
      anchor: "100%",
      fieldStyle: {
        fontFamily: "Courier",
      },
    },
    {
      name: "snippet",
      xtype: "textareafield",
      fieldLabel: __("Snippet"),
      allowBlank: false,
      anchor: "100%",
      height: 200,
      fieldStyle: {
        fontFamily: "Courier",
      },
    },
    {
      name: "change_configuration",
      xtype: "checkboxfield",
      boxLabel: __("Change configuration"),
    },
    {
      name: "resource_group",
      xtype: "noc.core.combotree",
      restUrl: "/inv/resourcegroup/",
      fieldLabel: __("Resource Group"),
      listWidth: 1,
      listAlign: "left",
      labelAlign: "left",
      width: 500,
    },
    {
      name: "is_enabled",
      xtype: "checkboxfield",
      boxLabel: __("Is Enabled"),
    },
    {
      name: "timeout",
      xtype: "numberfield",
      fieldLabel: __("Timeout(sec)"),
      allowBlank: false,
    },
    {
      name: "require_confirmation",
      xtype: "checkboxfield",
      boxLabel: __("Require Confirmation"),
    },
    {
      name: "ignore_cli_errors",
      xtype: "checkboxfield",
      boxLabel: __("Ignore CLI Errors"),
    },
    {
      name: "permission_name",
      xtype: "textfield",
      fieldLabel: __("Permission Name"),
    },
    {
      name: "display_in_menu",
      xtype: "checkboxfield",
      boxLabel: __("Show in menu"),
    },
    {
      name: "labels",
      xtype: "labelfield",
      fieldLabel: __("Labels"),
      allowBlank: true,
      query: {
        "enable_commandsnippet": true,
      },
    },
  ],
  filters: [
    {
      title: __("By Is Enabled"),
      name: "is_enabled",
      ftype: "boolean",
      // },
      // {
      //     title: __("By Require Confirmation"),
      //     name: "require_confirmation",
      //     ftype: "boolean"
      // },
      // {
      //     title: __("By Ignore CLI Errors"),
      //     name: "ignore_cli_errors",
      //     ftype: "boolean"
    }, 
  ],
});
