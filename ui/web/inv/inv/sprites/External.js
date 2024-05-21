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
      me.marker = me.add(me.getMarker("connector", attr.side, attr.actualScale));
      me.marker.setAttributes({
        translationX: parseFloat(fromX + length, 10),
        translationY: parseFloat(fromY, 10),
        hidden: false,
      });
    }
  },
  getMarker: function(id, side, scale){
    var point1X = (side === "left" ? -1 : 1) * scale * 20,
      point1Y = (side === "left" ? -1 : 1) * scale * 7.5,
      path = Ext.String.format("M{0},{1} L{2},{3} L0,0 Z", point1X, point1Y, point1X, (-1) * point1Y);

    return {
      type: "path",
      id: id,
      fillStyle: "red",
      path: path,
      hidden: true,
    };
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
    return null;
  },
});