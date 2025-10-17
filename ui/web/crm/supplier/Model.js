//---------------------------------------------------------------------
// crm.supplier Model
//---------------------------------------------------------------------
// Copyright (C) 2007-2017 The NOC Project
// See LICENSE for details
//---------------------------------------------------------------------
console.debug("Defining NOC.crm.supplier.Model");

Ext.define("NOC.crm.supplier.Model", {
  extend: "Ext.data.Model",
  rest_url: "/crm/supplier/",

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
      name: "labels",
      type: "auto",
    },
    {
      name: "is_affilated",
      type: "boolean",
    },
    {
      name: "name",
      type: "string",
    },
  ],
});
