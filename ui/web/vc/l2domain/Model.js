//---------------------------------------------------------------------
// vc.l2domain Model
//---------------------------------------------------------------------
// Copyright (C) 2007-2021 The NOC Project
// See LICENSE for details
//---------------------------------------------------------------------
console.debug("Defining NOC.vc.l2domain.Model");

Ext.define("NOC.vc.l2domain.Model", {
  extend: "Ext.data.Model",
  rest_url: "/vc/l2domain/",

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
      name: "profile",
      type: "string",
    },
    {
      name: "profile__label",
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
      name: "pools",
      type: "auto",
    },
    {
      name: "vlan_template",
      type: "string",
    },
    {
      name: "vlan_template__label",
      type: "string",
      persist: false,
    },
    {
      name: "default_vlan_profile",
      type: "string",
    },
    {
      name: "default_vlan_profile__label",
      type: "string",
      persist: false,
    },
    {
      name: "vlan_discovery_policy",
      type: "string",
      defaultValue: "P",
    },
    {
      name: "vlan_discovery_filter",
      type: "string",
    },
    {
      name: "vlan_discovery_filter__label",
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
      name: "remote_id",
      type: "string",
    },
    {
      name: "labels",
      type: "auto",
    },
    {
      name: "bi_id",
      type: "int",
    },
    {
      name: "count",
      type: "integer",
      persist: false,
    },
    {
      name: "row_class",
      type: "string",
      persist: false,
    },
  ],
});
