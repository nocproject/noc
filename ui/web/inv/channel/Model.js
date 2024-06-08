//---------------------------------------------------------------------
// inv.channel Model
//---------------------------------------------------------------------
// Copyright (C) 2007-2024 The NOC Project
// See LICENSE for details
//---------------------------------------------------------------------
console.debug("Defining NOC.inv.channel.Model");

Ext.define("NOC.inv.channel.Model", {
  extend: "Ext.data.Model",
  rest_url: "/inv/channel/",

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
      name: "parent",
      type: "string",
    },
    {
      name: "parent__label",
      type: "string",
      persist: false,
    },
    {
      name: "tech_domain",
      type: "string",
    },
    {
      name: "tech_domain__label",
      type: "string",
      persist: false,
    },  
    {
      name: "description",
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
      name: "supplier",
      type: "string",
    },
    {
      name: "supplier__label",
      type: "string",
      persist: false,
    },
    {
      name: "subscriber",
      type: "string",
    },
    {
      name: "subscriber__label",
      type: "string",
      persist: false,
    },
    {
      name: "labels",
      type: "auto",
    },
    {
      name: "effective_labels",
      type: "auto",
      persist: false,
    },
    {
      name: "constraints",
      type: "auto",
    },
    {
      name: "remote_system",
      type: "string",
    },
    {
      name: "remote_id",
      type: "string",
    },
    {
      name: "bi_id",
      type: "int",
      persist: false,
    },
  ],
});