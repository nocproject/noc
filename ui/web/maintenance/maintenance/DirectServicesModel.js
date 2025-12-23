//---------------------------------------------------------------------
// maintenance.maintenance DirectServicesModel
//---------------------------------------------------------------------
// Copyright (C) 2007-2025 The NOC Project
// See LICENSE for details
//---------------------------------------------------------------------
console.debug("Defining NOC.maintenance.maintenance.DirectServicesModel");

Ext.define("NOC.maintenance.maintenance.DirectServicesModel", {
  extend: "Ext.data.Model",
  rest_url: "/maintenance/maintenance/{{parent}}/",
  rootProperty: "direct_services",
  parentField: "service",
  isLocal: true,

  fields: [
    {
      name: "service",
      type: "string",
    },
    {
      name: "service__label",
      type: "string",
    },
  ],
});
