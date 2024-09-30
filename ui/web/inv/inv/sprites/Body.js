//---------------------------------------------------------------------
// NOC.inv.inv.sprites.Body
// Render SVG object body
//---------------------------------------------------------------------
// Copyright (C) 2007-2024 The NOC Project
// See LICENSE for details
//---------------------------------------------------------------------
console.debug("Defining NOC.inv.inv.sprites.Body");

Ext.define("NOC.inv.inv.sprites.Body", {
  extend: "Ext.draw.sprite.Composite",
  alias: "sprite.body",
  inheritableStatics: {
    def: {
      processors: {
        side: "string",
        width: "number",
        height: "number",
        gap: "number",
        label: "string",
        boxWidth: "number",
        boxHeight: "number",
        x: "number",
        y: "number",
      },
      triggers: {
        label: "recalculate",
        width: "recalculate",
        height: "recalculate",
        gap: "recalculate",
        x: "recalculate",
        y: "recalculate",
      },
      defaults: {
        side: "left", // "left" | "right"
      },
      updaters: {
        recalculate: function(attr){
          var me = this,
            pointX = attr.x + (attr.side === "left" ? 0 : attr.boxWidth);

          me.createSprites(attr);
          me.rect.setAttributes({
            width: attr.width,
            height: attr.height,
            x: pointX,
            y: attr.y,
          });
          me.label.setAttributes({
            text: attr.label,
            textAlign: attr.side === "left" ? "start" : "end",
            x: pointX + (attr.side === "left" ? 0 : attr.width),
            y: attr.y - attr.gap,
          });
        },
      },
    },
  },
  config: {
    fontSize: 14,
    fontFamily: "arial",
    fontWeight: "bold",
    backgroundColor: "#bdc3c7",
  },
  hitTest: function(){
    return null;
  },
  createSprites: function(){
    var me = this;

    if(!me.rect){
      me.rect = me.add({
        type: "rect",
        stroke: "black",
        fill: me.getBackgroundColor(),
        lineWidth: 2,
      });
      me.label = me.add({
        type: "text",
        fontFamily: me.getFontFamily(),
        fontWeight: me.getFontWeight(),
        fontSize: me.getFontSize(),
      });
    }
  },
});
