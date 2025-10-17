//---------------------------------------------------------------------
// Copyright (C) 2007-2017 The NOC Project
// See LICENSE for details
//---------------------------------------------------------------------

console.debug("Defining NOC.sa.getnow.SelectionGrid");
Ext.define("NOC.sa.getnow.SelectionGrid", {
  extend: "Ext.grid.Panel",
  alias: "widget.selectionGrid",

  bind: {
    store: "{objectsStore}",
  },
  reference: "selectionGrid",
  border: 1,
  emptyText: __("Not Found"),
  stateful: true,
  stateId: "getnow.selectionGrid",
  selModel: {
    mode: "MULTI",
    selType: "checkboxmodel",
  },
  columns: [
    {
      text: __("ID"),
      tooltip: __("ID"),
      hidden: true,
      dataIndex: "id",
      width: 60,
    },
    {
      dataIndex: "name",
      text: __("Managed object"),
      tooltip: __("Managed object"),
      width: 120,
      renderer: "onRenderTooltip",
    },
    {
      dataIndex: "profile_name",
      text: __("SA Profile"),
      tooltip: __("SA Profile"),
      width: 60,
      renderer: "onRenderTooltip",
    },
    {
      dataIndex: "last_success",
      text: __("Last success"),
      tooltip: __("Last success"),
      width: 40,
      renderer: "onRenderTooltip",
      sortable: false,
    },
    {
      dataIndex: "last_update",
      text: __("Last update"),
      tooltip: __("Last update"),
      width: 40,
      renderer: "onRenderTooltip",
      sortable: false,
    },
    {
      dataIndex: "status",
      text: __("Status"),
      tooltip: __("Status"),
      width: 50,
      sortable: false,
      renderer: "onRenderStatus",
    },
    {
      dataIndex: "last_status",
      text: __("Last status"),
      tooltip: __("Last status"),
      width: 50,
      sortable: false,
      renderer: "onRenderStatus",
    },
  ],
  viewConfig: {
    enableTextSelection: true,
    getRowClass: function(record){
      return record.get("status") === "R" ? "noc-status-running" : "";
    },
  },
  tbar: [
    {
      glyph: NOC.glyph.refresh,
      tooltip: __("Reload data"),
      handler: "onReload",
    },
    {
      text: __("Select All"),
      glyph: NOC.glyph.plus_circle,
      tooltip: __("Select all records from buffer (screen)"),
      handler: "onSelectAll",
    },
    {
      text: __("Unselect All"),
      glyph: NOC.glyph.minus_circle,
      bind: {
        disabled: "{!selectionGrid.selection}",
      },
      tooltip: __("Unselect All"),
      handler: "onUnselectAll",
    },
    {
      text: __("Filter"),
      glyph: NOC.glyph.filter,
      tooltip: __("Show/Hide Filter"),
      bind: {
        pressed: "{isFilterOpen}",
      },
      handler: "onShowFilter",
    },
    {
      text: __("Export"),
      glyph: NOC.glyph.arrow_down,
      tooltip: __("Export all records from buffer (screen)"),
      handler: "onExport",
    },
    "->",
    {
      xtype: "box",
      bind: {
        html: __("Selected") + ": {total.selection}",
      },
    },
  ],
  listeners: {
    selectionchange: "onSelectionChange",
    rowdblclick: "onRowDblClick",
  },
});