//---------------------------------------------------------------------
// sa.actioncommands Model
//---------------------------------------------------------------------
// Copyright (C) 2007-2017 The NOC Project
// See LICENSE for details
//---------------------------------------------------------------------
console.debug("Defining NOC.sa.actioncommands.Model");

Ext.define("NOC.sa.actioncommands.Model", {
  extend: "Ext.data.Model",
  rest_url: "/sa/actioncommands/",

  fields: [
    {
      name: "id",
      type: "string",
    },
    {
      name: "profile",
      type: "string",
    },
    {
      name: "profile__label",
      type: "string",
      persist: false,
    },
    {
      name: "commands",
      type: "string",
    },
    {
      name: "description",
      type: "string",
    },
    {
      name: "uuid",
      type: "string",
    },
    {
      name: "name",
      type: "string",
    },
    {
      name: "action",
      type: "string",
    },
    {
      name: "exit_scope_commands",
      type: "string",
    },
    {
      name: "match",
      type: "auto",
    },
    {
      name: "scopes",
      type: "auto",
    },
    {
      name: "test_cases",
      type: "auto",
    },
    {
      name: "config_mode",
      type: "boolean",
    },
    {
      name: "disable_when_change",
      type: "string",
      defaultValue: "N",
    },
    {
      name: "preference",
      type: "integer",
    },
    {
      name: "timeout",
      type: "integer",
    },
    {
      name: "is_builtin",
      type: "boolean",
      persist: false,
    },
  ],
});
