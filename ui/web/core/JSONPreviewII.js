//---------------------------------------------------------------------
// NOC.core.JSONPreviewII monaco editor
//---------------------------------------------------------------------
// Copyright (C) 2007-2025 The NOC Project
// See LICENSE for details
//---------------------------------------------------------------------
console.debug("Defining NOC.core.JSONPreviewII");

Ext.define("NOC.core.JSONPreviewII", {
  extend: "NOC.core.MonacoPanel",
  app: null,
  restUrl: null,
  previewName: null,
  tbar: [
    {
      itemId: "close",
      text: __("Close"),
      glyph: NOC.glyph.arrow_left,
      handler: "onBack",
    },
  ],
  initComponent: function(){
    this.items[0].language = "json";
    this.callParent();
  },
});