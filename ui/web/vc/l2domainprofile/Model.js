//---------------------------------------------------------------------
// vc.l2domainprofile Model
//---------------------------------------------------------------------
// Copyright (C) 2007-2021 The NOC Project
// See LICENSE for details
//---------------------------------------------------------------------
console.debug("Defining NOC.vc.l2domainprofile.Model");

Ext.define("NOC.vc.l2domainprofile.Model", {
  extend: "Ext.data.Model",
  rest_url: "/vc/l2domainprofile/",

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
      name: "workflow",
      type: "string",
    },
    {
      name: "style",
      type: "int",
    },
    {
      name: "style__label",
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
      name: "template__label",
      type: "string",
      persist: false,
    },
    {
      name: "vlan_discovery_policy",
      type: "string",
      defaultValue: "E",
    },
    {
      name: "provisioning_policy",
      type: "string",
      defaultValue: "D",
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
      name: "row_class",
      type: "string",
      persist: false,
    },
  ],
});
