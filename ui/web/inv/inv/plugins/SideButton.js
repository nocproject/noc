//---------------------------------------------------------------------
// inv.inv.plugins.SideButton widget
//---------------------------------------------------------------------
// Copyright (C) 2007-2024 The NOC Project
// See LICENSE for details
//---------------------------------------------------------------------
console.debug("Defining NOC.inv.inv.plugins.SideButton");

Ext.define("NOC.inv.inv.plugins.SideButton", {
  extend: "Ext.button.Segmented",
  alias: "widget.invPluginsSegmented",
  defaultListenerScope: true,
  bind: {
    disabled: "{!hasRear}",
  },
  items: [
    {
      glyph: NOC.glyph.hand_o_right,
      text: __("Front"),
      toggleGroup: "side",
      bind: {
        pressed: "{isFrontPressed}",
      },
      handler: "onFrontPressed",
    },
    {
      glyph: NOC.glyph.hand_o_left,
      text: __("Rear"),
      toggleGroup: "side",
      bind: {
        pressed: "{isRearPressed}",
      },
      handler: "onRearPressed", 
    },
  ],
  onFrontPressed: function(){
    this.fireEvent("sideChange", "front");
  },
  onRearPressed: function(){
    this.fireEvent("sideChange", "rear");
  },
});