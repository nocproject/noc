//---------------------------------------------------------------------
// sa.discoveredobject Model
//---------------------------------------------------------------------
// Copyright (C) 2007-2024 The NOC Project
// See LICENSE for details
//---------------------------------------------------------------------
console.debug("Defining NOC.sa.discoveredobject.model.DiscoveredObject");

Ext.define("NOC.sa.discoveredobject.model.DiscoveredObject", {
  extend: "Ext.data.Model",
  fields: [
    {
      name: "id",
      type: "string",
    },
  ],
});