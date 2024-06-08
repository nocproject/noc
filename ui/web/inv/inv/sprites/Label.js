//---------------------------------------------------------------------
// NOC.inv.inv.sprites.Label
// Render SVG object label
//---------------------------------------------------------------------
// Copyright (C) 2007-2024 The NOC Project
// See LICENSE for details
//---------------------------------------------------------------------
console.debug("Defining NOC.inv.inv.sprites.Label");

Ext.define("NOC.inv.inv.sprites.Label", {
  extend: "Ext.draw.sprite.Composite",
  alias: "sprite.label",
  inheritableStatics: {
    def: {
      processors: {
        pinId: "string",
        backgroundFill: "string",
        backgroundTranslationX: "number",
        backgroundTranslationY: "number",
        backgroundWidth: "number",
        backgroundHeight: "number",
        labelTextBaseline: "string",
        labelTextAlign: "string",
        labelText: "string",
        labelX: "number",
        labelY: "number",
        labelTranslationX: "number",
        labelTranslationY: "number",
        labelFontFamily: "string",
        labelFontWeight: "string",
        labelFontSize: "string",
        isSelected: "bool",
        labelColor: "string",
        enabled: "bool",
      },
      triggers: {
        pinId: "recalculate",
        backgroundFill: "recalculate",
        backgroundTranslationX: "recalculate",
        backgroundTranslationY: "recalculate",
        backgroundWidth: "recalculate",
        backgroundHeight: "recalculate",
        labelFontFamily: "recalculate",
        labelFontWeight: "recalculate",
        labelFontSize: "recalculate",
        labelTextBaseline: "recalculate",
        labelTextAlign: "recalculate",
        labelText: "recalculate",
        labelX: "recalculate",
        labelY: "recalculate",
        labelTranslationX: "recalculate",
        labelTranslationY: "recalculate",
        isSelected: "recalculate",
        labelColor: "recalculate",
        enabled: "recalculate",
      },
      updaters: {
        recalculate: function(attr){
          var me = this;

          me.createSprites(attr);
          me.rect.setAttributes({
            fill: attr.backgroundFill,
            translationX: attr.backgroundTranslationX,
            translationY: attr.backgroundTranslationY,
            width: attr.backgroundWidth,
            height: attr.backgroundHeight,
          });
          me.label.setAttributes({
            fontFamily: attr.labelFontFamily,
            fontWeight: attr.isSelected ? 'bold' : 'normal',
            fontSize: attr.labelFontSize,
            text: attr.labelText,
            textBaseline: attr.textBaseline,
            textAlign: attr.labelTextAlign,
            x: attr.labelX,
            y: attr.labelY,
            translationX: attr.labelTranslationX,
            translationY: attr.labelTranslationY,
            fill: attr.labelColor,
          });
        },
      },
    },
  },
  config: {
    isSelected: false,
    opacity: 0.7,
  },
  hitTest: function(point){
    var me = this,
      bbox = me.rect.getBBox(),
      x = point[0],
      y = point[1];

    if(bbox && x >= bbox.x && x <= (bbox.x + bbox.width) && y >= bbox.y && y <= (bbox.y + bbox.height)){
      return {
        sprite: me,
      }
    }
    return null;
  },
  createSprites: function(attr){
    var me = this;

    if(!me.rect){
      me.rect = me.add({
        type: "rect",
        fill: attr.backgroundFill,
        translationX: attr.backgroundTranslationX,
        translationY: attr.backgroundTranslationY,
        width: attr.backgroundWidth,
        height: attr.backgroundHeight,
        // stroke: "black",
        // lineWidth: 1,
        hidden: false,
      });
      me.label = me.add({
        type: "text",
        textBaseline: attr.labelTextBaseline,
        textAlign: attr.labelTextAlign,
        text: attr.labelText,
        x: attr.labelX,
        y: attr.labelY,
        translationX: attr.labelTranslationX,
        translationY: attr.labelTranslationY,
        hidden: false,
      });
    }
  },
});
