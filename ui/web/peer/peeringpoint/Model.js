//---------------------------------------------------------------------
// peer.peeringpoint Model
//---------------------------------------------------------------------
// Copyright (C) 2007-2012 The NOC Project
// See LICENSE for details
//---------------------------------------------------------------------
console.debug("Defining NOC.peer.peeringpoint.Model");

Ext.define("NOC.peer.peeringpoint.Model", {
  extend: "Ext.data.Model",
  rest_url: "/peer/peeringpoint/",

  fields: [
    {
      name: "id",
      type: "string",
    },
    {
      name: "hostname",
      type: "string",
    },
    {
      name: "location",
      type: "string",
    },
    {
      name: "local_as",
      type: "string",
    },
    {
      name: "local_as__label",
      type: "string",
      persist: false,
    },
    {
      name: "router_id",
      type: "string",
    },
    {
      name: "profile",
      type: "string",
    },
    {
      name: "profile__label",
      type: "string",
      persist: false,
    },
    {
      name: "communities",
      type: "string",
    },
    {
      name: "prefix_list_notification_group", 
      type: "string",
    },
    {
      name: "enable_prefix_list_provisioning",
      type: "boolean",
      defaultValue: false,
    },
  ],
});
