//---------------------------------------------------------------------
// inv.networksegmentprofile Model
//---------------------------------------------------------------------
// Copyright (C) 2007-2020 The NOC Project
// See LICENSE for details
//---------------------------------------------------------------------
console.debug("Defining NOC.inv.networksegmentprofile.Model");

Ext.define("NOC.inv.networksegmentprofile.Model", {
  extend: "Ext.data.Model",
  rest_url: "/inv/networksegmentprofile/",

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
      name: "discovery_interval",
      type: "int",
      defaultValue: 0,
    },
    {
      name: "autocreated_profile",
      type: "string",
    },
    {
      name: "enable_lost_redundancy",
      type: "boolean",
    },
    {
      name: "topology_methods",
      type: "auto",
    },
    {
      name: "uplink_policy",
      type: "auto",
    },
    {
      name: "management_vlan",
      type: "int",
      allowNull: true,
    },
    {
      name: "multicast_vlan",
      type: "int",
      allowNull: true,
    },
    {
      name: "mac_restrict_to_management_vlan",
      type: "boolean",
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
      name: "horizontal_transit_policy",
      type: "string",
    },
    {
      name: "enable_vlan",
      type: "boolean",
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
      name: "style",
      type: "int",
    },
    {
      name: "style__label",
      type: "string",
      persist: false,
    },
    {
      name: "is_persistent",
      type: "boolean",
    },
    {
      name: "bio_collision_policy",
      type: "auto",
    },
    {
      name: "calcified_profile",
      type: "string",
    },
    {
      name: "calcified_profile__label",
      type: "string",
    },
    {
      name: "calcified_name_template",
      type: "string",
    },
    {
      name: "calcified_name_template__label",
      type: "string",
    },
    {
      name: "row_class",
      type: "string",
      persist: false,
    },
  ],
});
