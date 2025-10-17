//---------------------------------------------------------------------
// ip.ipam.prefix form
//---------------------------------------------------------------------
// Copyright (C) 2007-2019 The NOC Project
// See LICENSE for details
//---------------------------------------------------------------------
console.debug("Defining NOC.ip.ipam.view.forms.prefix.Prefix");

Ext.define("NOC.ip.ipam.view.forms.prefix.Prefix", {
  extend: "Ext.panel.Panel",
  alias: "widget.ip.ipam.prefix.contents",
  controller: "ip.ipam.prefix.contents",
  viewModel: "ip.ipam.prefix.contents",
  requires: [
    "Ext.layout.container.Border",
    "Ext.layout.container.Accordion",
    "NOC.ip.ipam.view.forms.Info",
    "NOC.ip.ipam.view.forms.prefix.PrefixController",
    "NOC.ip.ipam.view.forms.prefix.PrefixModel",
    "NOC.ip.ipam.view.forms.prefix.PrefixAddressLists",
  ],
  layout: "border",
  minWidth: 700,
  scrollable: true,
  items: [
    {
      region: "center",
      xtype: "ip.ipam.list.prefixAddress",
      listeners: {
        ipIPAMPrefixFormNew: "onAppendPrefix",
      },
    },
    {
      region: "east",
      xtype: "ip.ipam.info",
      width: "15%",
      split: true,
      title: __("Info"),
      bind: {
        data: "{prefix}",
      },
    },
  ],
  tbar: [
    {
      text: __("Close"),
      tooltip: __("Close without saving"),
      glyph: NOC.glyph.arrow_left,
      handler: "onClose",
    },
    "-",
    {
      text: __("Add Address"),
      tooltip: __("Add Address"),
      glyph: NOC.glyph.plus,
      handler: "onAddAddress",
      bind: {
        disabled: "{!prefix.permissions.add_address}",
      },
    },
    "-",
    {
      text: __("Add Prefix"),
      tooltip: __("Add Prefix"),
      glyph: NOC.glyph.plus,
      handler: "onAddPrefix",
      bind: {
        disabled: "{!prefix.permissions.add_prefix}",
      },
    },
    {
      text: __("Delete Prefix"),
      tooltip: __("Delete Prefix"),
      glyph: NOC.glyph.trash,
      handler: "onDeletePrefix",
      bind: {
        disabled: "{!prefix.permissions.delete_prefix}",
      },
    },
    {
      text: __("Edit Prefix"),
      tooltip: __("Edit Prefix"),
      glyph: NOC.glyph.wrench,
      handler: "onEditPrefix",
      bind: {
        disabled: "{!prefix.permissions.change}",
      },
    },
    {
      text: __("Tools"),
      tooltip: __("Open tools"),
      glyph: NOC.glyph.edit,
      handler: "onTools",
    },
  ],
});
