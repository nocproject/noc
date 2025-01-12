//---------------------------------------------------------------------
// inv.inv OPM Diagram
//---------------------------------------------------------------------
// Copyright (C) 2007-2025 The NOC Project
// See LICENSE for details
//---------------------------------------------------------------------
console.debug("Defining NOC.inv.inv.plugins.opm.OPMDiagram");

Ext.define("NOC.inv.inv.plugins.opm.OPMDiagram", {
  extend: "Ext.draw.Container",
  xtype: "opm.diagram",
  //   title: __("OPM Diagram"),
  sprites: [{
    type: "circle",
    fillStyle: "#79BB3F",
    r: 100,
    x: 100,
    y: 100,
  }],
});