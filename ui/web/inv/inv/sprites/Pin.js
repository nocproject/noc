//---------------------------------------------------------------------
// NOC.inv.inv.sprites.Pin
// Render SVG pin image
//---------------------------------------------------------------------
// Copyright (C) 2007-2024 The NOC Project
// See LICENSE for details
//---------------------------------------------------------------------
console.debug("Defining NOC.inv.inv.sprites.Pin");

Ext.define("NOC.inv.inv.sprites.Pin", {
  extend: "Ext.draw.sprite.Composite",
  alias: "sprite.pin",
  inheritableStatics: {
    def: {
      processors: {
        pinColor: "string",
        internalColor: "string",
        pinName: "string",
        pinNameOrig: "string",
        pinNameWidth: "number",
        labelAlign: "string",
        labelColor: "string",
        internalLabelWidth: "number",
        hasInternalLabel: "bool",
        remoteId: "string",
        remoteName: "string",
        remoteSlot: "string",
        remoteSlotWidth: "number",
        side: "string",
        isSelected: "bool",
        isInternalFixed: "bool",
        cursorOn: "string",
        enabled: "bool",
        masked: "bool",
        pinOver: "bool",
        internalEnabled: "bool",
        allowInternal: "bool",
        allowDiscriminators: "data",
        x: "number",
        y: "number",
        actualScale: "number",
      },
      triggers: {
        pinColor: "recalculate",
        internalColor: "recalculate",
        isSelected: "recalculate",
        isInternalFixed: "recalculate",
        hasInternalLabel: "recalculate",
        pinName: "recalculate",
        labelAlign: "recalculate",
        labelColor: "recalculate",
        remoteId: "recalculate",
        remoteName: "recalculate",
        remoteSlot: "recalculate",
        side: "recalculate",
        allowInternal: "recalculate",
        allowDiscriminators: "recalculate",
        enabled: "recalculate",
        masked: "recalculate",
        pinOver: "recalculate",
        internalEnabled: "recalculate",
        x: "recalculate",
        y: "recalculate",
        actualScale: "rescale",
      },
      defaults: {
        pinColor: "#2c3e50",
        internalColor: "#2c3e50",
        pinName: "Undefined",
        pinNameWidth: 0,
        remoteId: "none",
        remoteName: "none",
        remoteSlot: "none",
        remoteSlotWidth: 0,
        isSelected: false,
        isInternalFixed: false,
        enabled: true,
        masked: false,
        internalEnabled: true,
        allowInternal: false,
        side: "left",
        labelAlign: "right", // "left" | "right"
        internalLabelWidth: 10,
        hasInternalLabel: false,
        actualScale: 1,
      },
      updaters: {
        recalculate: function(attr){
          var me = this;

          me.createSprites();
          me.box.setAttributes({
            translationX: attr.x,
            translationY: attr.y,
            fillStyle: attr.pinColor,
            stroke: attr.isSelected && !attr.isInternalFixed ? "lightgreen" : "black",
            lineWidth: attr.isSelected && !attr.isInternalFixed ? 3 : 1,
          });
          me.pinName = attr.pinName;
          me.pinNameOrig = attr.pinNameOrig;
          me.pinNameWidth = me.measureText(attr.pinName) + 0.2 * me.getBoxWidth();
          me.remoteSlotWidth = 0;
          if(me.remoteSlot !== "none"){
            me.remoteSlotWidth = me.measureText(me.remoteSlot) + 0.2 * me.getBoxWidth() + 20;
          }
          me.enabled = attr.enabled;
          me.internalEnabled = attr.internalEnabled;
          me.pinColor = attr.pinColor;
          me.internalColor = attr.internalColor;
          me.allowDiscriminators = attr.allowDiscriminators;
          me.label.setAttributes({
            text: attr.pinName,
            fontWeight: attr.pinOver ? 'bold' : me.getFontWeight(),
            textAlign: attr.labelAlign === "left" ? "end" : "start",
            fill: attr.labelColor,
          });
          if(me.internal){
            var internalCirclePadding = me.getBoxWidth() * (attr.side === "left" ? -1 : 2);

            if(attr.hasInternalLabel){
              internalCirclePadding = me.getBoxWidth() * (attr.side === "left" ? 0 : 1);
            }
            me.internal.setAttributes({
              translationX: attr.x + (attr.hasInternalLabel ? attr.internalLabelWidth : 0) + internalCirclePadding,
              translationY: attr.y + me.getBoxHeight() / 2,
              fillStyle: attr.internalColor,
              stroke: attr.isSelected && attr.isInternalFixed ? "lightgreen" : "black",
              lineWidth: attr.isSelected && attr.isInternalFixed ? 3 : 1,
            });
          }
          me.label.setAttributes({
            translationX: ((me.attr.labelAlign === "left" ? -0.25 : 1.25) * me.getBoxWidth()) + attr.x,
            translationY: attr.y,
          });
          me.labelBackground.setAttributes({
            translationX: attr.x + (me.attr.side === "left" ? me.getBoxWidth() + 2 : - 2 - me.pinNameWidth),
            translationY: attr.y,
            height: me.getBoxHeight(),
            width: me.pinNameWidth,
          });
        },
        rescale: function(attr){
          var me = this;

          me.createSprites();
          me.box.setAnimation({
            duration: 200,
            easing: "easeInOut",
          });
          me.box.setAttributes({
            scalingX: attr.actualScale,
            scalingY: attr.actualScale,
          });
          // me.label.setAttributes({
          // scalingX: attr.actualScale,
          // scalingY: attr.actualScale,
          // });
          if(me.internal){
            me.internal.setAttributes({
              scalingX: attr.actualScale,
              scalingY: attr.actualScale,
            });
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
  hitTest: function(point){
    // Removed the isVisible check since pin will always be visible.
    var me = this,
      x = point[0],
      y = point[1];
    if(me.internal){
      if(me.isOnSprite(me.internal.getBBox(), x, y, "internal")){
        return {
          sprite: me,
        };
      }
    }
    if(me.isOnSprite(me.box.getBBox(), x, y, "wire")){
      return {
        sprite: me,
      };
    }
    if(me.isOnSprite(me.label.getBBox(), x, y, "wire")){
      return {
        sprite: me,
      };
    }

    return null;
  },
  isOnSprite: function(bbox, x, y, on){
    var me = this;

    if(bbox && x >= bbox.x && x <= (bbox.x + bbox.width) && y >= bbox.y && y <= (bbox.y + bbox.height)){
      me.setAttributes({cursorOn: on});
      return true;
    }
    return false;
  },
  createSprites: function(){
    var me = this;

    if(!me.box){
      me.box = me.add({
        type: "rect",
        width: me.getBoxWidth(),
        height: me.getBoxHeight(),
        stroke: "black",
        lineWidth: 2,
      });
      if(me.allowInternal){
        me.internal = me.add({
          type: "circle",
          radius: me.getBoxWidth() / 2,
          stroke: "black",
          lineWidth: 2,
          x: 0,
          y: 0,
        });
      }
      me.labelBackground = me.add({
        type: "rect",
        fill: "white",
        // hidden: true,
        // stroke: "black",
        // lineWidth: 1,
      })
      me.label = me.add({
        type: "text",
        fontFamily: me.getFontFamily(),
        fontWeight: me.getFontWeight(),
        fontSize: me.getFontSize(),
        textBaseline: "middle",
        x: 0,
        y: me.box.height / 2,
        // hidden: true,
      });
    }
  },
  measureText: function(text){
    var me = this,
      font = Ext.String.format("{0} {1}px {2}", me.getFontWeight(), me.getFontSize(), me.getFontFamily());
    return Ext.draw.TextMeasurer.measureText(text, font).width;
  },
});
