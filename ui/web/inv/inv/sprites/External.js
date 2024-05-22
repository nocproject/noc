//---------------------------------------------------------------------
// NOC.inv.inv.sprites.External
// Render SVG external connection
//---------------------------------------------------------------------
// Copyright (C) 2007-2024 The NOC Project
// See LICENSE for details
//---------------------------------------------------------------------
console.debug("Defining NOC.inv.inv.sprites.External");

Ext.define("NOC.inv.inv.sprites.External", {
  extend: "Ext.draw.sprite.Composite",
  alias: "sprite.external",
  inheritableStatics: {
    def: {
      processors: {
        fromXY: "data",
        length: "number",
        side: "string",
        actualScale: "number",
        box: "data",
        isSelected: "bool",
        remoteId: "string",
        remoteName: "string",
        remoteSlot: "string",
      },
      triggers: {
        fromXY: "recalculate",
        length: "recalculate",
        isSelected: "select",
      },
      updaters: {
        recalculate: function(attr){
          var me = this;

          me.createSprites(attr);
        },
        select: function(attr){
          var me = this;

          if(me.marker){
            console.log("select : ", attr.isSelected);
          }
        },
      },
    },
  },
  config: {
    boxWidth: 15,
    boxHeight: 15,
    fontSize: 12,
    fontFamily: "arial",
    fontWeight: "normal",
    opacity: 0.7,
  },
  createSprites: function(attr){
    var me = this;
    
    if(!me.line){
      var offsetX = attr.box[0] / 2,
        fromX = attr.fromXY[0],
        fromY = attr.fromXY[1] + 0.5 * attr.box[1],
        length = (attr.side === "left" ? 1 : -1) * attr.length;

      me.line = me.add({
        type: "path",
        lineWidth: 2,
        path: Ext.String.format("M{0},{1} L{2},{3}",
                                fromX + offsetX, fromY, fromX + length, fromY),
        strokeStyle: "black",
      });
      var labelWidth = me.measureText(me.remoteSlot);
      var labelXY = [
        fromX + length + (me.side === "left" ? -0.7 * me.box[0] - labelWidth: 0.7 * me.box[0]),
        fromY,
      ];
      me.labelBackground = me.add({
        type: "rect",
        fill: "white",
        x: labelXY[0] + (me.side === "left" ? - 0.5 * me.box[0] : 0.5 * me.box[0]),
        y: labelXY[1] - 0.5 * me.box[1],
        width: labelWidth + 0.5 * me.box[0],
      });
      me.label = me.add({
        type: "text",
        fontFamily: me.getFontFamily(),
        fontWeight: me.getFontWeight(),
        fontSize: me.getFontSize(),
        textBaseline: "middle",
        text: me.remoteSlot,
        x: labelXY[0] + (me.side === "left" ? 0 : 0.7 * me.box[0]),
        y: labelXY[1],
      });
      me.boxSprite = me.add({
        type: "rect",
        x: fromX + length,
        y: fromY - 0.5 * me.box[0],
        width: me.box[0],
        height: me.box[1],
        stroke: "black",
        lineWidth: 1,
        fill: "white",
      });
      var arrowStartXY = [fromX + length + me.box[0], fromY];
      var path;
      if(me.side === "left"){
        path = Ext.String.format("M{0},{1} L{2},{3} L{4},{5} L{6},{7} L{8},{9} L{10},{11} Z",
                                 arrowStartXY[0], arrowStartXY[1],
                                 arrowStartXY[0], arrowStartXY[1] + 0.65 * me.box[1],
                                 arrowStartXY[0] + 1.25 * me.box[0], arrowStartXY[1] + 0.65 * me.box[1],
                                 arrowStartXY[0] + 2 * me.box[0], arrowStartXY[1],
                                 arrowStartXY[0] + 1.25 * me.box[0], arrowStartXY[1] - 0.65 * me.box[1],
                                 arrowStartXY[0], arrowStartXY[1] - 0.65 * me.box[1],
        );
      } else{
        arrowStartXY = [fromX + length, fromY];
        path = Ext.String.format("M{0},{1} L{2},{3} L{4},{5} L{6},{7} L{8},{9} L{10},{11} Z",
                                 arrowStartXY[0], arrowStartXY[1],
                                 arrowStartXY[0], arrowStartXY[1] + 0.65 * me.box[1],
                                 arrowStartXY[0] - 1.25 * me.box[0], arrowStartXY[1] + 0.65 * me.box[1],
                                 arrowStartXY[0] - 2 * me.box[0], arrowStartXY[1],
                                 arrowStartXY[0] - 1.25 * me.box[0], arrowStartXY[1] - 0.65 * me.box[1],
                                 arrowStartXY[0], arrowStartXY[1] - 0.65 * me.box[1],
        );
      }
      me.arrow = me.add({
        type: "path",
        path: path,
        stroke: "black",
      });
    }
  },
  hitTest: function(point){
    var me = this,
      x = point[0],
      y = point[1];

    if(me.line.isPointOnPath(x, y)){
      return {
        sprite: me,
      };
    }
    if(me.isOnSprite(me.boxSprite.getBBox(), x, y)){
      return {
        sprite: me,
      };
    }
    if(me.isOnSprite(me.labelBackground.getBBox(), x, y)){
      return {
        sprite: me,
      };
    }
    if(me.isOnSprite(me.arrow.getBBox(), x, y)){
      return {
        sprite: me,
      };
    }
    return null;
  },
  isOnSprite: function(bbox, x, y){
    if(bbox && x >= bbox.x && x <= (bbox.x + bbox.width) && y >= bbox.y && y <= (bbox.y + bbox.height)){
      return true;
    }
    return false;
  },
  measureText: function(text){
    var me = this,
      font = Ext.String.format("{0} {1}px {2}", me.getFontWeight(), me.getFontSize(), me.getFontFamily());
    return Ext.draw.TextMeasurer.measureText(text, font).width;
  },
});