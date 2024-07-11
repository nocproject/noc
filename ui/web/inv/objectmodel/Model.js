//---------------------------------------------------------------------
// inv.objectmodel Model
//---------------------------------------------------------------------
// Copyright (C) 2007-2024 The NOC Project
// See LICENSE for details
//---------------------------------------------------------------------
console.debug("Defining NOC.inv.objectmodel.Model");

Ext.define("NOC.inv.objectmodel.Model", {
  extend: "Ext.data.Model",
  rest_url: "/inv/objectmodel/",

  fields: [
    {
      name: "id",
      type: "string",
    },
    {
      name: "vendor",
      type: "string",
    },
    {
      name: "vendor__label",
      type: "string",
      persist: false,
    },
    {
      name: "short_label",
      type: "string",
    },
    {
      name: "connection_rule",
      type: "string",
    },
    {
      name: "configuration_rule",
      type: "string",
    },
    {
      name: "connection_rule__label",
      type: "string",
      persist: false,
    },
    {
      name: "cr_context",
      type: "string",
    },
    {
      name: "description",
      type: "string",
    },
    {
      name: "connections",
      type: "auto",
    },
    {
      name: "is_builtin",
      type: "boolean",
      persist: false,
    },
    {
      name: "uuid",
      type: "string",
      persist: false,
    },
    {
      name: "data",
      type: "auto",
    },
    {
      name: "sensors",
      type: "auto",
    },
    {
      name: "name",
      type: "string",
    },
    {
      name: "plugins",
      type: "auto",
    },
    {
      name: "labels",
      type: "auto",
    },
    {
      name: "cross",
      type: "auto",
    },
    {
      name: "front_facade",
      type: "string",
    },
    {
      name: "front_facade__label",
      type: "string",
    },
    {
      name: "rear_facade",
      type: "string",
    },
    {
      name: "rear_facade__label",
      type: "string",
    },
  ],
});
