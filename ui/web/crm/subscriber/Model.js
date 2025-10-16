//---------------------------------------------------------------------
// crm.subscriber Model
//---------------------------------------------------------------------
// Copyright (C) 2007-2016 The NOC Project
// See LICENSE for details
//---------------------------------------------------------------------
console.debug("Defining NOC.crm.subscriber.Model");

Ext.define("NOC.crm.subscriber.Model", {
  extend: "Ext.data.Model",
  rest_url: "/crm/subscriber/",

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
      name: "name",
      type: "string",
    },
    {
      name: "address",
      type: "string",
    },
    {
      name: "tech_contact_person",
      type: "string",
    },
    {
      name: "tech_contact_phone",
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
      name: "row_class",
      type: "string",
      persist: false,
    },
  ],
});
