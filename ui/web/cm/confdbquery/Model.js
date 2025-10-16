//---------------------------------------------------------------------
// cm.confdbquery Model
//---------------------------------------------------------------------
// Copyright (C) 2007-2019 The NOC Project
// See LICENSE for details
//---------------------------------------------------------------------
console.debug("Defining NOC.cm.confdbquery.Model");

Ext.define("NOC.cm.confdbquery.Model", {
  extend: "Ext.data.Model",
  rest_url: "/cm/confdbquery/",

  fields: [
    {
      name: "id",
      type: "string",
    },
    {
      name: "allow_object_classification",
      type: "boolean",
    },
    {
      name: "allow_interface_classification",
      type: "boolean",
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
      name: "allow_interface_validation",
      type: "boolean",
    },
    {
      name: "source",
      type: "string",
    },
    {
      name: "allow_object_validation",
      type: "boolean",
    },
    {
      name: "allow_object_filter",
      type: "boolean",
    },
    {
      name: "allow_interface_filter",
      type: "boolean",
    },
    {
      name: "uuid",
      type: "string",
    },
    {
      name: "params",
      type: "auto",
    },
    {
      name: "require_raw",
      type: "boolean",
    },
  ],
});