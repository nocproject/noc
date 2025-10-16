//---------------------------------------------------------------------
// maintenance.maintenance DirectObjectsModel
//---------------------------------------------------------------------
// Copyright (C) 2007-2018 The NOC Project
// See LICENSE for details
//---------------------------------------------------------------------
console.debug("Defining NOC.maintenance.maintenance.DirectObjectsModel");

Ext.define("NOC.maintenance.maintenance.DirectObjectsModel", {
  extend: "Ext.data.Model",
  rest_url: "/maintenance/maintenance/{{parent}}/",
  rootProperty: "direct_objects",
  parentField: "object",
  isLocal: true,

  fields: [
    {
      name: "object",
      type: "string",
    },
    {
      name: "object__label",
      type: "string",
    },
  ],
});
