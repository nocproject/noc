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
          var grid = field.up("panel").down("gridpanel"),
            store = grid.getStore(),
            trigger = field.getTrigger("clear");
          if(newValue){
            store.filter({
              property: "name",
              value: newValue,
              anyMatch: true,
              caseSensitive: false,
            });
            trigger.show();
          } else{
            store.clearFilter();
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
      style: {
        paddingRight: "20px",
      },
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
      stateId: "inv.inv-job-grid",
      emptyText: __("No jobs"),
      store: {
        model: "NOC.inv.inv.plugins.job.JobModel",
        data: [],
      },
      features: [{
        ftype: "grouping",
      }],
      scrollable: "y",
      columns: [
        {
          xtype: "glyphactioncolumn",
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
  //
  initComponent: function(){
    this.callParent();
    let store = this.down("grid").getStore();
    store.on("datachanged", this.getController().onDataChanged, this);
  },
  //
  preview: function(data, objectId){
    var me = this,
      vm = me.getViewModel(),
      records = data.data || [],
      maskComponent = me.up("[appId=inv.inv]").maskComponent,
      messageId = maskComponent.show("processing", "jobs"),
      store = this.down("grid").getStore();
    vm.set("currentId", objectId);
    if(!Ext.isEmpty(store)){
      store.removeAll();
      store.loadData(records);
    }
    maskComponent.hide(messageId);
  },
});