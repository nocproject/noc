//---------------------------------------------------------------------
// sa.commandsnippet Model
//---------------------------------------------------------------------
// Copyright (C) 2007-2011 The NOC Project
// See LICENSE for details
//---------------------------------------------------------------------
console.debug("Defining NOC.sa.commandsnippet.Model");

Ext.define("NOC.sa.commandsnippet.Model", {
  extend: "Ext.data.Model",
  rest_url: "/sa/commandsnippet/",

  fields: [
    {
      name: "id",
      type: "string",
    },
    {
      name: "resource_group",
      type: "string",
    },
    {
      name: "resource_group__label",
      type: "string",
      persist: false,
    },
    {
      name: "name",
      type: "string",
    },
    {
      name: "description",
      type: "string",
    },
    {
      name: "snippet",
      type: "string",
    },
    {
      name: "change_configuration",
      type: "boolean",
      defaultValue: false,
    },
    {
      name: "is_enabled", 
      type: "boolean",
      defaultValue: false,
    },
    {
      name: "timeout",
      defaultValue: "60",
      type: "int",
    },
    {
      name: "require_confirmation",
      type: "boolean",
      defaultValue: false,
    },
    {
      name: "ignore_cli_errors",
      type: "boolean",
      defaultValue: false,
    },
    {
      name: "permission_name",
      type: "string",
    },
    {
      name: "display_in_menu",
      type: "boolean",
      defaultValue: false,
    },
    {
      name: "labels",
      type: "string",
    },
  ],
});
