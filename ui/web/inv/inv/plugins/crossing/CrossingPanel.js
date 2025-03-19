//---------------------------------------------------------------------
// inv.inv CrossingPanel
//---------------------------------------------------------------------
// Copyright (C) 2007-2014 The NOC Project
// See LICENSE for details
//---------------------------------------------------------------------
console.debug("Defining NOC.inv.inv.plugins.crossing.CrossingPanel");

Ext.define("NOC.inv.inv.plugins.crossing.CrossingPanel", {
  extend: "NOC.inv.inv.plugins.VizSchemePluginAbstract",
  title: __("Crossing"),
  itemId: "crossingPanel",
  viewModel: {
    data: {
      showDetails: false,
    },
  },
  gridColumns: [
    {
      dataIndex: "input",
      text: __("Input"),
      width: 150,
    },
    {
      dataIndex: "input_discriminator",
      text: __("Input Discriminator"),
      flex: 1,
    },
    {
      dataIndex: "output",
      text: __("Output"),
      width: 150,
    },
    {
      dataIndex: "output_discriminator",
      text: __("Output Discriminator"),
      flex: 1,
    },
    {
      dataIndex: "gain_db",
      text: __("Gain (dB)"),
      width: 75,
    },
  ],
  initComponent: function(){
    var grid = this.items[0];
    //
    grid.stateful = true; 
    grid.stateId = "inv.inv-crossing-grid";
    grid.itemId = "invCrossingGrid";
    grid.columns = this.gridColumns;
    this.callParent(arguments);
  },
});
