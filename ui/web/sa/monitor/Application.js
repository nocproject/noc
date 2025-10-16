//---------------------------------------------------------------------
// Copyright (C) 2007-2017 The NOC Project
// See LICENSE for details
//---------------------------------------------------------------------

console.debug("Defining NOC.sa.monitor.Application");
Ext.define("NOC.sa.monitor.Application", {
  extend: "NOC.core.Application",
  requires: [
    "NOC.sa.monitor.Controller",
    "NOC.sa.monitor.ViewModel",
    "NOC.sa.monitor.SelectionGrid",
    "NOC.sa.monitor.Filter",
    "NOC.sa.monitor.JobLogPanel",
  ],

  alias: "widget.monitor",

  layout: "border",
  controller: "monitor",
  viewModel: "monitor",
  border: false,
  stateful: true,
  stateId: "monitor.appPanel",

  defaults: {
    resizable: true,
    animCollapse: false,
    collapseMode: "mini",
    hideCollapseTool: true,
    collapsed: true,
    border: false,
    split: true,
    stateful: true,
  },
  items: [
    {
      xtype: "sa.selectionGrid",
      reference: "grid",
      region: "center",
      collapsed: false,
      split: true,
    },
    {
      xtype: "monitor.Filter",
      appId: "sa.monitor",
      reference: "filterPanel",
      region: "east",
      width: 300,
      stateId: "monitor.filterPanel",
      selectionStore: "monitor.objectsStore",
      treeAlign: "right",
    },
    {
      xtype: "monitor.JobLogPanel",
      region: "south",
      reference: "logPanel",
      collapsed: true,
      title: __("Discovery Job Log"),
      height: "50%",
    },
  ],
  listeners: {
    destroy: "stopPolling",
  },
});
