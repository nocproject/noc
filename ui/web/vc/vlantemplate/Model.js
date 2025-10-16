//---------------------------------------------------------------------
// vc.vlantemplate Model
//---------------------------------------------------------------------
// Copyright (C) 2007-2021 The NOC Project
// See LICENSE for details
//---------------------------------------------------------------------
console.debug("Defining NOC.vc.vlantemplate.Model");

Ext.define("NOC.vc.vlantemplate.Model", {
  extend: "Ext.data.Model",
  rest_url: "/vc/vlantemplate/",

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
      name: "type",
      type: "string",
    },
    {
      name: "vlans",
      type: "auto",
    },
  ],
});
