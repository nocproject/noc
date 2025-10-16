//---------------------------------------------------------------------
// cm.objectnotify Model
//---------------------------------------------------------------------
// Copyright (C) 2007-2019 The NOC Project
// See LICENSE for details
//---------------------------------------------------------------------
console.debug("Defining NOC.cm.objectnotify.Model");

Ext.define("NOC.cm.objectnotify.Model", {
  extend: "Ext.data.Model",
  rest_url: "/cm/objectnotify/",

  fields: [
    {
      name: "id",
      type: "string",
    },
    {
      name: "type",
      type: "string",
    },
    {
      name: "administrative_domain",
      type: "string",
    },
    {
      name: "notify_immediately",
      type: "boolean",
      defaultValue: false,
    },
    {
      name: "notify_delayed",
      type: "boolean",
      defaultValue: false,
    },
    {
      name: "notification_group",
      type: "string",
    },
  ],
});