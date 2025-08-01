//---------------------------------------------------------------------
// inv.inv AlarmModel
//---------------------------------------------------------------------
// Copyright (C) 2007-2025 The NOC Project
// See LICENSE for details
//---------------------------------------------------------------------
console.debug("Defining NOC.inv.inv.plugins.alarm.AlarmModel");

Ext.define("NOC.inv.inv.plugins.alarm.AlarmModel", {
  extend: "Ext.data.Model",
  fields: [
    {
      name: "id",
      type: "string",
    },
    {
      name: "title",
      type: "string",
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
      name: "channel",
      type: "string",
    },
    {
      name: "channel__label",
      type: "string",
      persist: false,
    },
    {
      name: "object",
      type: "auto",
    },
  ],
});
