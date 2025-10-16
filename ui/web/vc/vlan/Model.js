//---------------------------------------------------------------------
// vc.vlan Model
//---------------------------------------------------------------------
// Copyright (C) 2007-2017 The NOC Project
// See LICENSE for details
//---------------------------------------------------------------------
console.debug("Defining NOC.vc.vlan.Model");

Ext.define("NOC.vc.vlan.Model", {
  extend: "Ext.data.Model",
  rest_url: "/vc/vlan/",

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
      name: "apply_translation",
      type: "boolean",
      defaultValue: true,
    },
    {
      name: "vlan",
      type: "int",
    },
    {
      name: "description",
      type: "string",
    },
    {
      name: "labels",
      type: "auto",
    },
    {
      name: "l2_domain",
      type: "string",
    },
    {
      name: "l2_domain__label",
      type: "string",
      persist: false,
    },
    {
      name: "remote_id",
      type: "string",
    },
    {
      name: "project",
      type: "string",
    },
    {
      name: "project__label",
      type: "string",
      persist: false,
    },
    {
      name: "state",
      type: "string",
      persist: false,
    },
    {
      name: "state__label",
      type: "string",
      persist: false,
    },
    {
      name: "remote_system",
      type: "string",
    },
    {
      name: "remote_system__label",
      type: "string",
      persist: false,
    },
    {
      name: "bi_id",
      type: "string",
    },
    {
      name: "name",
      type: "string",
    },
    // Info fields
    {
      name: "interfaces_count",
      type: "auto",
      persist: false,
    },
    {
      name: "prefixes",
      type: "auto",
      persist: false,
    },
    {
      name: "row_class",
      type: "string",
      persist: false,
    },
    {
      name: "first_discovered",
      type: "string",
      persist: false,
    },
    {
      name: "last_seen",
      type: "string",
      persist: false,
    },
    {
      name: "expired",
      type: "string",
      persist: false,
    },
  ],
});
