//---------------------------------------------------------------------
// sa.discoveredobject application
//---------------------------------------------------------------------
// Copyright (C) 2007-2020 The NOC Project
// See LICENSE for details
//---------------------------------------------------------------------
console.debug("Defining NOC.sa.discoveredobject.view.Grid");

Ext.define("NOC.sa.discoveredobject.view.Grid", {
  extend: "Ext.grid.Panel",
  controller: "sa.discoveredobject.grid",
  alias: "widget.sa.discoveredobject.grid",
  requires: [
    "NOC.sa.discoveredobject.ApplicationController",
    "NOC.sa.discoveredobject.controller.Grid",
    "NOC.sa.discoveredobject.store.DiscoveredObject",
    // "Ext.ux.grid.column.GlyphAction"
  ],
  stateful: true,
  store: {
    type: "sa.discoveredobject",
  },
  bind: {
    selection: "{selectedRow}",
  },
  selModel: {
    mode: "MULTI",
    type: "checkboxmodel",
  },
  columns: [
    {
      text: __("ID"),
      dataIndex: "id",
      hidden: true,
    },
    {
      text: __("Address"),
      dataIndex: "address",
    },
    {
      text: __("Pool"),
      dataIndex: "pool",
      width: 70,
      renderer: NOC.render.Lookup("pool"),
    },
    {
        text: __("Is Dirty"),
        dataIndex: "is_dirty",
        width: 50,
        renderer: NOC.render.Bool,
        sortable: false
    },
    {
        text: __("Is Synced"),
        dataIndex: "is_synced",
        width: 50,
        renderer: NOC.render.Bool,
        sortable: false
    },
    {
      text: __("Hostname"),
      dataIndex: "hostname",
      renderer: function(v){
        return v || "N/A";
      },
    },
    {
      text: __("State"),
      dataIndex: "state",
      width: 200,
      renderer: NOC.render.Lookup("state"),
    },
    {
      text: __("Rule"),
      dataIndex: "rule",
      width: 100,
      renderer: NOC.render.Lookup("rule"),
    },
    {
      text: __("Checks"),
      dataIndex: "checks",
      width: 250,
      renderer: "checksRenderer",
    },
    {
      text: __("Labels"),
      dataIndex: "effective_labels",
      editor: "labelfield",
      width: 200,
      renderer: NOC.render.LabelField,
    },
  ],
  listeners: {
    afterrender: "afterrenderHandler",
    selectionchange: "onGridStoreSizeChange",
  },
  dockedItems: [{
    tbar: {
      items: [
        { // @todo: Search
          glyph: NOC.glyph.refresh,
          tooltip: __("Refresh data"),
          style: {
            pointerEvents: "all",
          },
          handler: "onGridRefresh",
        },
        {
          xtype: "combo",
          editable: false,
          minWidth: 225,
          emptyText: __("Group select"),
          store: {
            fields: ["cmd", "title"],
            data: [
              {"cmd": "SCREEN", "title": __("All devices on screen")},
              {"cmd": "FIRST_50", "title": __("First 50")},
              {"cmd": "FIRST_100", "title": __("First 100")},
              {"cmd": "N_ROWS", "title": __("First N")},
              {"cmd": "PERIOD", "title": __("Period start,qty")},
            ],
          },
          queryMode: "local",
          displayField: "title",
          valueField: "cmd",
          listeners: {
            select: "onSelectAll",
          },
        },
        {
          text: __("Unselect All"),
          glyph: NOC.glyph.minus_circle,
          tooltip: __("Unselect all devices"),
          style: {
            pointerEvents: "all",
          },
          bind: {
            disabled: "{!gridHasSelection}",
          },
          handler: "onUnselectAll",
        },
        "->",
        {
          xtype: "box",
          bind: {
            html: "<span class='x-btn-inner x-btn-inner-default-toolbar-small'>" + __("Selected : {total.selected}") + "</span",
          },
        },
        "|",
        {
          xtype: "box",
          bind: {
            html: "<span class='x-btn-inner x-btn-inner-default-toolbar-small'>" + __("Total : {total.all}") + "</span>",
          },
        }],
    },
  }],
  viewConfig: {
    enableTextSelection: true,
  },
});
