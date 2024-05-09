//---------------------------------------------------------------------
// NOC.inv.inv.sprites.Connection
// Render SVG connection
//---------------------------------------------------------------------
// Copyright (C) 2007-2024 The NOC Project
// See LICENSE for details
//---------------------------------------------------------------------
console.debug("Defining NOC.inv.inv.sprites.Connection");

Ext.define("NOC.inv.inv.sprites.Connection", {
  extend: "Ext.draw.sprite.Composite",
  alias: "sprite.connection",
  inheritableStatics: {
    def: {
      processors: {
        connectionType: "string",
        fromPortId: "string",
        fromPort: "string",
        fromXY: "data",
        fromHasArrow: "bool",
        fromDiscriminator: "string",
        fromSide: "string",
        toPortId: "string",
        toPort: "string",
        toXY: "data",
        toHasArrow: "bool",
        toDiscriminator: "string",
        toSide: "string",
        cable: "string",
        offset: "data",
        isDeleted: "bool",
        discriminatorWidth: "number",
        gainDb: "number",
        actualScale: "number",
        trace: "number",
        path: "string",
        length: "number",
        isNew: "bool",
        isSelected: "bool",
      },
      triggers: {
        path: "recalculate",
        fromDiscriminator: "recalculate",
        toDiscriminator: "recalculate",
        gainDb: "recalculate",
        discriminatorWidth: "recalculate",
        cable: "recalculate",
        isNew: "recalculate",
        isSelected: "recalculate",
      },
      defaults: {
      },
      updaters: {
        recalculate: function(attr){
          var me = this,
            path = attr.path;

          me.createSprites(attr);
          me.isNew = attr.isNew;
          me.cable = attr.cable;
          me.gainDb = attr.gainDb;
          if(attr.connectionType === "wire"){
            path = Ext.String.format("M{0},{1} L{2},{3} L{4},{5} L{6},{7}",
                                     attr.fromXY[0], attr.fromXY[1],
                                     attr.fromXY[0] + attr.offset[0], attr.fromXY[1],
                                     attr.toXY[0] - attr.offset[1], attr.toXY[1],
                                     attr.toXY[0], attr.toXY[1]);
          }
          if(attr.connectionType === "loopback"){
            path = Ext.String.format("M{0},{1} L{2},{3} L{4},{5} L{6},{7}",
                                     attr.fromXY[0], attr.fromXY[1],
                                     attr.fromXY[0] + (attr.fromSide === "left" ? 1 * attr.offset[0] : -1 * attr.offset[1]), attr.fromXY[1],
                                     attr.fromXY[0] + (attr.fromSide === "left" ? 1 * attr.offset[0] : -1 * attr.offset[1]), attr.toXY[1],
                                     attr.toXY[0], attr.toXY[1]);
          }
          me.line.setAttributes({
            side: attr.fromSide,
            fromPortId: attr.fromPortId,
            toPortId: attr.toPortId,
            connectionType: attr.connectionType,
            path: path,
            strokeStyle: me.getColor(attr),
            "marker-end": "url(#arrow)",
          });

          if(!Ext.isEmpty(attr.fromDiscriminator)){
            me.fromDisc.setAttributes({
              text: me.makeEllipses(attr.fromDiscriminator, attr.discriminatorWidth),
              textAlign: attr.fromSide === "left" ? "start" : "end",
              translationX: parseFloat(attr.fromXY[0], 10) + me.getBoxWidth() * (attr.fromSide === "left" ? 1 : -1),
              translationY: parseFloat(attr.fromXY[1], 10),
            });
            if(!me.fromDiscriminatorTooltip && me.measureText(attr.fromDiscriminator) > me.measureText(me.fromDisc.attr.text)){
              me.fromDiscriminatorTooltip = Ext.create("Ext.tip.ToolTip", {
                html: attr.fromDiscriminator,
                hidden: true,
              });
            }
          }
          if(!Ext.isEmpty(attr.toDiscriminator)){
            me.toDisc.setAttributes({
              text: me.makeEllipses(attr.toDiscriminator, attr.discriminatorWidth),
              textAlign: attr.toSide === "left" ? "start" : "end",
              translationX: parseFloat(attr.toXY[0], 10) + me.getBoxWidth() * (attr.fromSide === "left" ? 1 : -1),
              translationY: parseFloat(attr.toXY[1], 10),
            });
            if(!me.toDiscriminatorTooltip && me.measureText(attr.toDiscriminator) > me.measureText(me.toDisc.attr.text)){
              me.toDiscriminatorTooltip = Ext.create("Ext.tip.ToolTip", {
                html: attr.toDiscriminator,
                hidden: true,
              });
            }
          }
          if(me.toArrowMarker){
            me.toArrowMarker.setAttributes({
              translationX: parseFloat(attr.toXY[0], 10),
              translationY: parseFloat(attr.toXY[1], 10),
              hidden: false,
            });
          }
          if(me.fromArrowMarker){
            me.fromArrowMarker.setAttributes({
              translationX: parseFloat(attr.fromXY[0], 10),
              translationY: parseFloat(attr.fromXY[1], 10),
              hidden: false,
            });
          }
        },
      },
    },
  },
  config: {
    boxWidth: 15,
    boxHeight: 15,
    fontSize: 10,
    fontFamily: "arial",
    fontWeight: "normal",
    availableColor: "#1F6D91",
    newColor: "lightgreen",
    disabledColor: "#d0d0d0",
    selectedColor: "#f5d63c",
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

    if(me.toDisc){
      if(me.isOnSprite(me.toDisc.getBBox(), x, y)){
        return {
          sprite: me,
        };
      }
    }
    if(me.fromDisc){
      if(me.isOnSprite(me.fromDisc.getBBox(), x, y)){
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
  createSprites: function(attr){
    var me = this;

    if(!me.line){
      me.line = me.add({
        type: "path",
        lineWidth: 2,
      });
      if(attr.toHasArrow){
        me.toArrowMarker = me.add(me.getMarker("arrow", attr.toSide, attr.actualScale));
      }
      if(attr.fromHasArrow){
        me.fromArrowMarker = me.add(me.getMarker("arrow", attr.fromSide, attr.actualScale));
      }
      if(attr.toDiscriminator){
        me.toDisc = me.add({
          type: "text",
          fontFamily: me.getFontFamily(),
          fontWeight: me.getFontWeight(),
          fontSize: me.getFontSize(),
          textBaseline: "middle",
        });
      }
      if(attr.fromDiscriminator){
        me.fromDisc = me.add({
          type: "text",
          fontFamily: me.getFontFamily(),
          fontWeight: me.getFontWeight(),
          fontSize: me.getFontSize(),
          textBaseline: "middle",
        });
      }
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
  makeEllipses: function(text, reservedWidth){
    var me = this,
      width = me.measureText(text),
      suffix = "...";

    reservedWidth = Math.abs(reservedWidth) - me.getBoxWidth() * 1.1;
    if(reservedWidth > 0 && width > reservedWidth){
      while(width > reservedWidth){
        text = text.slice(0, -1);
        width = me.measureText(text + suffix);
      }
      text += suffix;
    }
    return text;
  },
  measureText: function(text){
    var me = this,
      font = Ext.String.format("{0} {1}px {2}", me.getFontWeight(), me.getFontSize(), me.getFontFamily());
    return Ext.draw.TextMeasurer.measureText(text, font).width;
  },
  getColor: function(attr){
    var me = this;

    if(attr.isSelected){
      return me.getSelectedColor();
    } else if(attr.isNew){
      return me.getNewColor();
    } else if(!attr.isDeleted){
      return me.getDisabledColor();
    } else{
      return me.getAvailableColor();
    }
  },
});
