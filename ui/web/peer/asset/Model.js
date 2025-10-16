//---------------------------------------------------------------------
// peer.asset Model
//---------------------------------------------------------------------
// Copyright (C) 2007-2012 The NOC Project
// See LICENSE for details
//---------------------------------------------------------------------
console.debug("Defining NOC.peer.asset.Model");

Ext.define("NOC.peer.asset.Model", {
  extend: "Ext.data.Model",
  rest_url: "/peer/asset/",

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
      name: "members",
      type: "string",
    },
    {
      name: "rpsl_header",
      type: "string",
    },
    {
      name: "rpsl_footer",
      type: "string",
    },
    {
      name: "labels",
      type: "auto",
    },
  ],
});
