//---------------------------------------------------------------------
// Application UI
//---------------------------------------------------------------------
// Copyright (C) 2007-2024d The NOC Project
// See LICENSE for details
//---------------------------------------------------------------------
console.debug("Defining NOC application");

Ext.application({
  name: "NOC",
  paths: {
    "NOC": "/ui/web",
    "Ext.ux": "/ui/web/ux",
  },
  name: "NOC",
  paths: {
    "NOC": "/ui/web",
    "Ext.ux": "/ui/web/ux",
  },

  requires: [
    "NOC.main.desktop.Application",
  ],

  launch: function(){
    var me = this;
    Ext.setGlyphFontFamily("FontAwesome");
    console.log("Initializing history API");
    Ext.History.init();
    console.log("NOC application starting");
    // Create viewport
    me.app = Ext.create("NOC.main.desktop.Application");
  },
});
