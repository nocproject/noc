//---------------------------------------------------------------------
// maintenance.maintenance DirectSegmentsModel
//---------------------------------------------------------------------
// Copyright (C) 2007-2018 The NOC Project
// See LICENSE for details
//---------------------------------------------------------------------
console.debug("Defining NOC.maintenance.maintenance.DirectSegmentsModel");

Ext.define("NOC.maintenance.maintenance.DirectSegmentsModel", {
  extend: "Ext.data.Model",
  rest_url: "/maintenance/maintenance/{{parent}}/",
  rootProperty: "direct_segments",
  parentField: "segment",
  isLocal: true,

  fields: [
    {
      name: "segment",
      type: "string",
    },
    {
      name: "segment__label",
      type: "string",
    },
  ],
});
