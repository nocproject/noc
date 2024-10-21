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
    "NOC.inv.inv.plugins.job.JobController",
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
        filters: [
          {
            property: "name",
            value: "{searchText}",
            anyMatch: true,
            caseSensitive: false,
          },
        ],
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
    {
      xtype: "textfield",
      itemId: "searchText",
      emptyText: __("Search..."),
      width: 400,
      bind: {
        value: "{searchText}",
      },
      listeners: {
        change: function(field, newValue){
          var trigger = field.getTrigger("clear");
          if(newValue){
            trigger.show();
          } else{
            trigger.hide();
          }
        },
      },
      triggers: {
        clear: {
          cls: "x-form-clear-trigger",
          hidden: true,
          handler: function(field){
            field.setValue("");
            var grid = field.up("panel").down("gridpanel"),
              store = grid.getStore();
            store.clearFilter();
            field.getTrigger("clear").hide();
          },
        },
      },
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
          flex: 1,
        },
        {
          text: __("Description"),
          dataIndex: "description",
          flex: 2,
        },
        {
          text: __("Created At"),
          dataIndex: "created_at",
          width: 175,
          renderer: NOC.render.DateTime,
        },
        {
          text: __("Completed At"),
          dataIndex: "completed_at",
          width: 175,
          renderer: NOC.render.DateTime,
        },
        {
          text: __("Status"),
          dataIndex: "status",
          width: 135,
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
      vm = me.getViewModel(),
      records = data.data || [],
      maskComponent = me.up("[appId=inv.inv]").maskComponent,
      messageId = maskComponent.show("processing", "jobs");
    vm.set("currentId", objectId);
    vm.get("gridStore").loadData(records);
    maskComponent.hide(messageId);
  },
});