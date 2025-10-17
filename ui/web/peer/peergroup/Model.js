//---------------------------------------------------------------------
// peer.peergroup Model
//---------------------------------------------------------------------
// Copyright (C) 2007-2011 The NOC Project
// See LICENSE for details
//---------------------------------------------------------------------
console.debug("Defining NOC.peer.peergroup.Model");

Ext.define("NOC.peer.peergroup.Model", {
  extend: "Ext.data.Model",
  rest_url: "/peer/peergroup/",

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
      name: "communities",
      type: "string",
    },
    {
      name: "max_prefixes",
      defaultValue: 100,
      type: "int",
    },
    {
      name: "local_pref",
      type: "int",   
    },
    {
      name: "import_med",
      type: "int",   
    },
    {
      name: "export_med",
      type: "int",
    },
  ],
});
