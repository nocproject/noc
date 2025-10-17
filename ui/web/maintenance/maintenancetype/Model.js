//---------------------------------------------------------------------
// maintenance.maintenancetype Model
//---------------------------------------------------------------------
// Copyright (C) 2007-2016 The NOC Project
// See LICENSE for details
//---------------------------------------------------------------------
console.debug("Defining NOC.maintenance.maintenancetype.Model");

Ext.define("NOC.maintenance.maintenancetype.Model", {
  extend: "Ext.data.Model",
  rest_url: "/maintenance/maintenancetype/",

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
      name: "suppress_alarms",
      type: "boolean",
    },
    {
      name: "card_template",
      type: "string",
    },
  ],
});
