//---------------------------------------------------------------------
// core.ObservableModel
//---------------------------------------------------------------------
// Copyright (C) 2007-2021 The NOC Project
// See LICENSE for details
//---------------------------------------------------------------------
console.debug("Defining NOC.core.ObservableModel");

Ext.define("NOC.core.ObservableModel", {
  extend: "Ext.data.Model",
  idProperty: "key",
  fields: [
    {name: "key", type: "string"},
    {name: "value"},
  ],
});
