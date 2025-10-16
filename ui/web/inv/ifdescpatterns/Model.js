//---------------------------------------------------------------------
// inv.ifdescpatterns Model
//---------------------------------------------------------------------
// Copyright (C) 2007-2020 The NOC Project
// See LICENSE for details
//---------------------------------------------------------------------
console.debug("Defining NOC.inv.ifdescpatterns.Model");

Ext.define("NOC.inv.ifdescpatterns.Model", {
  extend: "Ext.data.Model",
  rest_url: "/inv/ifdescpatterns/",

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
      name: "description",
      type: "string",
    },
    {
      name: "resolve_remote_port_by_object",
      type: "boolean",
    },
    {
      name: "patterns",
      type: "auto",
    },
  ],
});