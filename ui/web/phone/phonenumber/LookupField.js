//---------------------------------------------------------------------
// NOC.phone.phonenumber.Lookup
//---------------------------------------------------------------------
// Copyright (C) 2007-2016 The NOC Project
// See LICENSE for details
//---------------------------------------------------------------------
console.debug("Defining NOC.phone.phonenumber.LookupField");

Ext.define("NOC.phone.phonenumber.LookupField", {
  extend: "NOC.core.ComboBox",
  alias: "widget.phone.phonenumber.LookupField",
  listConfig: {
    getInnerTpl: function(){
      return "{label} <span style='float: right' class='x-display-tag'>{dialplan}</span>";
    },
  },
  uiStyle: "medium-combo",
});
