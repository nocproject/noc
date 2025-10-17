//---------------------------------------------------------------------
// NOC.main.check.Lookup
//---------------------------------------------------------------------
// Copyright (C) 2007-2012 The NOC Project
// See LICENSE for details
//---------------------------------------------------------------------
console.debug("Defining NOC.main.messagetype.LookupField");

Ext.define("NOC.main.ref.messagetype.LookupField", {
  extend: "NOC.core.ComboBox",
  alias: "widget.main.ref.messagetype.LookupField",
  uiStyle: "medium-combo",
  askPermission: false,
});
