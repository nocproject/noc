//---------------------------------------------------------------------
// inv.inv OPM Controller
//---------------------------------------------------------------------
// Copyright (C) 2007-2025 The NOC Project
// See LICENSE for details
//---------------------------------------------------------------------
console.debug("Defining NOC.inv.inv.plugins.opm.OPMController");

Ext.define("NOC.inv.inv.plugins.opm.OPMController", {
  extend: "Ext.app.ViewController",
  alias: "controller.opm",
  
  collapseSettings: function(){
    this.lookupReference("opmRightPanel").toggleCollapse();
  },
});