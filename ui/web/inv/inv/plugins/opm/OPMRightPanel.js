//---------------------------------------------------------------------
// inv.inv OPM Right Panel
//---------------------------------------------------------------------
// Copyright (C) 2007-2025 The NOC Project
// See LICENSE for details
//---------------------------------------------------------------------
console.debug("Defining NOC.inv.inv.plugins.opm.OPMRightPanel");

Ext.define("NOC.inv.inv.plugins.opm.OPMRightPanel", {
  extend: "Ext.panel.Panel",
  title: __("Settings"),
  xtype: "opm.rightPanel",  
  border: true,
  hideMode: "offsets",
});