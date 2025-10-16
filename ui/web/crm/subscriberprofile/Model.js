//---------------------------------------------------------------------
// crm.subscriberprofile Model
//---------------------------------------------------------------------
// Copyright (C) 2007-2016 The NOC Project
// See LICENSE for details
//---------------------------------------------------------------------
console.debug("Defining NOC.crm.subscriberprofile.Model");

Ext.define("NOC.crm.subscriberprofile.Model", {
  extend: "Ext.data.Model",
  rest_url: "/crm/subscriberprofile/",

  fields: [
    {
      name: "id",
      type: "string",
    },
    {
      name: "style",
      type: "int",
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
      name: "labels",
      type: "auto",
    },
    {
      name: "glyph",
      type: "string",
    },
    {
      name: "display_order",
      type: "integer",
      defaultValue: 100,
    },
    {
      name: "show_in_summary",
      type: "boolean",
    },
    {
      name: "weight",
      type: "int",
    },
    {
      name: "workflow",
      type: "string",
    },
    {
      name: "workflow__label",
      type: "string",
      persist: false,
    },
    {
      name: "row_class",
      type: "string",
      persist: false,
    },
    {
      name: "remote_system",
      type: "string",
    },
    {
      name: "remote_system__label",
      type: "string",
      persist: false,
    },
    {
      name: "remote_id",
      type: "string",
    },
    {
      name: "bi_id",
      type: "string",
      persist: false,
    },
  ],
});
