//---------------------------------------------------------------------
// peer.communitytype Model
//---------------------------------------------------------------------
// Copyright (C) 2007-2011 The NOC Project
// See LICENSE for details
//---------------------------------------------------------------------
console.debug("Defining NOC.peer.communitytype.Model");

Ext.define("NOC.peer.communitytype.Model", {
  extend: "Ext.data.Model",
  rest_url: "/peer/communitytype/",

  fields: [
    {
      name: "id",
      type: "string",
    },
    {
      name: "name",
      type: "string",
    },
  ],
});
