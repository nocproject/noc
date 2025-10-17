//---------------------------------------------------------------------
// inv.sensor DataModel
//---------------------------------------------------------------------
// Copyright (C) 2007-2013 The NOC Project
// See LICENSE for details
//---------------------------------------------------------------------
console.debug("Defining NOC.inv.inv.plugins.sensor.SensorModel");

Ext.define("NOC.inv.inv.plugins.sensor.SensorModel", {
  extend: "Ext.data.Model",
  fields: [
    {
      name: "local_id",
      type: "string",
    },
    {
      name: "profile",
      type: "auto",
    },
    {
      name: "units",
      type: "auto",
    },
    {
      name: "object",
      type: "string",
    },
    {
      name: "state",
      type: "auto",
    },
    {
      name: "modbus_register",
      type: "string",
    },
    {
      name: "modbus_format",
      type: "string",
    },
    {
      name: "protocol",
      type: "string",
    },
    {
      name: "snmp_oid",
      type: "string",
    },
  ],
});
