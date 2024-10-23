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
        model: "string",
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
          var label = attr.label,
            me = this,
            pointX = attr.x + (attr.side === "left" ? 0 : attr.boxWidth);

          me.createSprites(attr);
          me.rect.setAttributes({
            width: attr.width,
            height: attr.height,
            x: pointX,
            y: attr.y,
          });
          if(!me.labelTooltip && me.measureText(attr.label) > attr.width){
            label = me.makeEllipses(attr.label, attr.width);
            me.labelTooltip = Ext.create("Ext.tip.ToolTip", {
              html: attr.label,
              hidden: true,
            });
          }
          me.label.setAttributes({
            text: label + "\n" + attr.model,
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
  hitTest: function(point){
    var me = this,
      x = point[0],
      y = point[1];

    if(me.label){
      if(me.isOnSprite(me.label.getBBox(), x, y)){
        return {
          sprite: me,
        };
      }
    }
    return null;
  },
  isOnSprite: function(bbox, x, y){
    if(bbox && x >= bbox.x && x <= (bbox.x + bbox.width) && y >= bbox.y && y <= (bbox.y + bbox.height)){
      return true;
    }
    return false;
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
  measureText: function(text){
    var me = this,
      font = Ext.String.format("{0} {1}px {2}", me.getFontWeight(), me.getFontSize(), me.getFontFamily());
    return Ext.draw.TextMeasurer.measureText(text, font).width;
  },
  makeEllipses: function(text, reservedWidth){
    var me = this,
      width = me.measureText(text),
      prefix = "...";

    if(reservedWidth > 0 && width > reservedWidth){
      while(width > reservedWidth){
        text = text.slice(1);
        width = me.measureText(prefix + text);
      }
      prefix += text;
    }
    return prefix;
  },
});
