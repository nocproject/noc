//---------------------------------------------------------------------
// sa.service Instance Model 
//---------------------------------------------------------------------
// Copyright (C) 2007-2024 The NOC Project
// See LICENSE for details
//---------------------------------------------------------------------
console.debug("Defining NOC.sa.service.InstanceModel");

Ext.define("NOC.sa.service.InstanceModel", {
  extend: "Ext.data.Model",
  //   {
  //       "sources": ["M"],
  //       "type": "network",
  //       "fqdn": null,
  //       "port": 0,
  //       "managed_object": null,
  //       "addresses": [],
  //       "name": "port",
  //       "resources": [{"resource": "if:5e4fd5752b579e9447509151", "resource_label": "Name1"}],
  //       "allow_update": true
  //     }]
  fields: [
    {
      name: "name",
      type: "string",
    },
    {
      name: "fqdn",
      type: "string",
    },
    {
      name: "type",
      type: "string",
    },
    {
      name: "sources",
      type: "string",
    },
    {
      name: "port",
      type: "int",
    },
    {
      name: "managed_object",
      type: "string",
    },
    {
      name: "addresses",
      type: "auto",
    },
    {
      name: "resources",
      type: "auto",
    },
    {
      name: "allow_update",
      type: "boolean",
    },
  ],
});