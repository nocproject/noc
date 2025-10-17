//---------------------------------------------------------------------
// NOC.core.State
//---------------------------------------------------------------------
// Copyright (C) 2007-2017 The NOC Project
// See LICENSE for details
//---------------------------------------------------------------------
console.debug("Defining NOC.core.StateModel");
Ext.define("NOC.core.StateModel", {
  extend: "Ext.data.Model",
  fields: [
    {name: "id", type: "string"},
    {name: "label", type: "string"},
    {name: "description", type: "string"},
    {name: "to_state", type: "string"},
    {name: "to_state__label", type: "string"},
  ],
});
