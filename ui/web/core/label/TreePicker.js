//---------------------------------------------------------------------
// core.label.treepicker widget
//---------------------------------------------------------------------
// Copyright (C) 2007-2021 The NOC Project
// See LICENSE for details
//---------------------------------------------------------------------
console.debug("Defining NOC.core.label.TreePicker");

Ext.define("NOC.core.label.TreePicker", {
  extend: "Ext.tree.Panel",
  alias: "widget.core.label.treepicker",
  controller: "core.label.treepicker",
  requires: [
    "NOC.core.label.LabelFieldModel",
    "NOC.core.label.TreePickerController",
  ],
  baseCls: Ext.baseCSSPrefix + "boundlist",
  shrinkWrap: 2,
  shrinkWrapDock: true,
  animCollapse: true,
  singleExpand: false,
  useArrows: true,
  scrollable: true,
  floating: true,
  manageHeight: false,
  collapseFirst: false,
  rootVisible: false,
  selModel: {
    mode: "SIMPLE",
  },
  tbar: [
    {
      xtype: "searchfield",
      width: "90%",
      emptyText: __("pattern"),
      enableKeyEvents: true,
      triggers: {
        clear: {
          cls: "x-form-clear-trigger",
          hidden: true,
          handler: "onClearSearchField",
        },
      },
      listeners: {
        keyup: "onChangeSearchField",
      },
    },
    "->",
    {
      glyph: NOC.glyph.times_circle,
      tooltip: __("Close"),
      handler: "onClosePanel",
    },
  ],
  store: {
    model: "NOC.core.label.LabelFieldModel",
    autoLoad: true,
    proxy: {
      url: "/main/label/lookup_tree/",
      type: "ajax",
      extraParams: this.query,
      reader: "json",
    },
  },
  listeners: {
    itemclick: "onItemClick",
    itemkeydown: "onPickerKeyDown",
    focusleave: "onLeaveFocusTreePicker",
  },
});
