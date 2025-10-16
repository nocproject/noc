//---------------------------------------------------------------------
// NOC.inv.networksegment.TreeCombo
//---------------------------------------------------------------------
// Copyright (C) 2007-2018 The NOC Project
// See LICENSE for details
//---------------------------------------------------------------------
console.debug("Defining NOC.inv.networksegment.TreeCombo");

Ext.define("NOC.inv.networksegment.ComboTree", {
  extend: "NOC.core.combotree.ComboTree",
  alias: "widget.inv.networksegment.ComboTree",
  restUrl: "/inv/networksegment/",
});
