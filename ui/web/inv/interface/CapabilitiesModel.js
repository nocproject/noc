//---------------------------------------------------------------------
// sa.managedobject CapabilitiesModel
//---------------------------------------------------------------------
// Copyright (C) 2007-2025 The NOC Project
// See LICENSE for details
//---------------------------------------------------------------------
console.debug("Defining NOC.inv.interface.CapabilitiesModel");

Ext.define("NOC.inv.interface.CapabilitiesModel", {
  extend: "Ext.data.Model",
  rest_url: "/inv/interface/{{parent}}/caps/",
  parentField: "managed_object_id",

  fields: [
    {
      name: "capability",
      type: "string",
    },
    {
      name: "description",
      type: "string",
    },
    {
      name: "source",
      type: "string",
    },
    {
      name: "value",
      type: "auto",
    },
  ],
});

