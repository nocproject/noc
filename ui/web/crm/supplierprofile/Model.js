//---------------------------------------------------------------------
// crm.supplierprofile Model
//---------------------------------------------------------------------
// Copyright (C) 2007-2016 The NOC Project
// See LICENSE for details
//---------------------------------------------------------------------
console.debug("Defining NOC.crm.supplierprofile.Model");

Ext.define("NOC.crm.supplierprofile.Model", {
  extend: "Ext.data.Model",
  rest_url: "/crm/supplierprofile/",

  fields: [
    {
      name: "id",
      type: "string",
    },
    {
      name: "style",
      type: "int",
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
      name: "labels",
      type: "auto",
    },
    {
      name: "workflow",
      type: "string",
    },
    {
      name: "workflow__label",
      type: "string",
      persist: false,
    },
    {
      name: "row_class",
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
      name: "bi_id",
      type: "string",
      persist: false,
    },
  ],
});
