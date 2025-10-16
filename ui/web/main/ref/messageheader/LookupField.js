//---------------------------------------------------------------------
// NOC.main.check.Lookup
//---------------------------------------------------------------------
// Copyright (C) 2007-2012 The NOC Project
// See LICENSE for details
//---------------------------------------------------------------------
console.debug("Defining NOC.main.messageheader.LookupField");

Ext.define("NOC.main.ref.messageheader.LookupField", {
  extend: "NOC.core.ComboBox",
  alias: "widget.main.ref.messageheader.LookupField",
  uiStyle: "medium-combo",
  askPermission: false,
});
