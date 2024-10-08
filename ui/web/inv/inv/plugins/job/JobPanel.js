//---------------------------------------------------------------------
// inv.inv Job Panel
//---------------------------------------------------------------------
// Copyright (C) 2007-2024 The NOC Project
// See LICENSE for details
//---------------------------------------------------------------------
console.debug("Defining NOC.inv.inv.plugins.job.JobPanel");

Ext.define("NOC.inv.inv.plugins.job.JobPanel", {
  extend: "Ext.panel.Panel",
  requires: [
    "NOC.inv.inv.plugins.job.JobModel",
    "NOC.inv.inv.plugins.job.Controller",
  ],
  title: __("Jobs"),
  closable: false,
  layout: "fit",
  controller: "job",
  viewModel: {
    stores: {
      gridStore: {
        model: "NOC.inv.inv.plugins.job.JobModel",
        listeners: {
          datachanged: "onDataChanged",
        },
      },
    },
    data: {
      searchText: "",
      totalCount: 0,
      currentId: undefined,
    },
  },
  tbar: [
    {
      glyph: NOC.glyph.refresh,
      tooltip: __("Reload"),
      handler: "onReload",
    },
    "->",
    {
      xtype: "tbtext",
      bind: {
        html: __("Total") + ": {totalCount}",
      },
    },
  ],
  items: [
    {
      xtype: "gridpanel",
      border: false,
      stateful: true,
      emptyText: __("No jobs"),
      bind: {
        store: "{gridStore}",
      },
      features: [{
        ftype: "grouping",
      }],
      scrollable: "y",
      columns: [
        {
          xtype: 'glyphactioncolumn',
          width: 25,
          items: [
            {
              glyph: NOC.glyph.eye,
              tooltip: __("View"),
              handler: "onViewJob",
            },
          ],

        },
        {
          text: __("Name"),
          dataIndex: "name",
        },
        {
          text: __("Description"),
          dataIndex: "description",
        },
        {
          text: __("Created At"),
          dataIndex: "created_at",
          renderer: NOC.render.DateTime,
        },
        {
          text: __("Completed At"),
          dataIndex: "completed_at",
          renderer: NOC.render.DateTime,
        },
        {
          text: __("Status"),
          dataIndex: "status",
          renderer: NOC.render.JobStatus,
        },
      ],
      listeners: {
        rowdblclick: "onRowDblClick",
        activate: "onActivateGrid",
      },
    },
  ],
  preview: function(data, objectId){
    var me = this,
      vm = me.getViewModel();
    vm.set("currentId", objectId);
    vm.get("gridStore").loadData(data.data);
  },
});