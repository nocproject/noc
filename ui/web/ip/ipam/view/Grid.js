//---------------------------------------------------------------------
// ip.ipam  application
//---------------------------------------------------------------------
// Copyright (C) 2007-2018 The NOC Project
// See LICENSE for details
//---------------------------------------------------------------------
console.debug("Defining NOC.ip.ipam.view.Grid");

Ext.define("NOC.ip.ipam.view.Grid", {
  extend: "Ext.grid.Panel",
  alias: "widget.ip.ipam.grid",
  controller: "ip.ipam.GridController",
  requires: [
    "Ext.grid.feature.Grouping",
    "NOC.ip.ipam.view.GridController",
    "NOC.ip.ipam.store.VRF",
  ],
  store: {
    type: "ip.ipam",
  },
  features: [{
    ftype: "grouping",
    collapsible: true,
    // groupHeaderTpl: '{columnName}: <tpl if="{name">|{name}|{name.length}|<tpl else>"Ungrouped"</tpl>',
  }],
  columns: [
    {
      xtype: "glyphactioncolumn",
      width: 60,
      sortable: false,
      stateId: "rowaction",
      items: [
        {
          glyph: NOC.glyph.star,
          tooltip: __("Mark/Unmark"),
          getColor: function(cls, meta, r){
            return r.get("fav_status") ? NOC.colors.starred : NOC.colors.unstarred;
          },
          handler: "onFavItem",
        },
        {
          glyph: NOC.glyph.edit,
          color: NOC.colors.edit,
          tooltip: __("Edit"),
          handler: "onEditItem",
        },
        {
          glyph: NOC.glyph.id_card_o,
          color: NOC.colors.edit,
          tooltip: __("Open card"),
          handler: "onOpenCard",
        },
      ],
    },
    {
      text: __("Name"),
      dataIndex: "name",
    },
    {
      text: __("State"),
      dataIndex: "state",
      renderer: NOC.render.Lookup("state"),
    },
    {
      text: __("Group"),
      dataIndex: "vrf_group",
      renderer: NOC.render.Lookup("vrf_group"),
    },
    {
      text: __("Profile"),
      dataIndex: "profile",
      renderer: NOC.render.Lookup("profile"),
    },
    {
      text: __("Project"),
      dataIndex: "project",
      renderer: NOC.render.Lookup("project"),
    },
    {
      text: __("RD"),
      dataIndex: "rd",
      width: 100,
    },
    {
      text: __("VPN ID"),
      dataIndex: "vpn_id",
      width: 100,
    },
    {
      xtype: "actioncolumn",
      text: __("IPv4"),
      items: [{
        tooltip: __("To see the prefix contents"),
        getClass: function(v, _, record){
          return "x-fa fa-" + (record.get("afi_ipv4") ? "eye pointer-cursor" : "times default-cursor");
        },
        handler: "onViewRootPrefix4",
      }],
      width: 50,
    },
    {
      xtype: "actioncolumn",
      text: __("IPv6"),
      items: [{
        tooltip: __("To see the prefix contents"),
        getTip: function(value, metadata, record){
          return record.get("afi_ipv6") ? __("View Detail") : "";
        },
        getClass: function(v, _, record){
          return "x-fa fa-" + (record.get("afi_ipv6") ? "eye pointer-cursor" : "times default-cursor");
        },
        handler: "onViewRootPrefix6",
      }],
      width: 50,
    },
    {
      text: __("Description"),
      dataIndex: "description",
      flex: 1,
    },
    {
      text: __("Labels"),
      dataIndex: "labels",
      renderer: NOC.render.LabelField,
    },
  ],
  viewConfig: {
    enableTextSelection: true,
    getRowClass: function(record){
      var c = record.get("row_class");
      if(c){
        return c;
      } else{
        return "";
      }
    },
  },
});
