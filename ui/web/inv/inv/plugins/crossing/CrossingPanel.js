//---------------------------------------------------------------------
// inv.inv CrossingPanel
//---------------------------------------------------------------------
// Copyright (C) 2007-2014 The NOC Project
// See LICENSE for details
//---------------------------------------------------------------------
console.debug("Defining NOC.inv.inv.plugins.crossing.CrossingPanel");

Ext.define("NOC.inv.inv.plugins.crossing.CrossingPanel", {
  extend: "NOC.inv.inv.plugins.SchemePluginAbstract",
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
});
