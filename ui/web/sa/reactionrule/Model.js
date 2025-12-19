//---------------------------------------------------------------------
// sa.reactionrule Model
//---------------------------------------------------------------------
// Copyright (C) 2007-2025 The NOC Project
// See LICENSE for details
//---------------------------------------------------------------------
console.debug("Defining NOC.sa.reactionrule.Model");

Ext.define("NOC.sa.reactionrule.Model", {
  extend: "Ext.data.Model",
  rest_url: "/sa/reactionrule/",

  fields: [
    {
      name: "id",
      type: "string",
    },
    {
      name: "description",
      type: "string",
    },
    {
      name: "name",
      type: "string",
    },
    {
      name: "uuid",
      type: "string",
    },
    {
      name: "is_active",
      type: "boolean",
    },
    {
      name: "is_builtin",
      type: "boolean",
      persist: false,
    },
    {
      name: "replace_rule_policy",
      type: "string",
    },
    {
      name: "replace_rule",
      type: "string",
    },
    {
      name: "replace_rule__label",
      type: "string",
      persist: false,
    },
    {
      name: "notification_policy",
      type: "string",
      defaultValue: "D",
    },
    {
      name: "notification_group",
      type: "string",
    },
    {
      name: "notification_group__label",
      type: "string",
      persist: false,
    },
    {
      name: "subject_template",
      type: "string",
    },
    {
      name: "object_model",
      type: "string",
    },
    {
      name: "operations",
      type: "auto",
    },
    {
      name: "conditions",
      type: "auto",
    },
    {
      name: "actions",
      type: "auto",
    },
    {
      name: "field_data",
      type: "auto",
    },
    {
      name: "affected_rules",
      type: "auto",
    },
    {
      name: "preference",
      type: "int",
      defaultValue: 1000,
    },
    {
      name: "stop_processing",
      type: "boolean",
    },
    {
      name: "alarm_disposition",
      type: "string",
    },
    {
      name: "alarm_disposition__label",
      type: "string",
      persist: false,
    },
    {
      name: "bi_id",
      type: "string",
      persist: false,
    },
  ],
});
