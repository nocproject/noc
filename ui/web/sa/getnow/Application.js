//---------------------------------------------------------------------
// Copyright (C) 2007-2017 The NOC Project
// See LICENSE for details
//---------------------------------------------------------------------

console.debug("Defining NOC.sa.getnow.Application");
Ext.define("NOC.sa.getnow.Application", {
  extend: "NOC.core.Application",
  requires: [
    "NOC.core.filter.Filter",
    "NOC.core.MonacoPanel",
    "NOC.sa.getnow.Controller",
    "NOC.sa.getnow.SelectionGrid",
    "NOC.sa.getnow.ViewModel",
  ],

  alias: "widget.getnow",

  layout: "border",
  controller: "getnow",
  viewModel: "getnow",
  border: false,
  stateful: true,
  stateId: "getnow.appPanel",

  items: [
    {
      xtype: "selectionGrid",
      region: "west",
      resizable: true,
      split: true,
      width: "35%",
    },
    {
      // xclass: "NOC.core.MonacoPanel",
      xtype: "core.monacopanel",
      defaultListenerScope: false,
      region: "center",
      width: "65%",
      app: this,
      reference: "repoPreview",
      previewName: "{0} config",
      restUrl: "/sa/managedobject/{0}/repo/cfg/",
      historyHashPrefix: "config",
      listeners: {
        destroy: "onStopPolling",
      },
      tbar: [
        {
          text: __("Get config NOW"),
          tooltip: __("Get config NOW"),
          bind: {
            disabled: "{!selectionGrid.selection}",
          },
          handler: "onGetConfig",
        },
        {
          text: __("Stop Polling"),
          tooltip: __("Stop Polling"),
          bind: {
            disabled: "{!isStarted}",
          },
          handler: "onStopPolling",
        },
        "->",
        {
          xtype: "box",
          bind: {
            html: '<span style="text-align: center;" class="noc-badge {polling.style}">{polling.leave}</span>',
          },
        },
      ],
    },
    {
      xtype: "NOC.Filter",
      // appId: this.appId,
      appId: "sa.getnow",
      reference: "filterPanel",
      region: "east",
      width: 300,
      collapsed: true,
      border: true,
      animCollapse: false,
      collapseMode: "mini",
      hideCollapseTool: true,
      split: true,
      resizable: true,
      stateful: true,
      stateId: "getnow.filterPanel",
      selectionStore: "getnow.objectsStore",
      treeAlign: "right",
      listeners: {
        collapse: "onCollapseFilter",
        expand: "onExpandFilter",
      },
    },
  ],
});