//---------------------------------------------------------------------
// main.systemnotification Model
//---------------------------------------------------------------------
// Copyright (C) 2007-2012 The NOC Project
// See LICENSE for details
//---------------------------------------------------------------------
console.debug("Defining NOC.main.systemnotification.Model");

Ext.define("NOC.main.systemnotification.Model", {
  extend: "Ext.data.Model",
  rest_url: "/main/systemnotification/",

  fields: [
    {
      name: "id",
      type: "string",
    },
    {
      name: "name",
      type: "string",
    },
    {
      name: "notification_group",
      type: "int",
    },
    {
      name: "notification_group__label",
      type: "string",
      persist: false,
    },
  ],
});
