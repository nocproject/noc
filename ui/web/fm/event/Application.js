//---------------------------------------------------------------------
// fm.event application
//---------------------------------------------------------------------
// Copyright (C) 2007-2025 The NOC Project
// See LICENSE for details
//---------------------------------------------------------------------
console.debug("Defining NOC.fm.event.Application");

Ext.define("NOC.fm.event.Application", {
  extend: "NOC.core.Application",
  requires: [
    "NOC.core.ComboBox",
    "NOC.core.combotree.ComboTree",
    "NOC.core.JSONPreview",
    "NOC.core.ModelStore",
    "NOC.sa.managedobject.LookupField",
    "NOC.inv.resourcegroup.Model",
    "NOC.sa.administrativedomain.LookupField",
    "NOC.fm.eventclass.LookupField",
    "NOC.fm.event.ApplicationModel",
    "NOC.fm.event.ApplicationController",
    "NOC.fm.event.EventFilter",
    "NOC.fm.event.EventInspector",
  ],
  layout: "card",
  controller: "fm.event",
  viewModel: {
    type: "fm.event",
  },
  //
  initComponent: function(){
    var me = this,
      bs = Math.max(50, Math.ceil(screen.height / 24) + 10);

    me.store = Ext.create("NOC.core.ModelStore", {
      model: "NOC.fm.event.Model",
      autoLoad: false,
      customFields: [],
      pageSize: bs,
      leadingBufferZone: bs,
      numFromEdge: bs,
      trailingBufferZone: bs,
      sorters: [
        {
          property: "timestamp",
          direction: "DESC",
        },
      ],
    });

    me.store.on("load", function(store){
      me.getViewModel().set("total", store.getTotalCount());
    });
    me.gridPanel = Ext.create("Ext.grid.Panel", {
      region: "center",
      split: true,
      store: me.store,
      border: false,
      itemId: "fm-event-grid",
      stateful: true,
      stateId: "fm.event-grid",
      allowDeselect: true,
      columns: [
        {
          text: __("ID"),
          dataIndex: "id",
          width: 150,
        },
        {
          text: __("Time"),
          dataIndex: "timestamp",
          width: 100,
          renderer: NOC.render.DateTime,
        },
        {
          text: __("Administrative Domain"),
          dataIndex: "administrative_domain",
          width: 200,
          renderer: NOC.render.Lookup("administrative_domain"),
        },
        {
          text: __("Object"),
          dataIndex: "managed_object",
          width: 200,
          renderer: NOC.render.Lookup("managed_object"),
        },
        {
          text: __("Class"),
          dataIndex: "event_class",
          width: 300,
          renderer: NOC.render.Lookup("event_class"),
        },
        {
          text: __("Subject"),
          dataIndex: "subject",
          flex: 1,
        },
        {
          text: __("Alarm"),
          dataIndex: "alarms",
          width: 30,
          align: "right",
        },
        {
          text: __("Rep."),
          dataIndex: "repeats",
          width: 30,
          align: "right",
        },
        {
          text: __("Dur."),
          dataIndex: "duration",
          width: 70,
          align: "right",
          renderer: NOC.render.Duration,
        },
      ],
      viewConfig: {
        enableTextSelection: true,
        getRowClass: Ext.bind(me.getRowClass, me),
      },
      listeners: {
        select: "expandInspector",
        deselect: "collapseInspector",
      },
    });

    me.filterPanel = Ext.create("NOC.fm.event.EventFilter", {
      itemId: "filterPanel",
    });

    me.inspectorPanel = Ext.create("NOC.fm.event.EventInspector", {
      itemId: "inspectorPanel",
    });

    me.eastContainer = Ext.create("Ext.panel.Panel", {
      region: "east",
      width: "20%",
      layout: "card",
      header: false,
      collapseMode: "mini",
      collapsible: true,
      split: true,
      collapsed: true,
      hideCollapseTool: true,
      animCollapse: false,
      items: [
        me.filterPanel,
        me.inspectorPanel,
      ],
    });

    me.mainPanel = Ext.create("Ext.panel.Panel", {
      layout: "border",
      itemId: "fm-event-main",
      tbar: [
        {
          glyph: NOC.glyph.refresh,
          handler: "onRefresh",
        },
        {
          text: __("Filtering List"),
          glyph: NOC.glyph.filter,
          tooltip: __("Show/Hide Filter"),
          style: {
            pointerEvents: "all",
          },
          handler: "toggleFilter",
        },
        "->",
        {
          xtype: "tbtext",
          bind: {
            html: "{eventsTotal}",
          },
        },
      ],
      items: [
        me.gridPanel,
        me.eastContainer,
      ],
    });
    //
    me.jsonPanel = Ext.create("NOC.core.JSONPreview", {
      app: me,
      restUrl: new Ext.XTemplate("/fm/event/{id}/json/"),
      previewName: new Ext.XTemplate("Event: {id}"),
    });
    me.ITEM_GRID = me.registerItem(me.mainPanel);
    me.ITEM_JSON = me.registerItem(me.jsonPanel);
    Ext.apply(me, {
      items: me.getRegisteredItems(),
    });
    me.callParent();
  },
  // Return Grid's row classes
  getRowClass: function(record){
    var c = record.get("row_class");
    if(c){
      return c;
    } else{
      return "";
    }
  },
  //
  showGrid: function(){
    this.showItem(this.ITEM_GRID);
    this.setHistoryHash();
  },
  showForm: function(){
    this.showGrid();
  },
});
