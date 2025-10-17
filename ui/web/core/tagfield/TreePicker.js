//---------------------------------------------------------------------
// core.treepicker widget
//---------------------------------------------------------------------
// Copyright (C) 2007-2020 The NOC Project
// See LICENSE for details
//---------------------------------------------------------------------
console.debug("Defining NOC.core.tagfield.TreePicker");

Ext.define("NOC.core.tagfield.TreePicker", {
  extend: "Ext.tree.Panel",
  alias: "widget.core.tagfield.treepicker",
  controller: "core.tagfield.treepicker",
  requires: [
    "NOC.core.tagfield.TreePickerController",
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
  currentLeaf: false,
  rootVisible: false,
  root: {
    expanded: true,
    children: [],
  },
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
  listeners: {
    itemclick: "onItemClick",
    itemkeydown: "onPickerKeyDown",
    beforeitemexpand: "onItemBeforeExpand",
    itemexpand: "onItemExpand",
    focusleave: "onLeaveFocusTreePicker",
  },
  initComponent: function(){
    // tree panel store
    this.treeStore = Ext.create("Ext.data.Store",
                                Ext.merge(
                                  Ext.clone(this.scope.getStore()),
                                  {
                                    autoLoad: true,
                                    pageSize: 500,
                                    proxy: {
                                      extraParams: {parent: ""},
                                    },
                                    listeners: {
                                      scope: this.getController(),
                                      load: this.getController().onLoadTree,
                                    },
                                  }, true));
    this.callParent();
  },
});
