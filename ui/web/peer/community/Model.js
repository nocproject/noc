//---------------------------------------------------------------------
// peer.community Model
//---------------------------------------------------------------------
// Copyright (C) 2007-2012 The NOC Project
// See LICENSE for details
//---------------------------------------------------------------------
console.debug("Defining NOC.peer.community.Model");

Ext.define("NOC.peer.community.Model", {
  extend: "Ext.data.Model",
  rest_url: "/peer/community/",

  fields: [
    {
      name: "id",
      type: "string",
    },
    {
      name: "community",
      type: "string",
    },
    {
      name: "type",
      type: "string",
    },
    {
      name: "type__label",
      type: "string",
      persist: false,
    },
    {
      name: "description",
      type: "string",
    },
  ],
});
