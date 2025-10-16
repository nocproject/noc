//---------------------------------------------------------------------
// vc.vlanfilter Model
//---------------------------------------------------------------------
// Copyright (C) 2007-2012 The NOC Project
// See LICENSE for details
//---------------------------------------------------------------------
console.debug("Defining NOC.vc.vlanfilter.Model");

Ext.define("NOC.vc.vlanfilter.Model", {
  extend: "Ext.data.Model",
  rest_url: "/vc/vlanfilter/",

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
      name: "include_expression",
      type: "string",
    },
    {
      name: "exclude_expression",
      type: "string",
    },
    {
      name: "description",
      type: "string",
    },
    {
      name: "match_labels",
      type: "auto",
      persist: false,
    },
  ],
});
