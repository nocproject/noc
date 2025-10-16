//---------------------------------------------------------------------
// fm.alarmdiagnosticconfig Model
//---------------------------------------------------------------------
// Copyright (C) 2007-2016 The NOC Project
// See LICENSE for details
//---------------------------------------------------------------------
console.debug("Defining NOC.fm.alarmdiagnosticconfig.Model");

Ext.define("NOC.fm.alarmdiagnosticconfig.Model", {
  extend: "Ext.data.Model",
  rest_url: "/fm/alarmdiagnosticconfig/",

  fields: [
    {
      name: "id",
      type: "string",
    },
    {
      name: "enable_periodic",
      type: "boolean",
      defaultValue: true,
    },
    {
      name: "alarm_class",
      type: "string",
    },
    {
      name: "alarm_class__label",
      type: "string",
      persist: false,
    },
    {
      name: "on_raise_script",
      type: "string",
    },
    {
      name: "enable_on_raise",
      type: "boolean",
      defaultValue: true,
    },
    {
      name: "on_raise_header",
      type: "string",
    },
    {
      name: "periodic_header",
      type: "string",
    },
    {
      name: "on_clear_header",
      type: "string",
    },
    {
      name: "periodic_interval",
      type: "int",
    },
    {
      name: "on_clear_action",
      type: "string",
    },
    {
      name: "on_clear_action__label",
      type: "string",
      persist: false,
    },
    {
      name: "on_clear_handler",
      type: "string",
    },
    {
      name: "periodic_script",
      type: "string",
    },
    {
      name: "periodic_handler",
      type: "string",
    },
    {
      name: "description",
      type: "string",
    },
    {
      name: "enable_on_clear",
      type: "boolean",
      defaultValue: true,
    },
    {
      name: "periodic_action",
      type: "string",
    },
    {
      name: "periodic_action__label",
      type: "string",
      persist: false,
    },
    {
      name: "is_active",
      type: "boolean",
      defaultValue: true,
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
      name: "only_root",
      type: "boolean",
      defaultValue: true,
    },
    {
      name: "on_raise_action",
      type: "string",
    },
    {
      name: "on_raise_action__label",
      type: "string",
      persist: false,
    },
    {
      name: "on_clear_script",
      type: "string",
    },
    {
      name: "name",
      type: "string",
    },
    {
      name: "on_raise_handler",
      type: "string",
    },
    {
      name: "on_raise_delay",
      type: "int",
    },
    {
      name: "on_clear_delay",
      type: "int",
    },
  ],
});
