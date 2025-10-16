//---------------------------------------------------------------------
// vc.vpn Model
//---------------------------------------------------------------------
// Copyright (C) 2007-2017 The NOC Project
// See LICENSE for details
//---------------------------------------------------------------------
console.debug("Defining NOC.vc.vpn.Model");

Ext.define("NOC.vc.vpn.Model", {
  extend: "Ext.data.Model",
  rest_url: "/vc/vpn/",

  fields: [
    {
      name: "id",
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
      name: "route_target",
      type: "auto",
    },
    {
      name: "remote_system",
      type: "string",
    },
    {
      name: "remote_system__label",
      type: "string",
      perisist: false,
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
      name: "remote_id",
      type: "string",
    },
    {
      name: "project",
      type: "int",
    },
    {
      name: "project__label",
      type: "string",
      persist: false,
    },
    {
      name: "parent",
      type: "string",
    },
    {
      name: "parent__label",
      type: "string",
      persist: false,
    },
    {
      name: "state",
      type: "string",
    },
    {
      name: "state__label",
      type: "string",
      persist: false,
    },
    {
      name: "bi_id",
      type: "string",
      persist: false,
    },
    {
      name: "description",
      type: "string",
    },
  ],
});
