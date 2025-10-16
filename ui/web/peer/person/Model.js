//---------------------------------------------------------------------
// peer.person Model
//---------------------------------------------------------------------
// Copyright (C) 2007-2011 The NOC Project
// See LICENSE for details
//---------------------------------------------------------------------
console.debug("Defining NOC.peer.person.Model");

Ext.define("NOC.peer.person.Model", {
  extend: "Ext.data.Model",
  rest_url: "/peer/person/",

  fields: [
    {
      name: "id",
      type: "string",
    },
    {
      name: "nic_hdl",
      type: "string",
    },
    {
      name: "person",
      type: "string",
    },
    {
      name: "type",
      defaultValue: "P",
      type: "string",
    },
    {
      name: "address",
      type: "string",
    },
    {
      name: "phone",
      type: "string",
    },
    {
      name: "fax_no",
      type: "string",
    },
    {
      name: "email",
      type: "string",
    },
    {
      name: "rir",
      type: "string",
    },
    {
      name: "rir__label",
      type: "string",
      persist: false,
    },
    {
      name: "extra",
      type: "string",
    },
  ],
});
