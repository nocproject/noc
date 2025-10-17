//---------------------------------------------------------------------
// sa.managedobject Model
//---------------------------------------------------------------------
// Copyright (C) 2007-2023 The NOC Project
// See LICENSE for details
//---------------------------------------------------------------------

console.debug("Defining NOC.sa.managedobject.ApplicationModel");
Ext.define("NOC.sa.managedobject.ApplicationModel", {
  extend: "Ext.data.Model",
  rest_url: "/sa/managedobject/list/",
  actionMethods: {
    read: "POST",
  },

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
      name: "address",
      type: "string",
    },
    {
      name: "profile",
      type: "string",
    },
    {
      name: "platform",
      type: "string",
    },
    {
      name: "version",
      type: "string",
    },
    {
      name: "oper_status",
      type: "string",
    },
    {
      name: "is_managed",
      type: "boolean",
      persist: false,
    },
    {
      name: "object_profile",
      type: "string",
    },
    {
      name: "administrative_domain",
      type: "string",
    },
    {
      name: "auth_profile",
      type: "string",
    },
    {
      name: "vrf",
      type: "string",
    },
    {
      name: "pool",
      type: "string",
    },
    {
      name: "description",
      type: "string",
    },
    {
      name: "interface_count",
      type: "int",
    },
    {
      name: "link_count",
      type: "int",
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
    {
      name: "state",
      type: "string",
    },
    {
      name: "status",
      defaultValue: "w",
      persist: false,
    },
    {
      name: "result",
      persist: false,
    },
  ],
});
