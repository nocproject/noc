//---------------------------------------------------------------------
// Flex Layout
//---------------------------------------------------------------------
// Copyright (C) 2007-2024 The NOC Project
// See LICENSE for details
//---------------------------------------------------------------------

console.debug("Defining NOC.core.layout.Flex");

Ext.define("NOC.core.layout.Flex", {
  extend: "Ext.layout.container.Container",
  alias: "layout.flex",
  type: "flex",

  config: {
    display: "flex",
    direction: "row",
    wrap: "wrap",
    justifyContent: "flex-start",
    alignItems: "stretch",
  },

  autoSize: Ext.emptyFn,

  beginLayout: function(){
    var me = this,
      target = me.getRenderTarget();

    me.callParent(arguments);

    target.setStyle({
      display: me.display || "flex",
      flexDirection: me.direction || "row",
      flexWrap: me.wrap || "wrap",
      justifyContent: me.justifyContent || "flex-start",
      alignItems: me.alignItems || "stretch",
    });
  },

  beginLayoutCycle: function(){
    var me = this,
      items = me.getLayoutItems(),
      len = items.length,
      i, item;

    me.callParent(arguments);
    for(i = 0; i < len; i++){
      item = items[i];
      item.el.setStyle({
        flex: item.flex || "1 1 auto",
        margin: item.margin || "10px",
        minWidth: item.minWidth || "auto",
      });
    }
  },
});
