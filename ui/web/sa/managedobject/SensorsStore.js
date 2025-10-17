//---------------------------------------------------------------------
// sa.managedobject Sensors Store
//---------------------------------------------------------------------
// Copyright (C) 2007-2021 The NOC Project
// See LICENSE for details
//---------------------------------------------------------------------
console.debug("Defining NOC.sa.managedobject.SensorsStore");

Ext.define("NOC.sa.managedobject.SensorsStore", {
  extend: "Ext.data.Store",
  model: null,
  fields: [
    {
      name: "id",
      type: "auto",
    },
    {
      name: "ipmi_id",
      type: "auto",
    },
    {
      name: "label",
      type: "string",
    },
    {
      name: "labels",
      type: "auto",
    },
    {
      name: "effective_labels",
      type: "auto",
    },
    {
      name: "last_seen",
      type: "date",
    },
    {
      name: "local_id",
      type: "auto",
    },
    {
      name: "managed_object",
      type: "auto",
    },
    {
      name: "modbus_register",
      type: "auto",
    },
    {
      name: "object",
      type: "auto",
    },
    {
      name: "object__label",
      type: "string",
    },
    {
      name: "profile",
      type: "auto",
    },
    {
      name: "profile__label",
      type: "string",
    },
    {
      name: "protocol",
      type: "string",
    },
    {
      name: "row_class",
      type: "string",
      persist: false,

    },
    {
      name: "snmp_oid",
      type: "string",
    },
    {
      name: "state",
      type: "auto",
    },
    {
      name: "state__label",
      type: "string",
    },
    {
      name: "units",
      type: "auto",
    },
    {
      name: "units__label",
      type: "string",
    },
  ],
  data: [],
});
