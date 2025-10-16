//---------------------------------------------------------------------
// peer.organisation Model
//---------------------------------------------------------------------
// Copyright (C) 2007-2011 The NOC Project
// See LICENSE for details
//---------------------------------------------------------------------
console.debug("Defining NOC.peer.organisation.Model");

Ext.define("NOC.peer.organisation.Model", {
  extend: "Ext.data.Model",
  rest_url: "/peer/organisation/",

  fields: [
    {
      name: "id",
      type: "string",
    },
    {
      name: "organisation",
      type: "string",
    },
    {
      name: "org_name",
      type: "string",
    },
    {
      name: "org_type",
      type: "string",
    },
    {
      name: "address",
      type: "string",
    },
    {
      name: "mnt_ref",
      type: "string",
    },
  ],
});
