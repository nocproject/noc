//---------------------------------------------------------------------
// inv.configuredmap Model
//---------------------------------------------------------------------
// Copyright (C) 2007-2022 The NOC Project
// See LICENSE for details
//---------------------------------------------------------------------
console.debug("Defining NOC.inv.configuredmap.Model");

Ext.define("NOC.inv.configuredmap.Model", {
  extend: "Ext.data.Model",
  rest_url: "/inv/configuredmap/",

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
      name: "layout",
      type: "string",
      defaultValue: "manual",
    },
    {
      name: "width",
      type: "int",
      defaultValue: 0,
    },
    {
      name: "height",
      type: "int",
      defaultValue: 0,
    },
    {
      name: "background_opacity",
      type: "int",
      defaultValue: 30,
    },
    {
      name: "background_image",
      type: "string",
    },
    {
      name: "add_linked_node",
      type: "boolean",
      defaultValue: false,
    },
    {
      name: "enable_node_portal",
      type: "boolean",
    },
    {
      name: "add_topology_links",
      type: "boolean",
    },
    {
      name: "status_filter",
      type: "auto",
    },
    {
      name: "nodes",
      type: "auto",
    },
    {
      name: "links",
      type: "auto",
    },
  ],
});
