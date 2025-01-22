//---------------------------------------------------------------------
// NOC.inv.inv.plugins.opm.OPMLegendSprite
//---------------------------------------------------------------------
// Copyright (C) 2007-2025 The NOC Project
// See LICENSE for details
//---------------------------------------------------------------------
console.debug("Defining NOC.inv.inv.plugins.opm.OPMLegendSprite");

Ext.define("NOC.inv.inv.plugins.opm.OPMLegendSprite", {
  extend: "Ext.draw.sprite.Composite",
  alias: "sprite.legend",
  inheritableStatics: {
    def: {
      processors: {
        dirs: "data",
        colors: "data",
        width: "number",
        x: "number",
        y: "number",
        mouseOver: "bool",
        dir: "string",
        pageX: "number",
        pageY: "number",
      },
      triggers: {
        dirs: "recalculate",
        colors: "recalculate",
        width: "recalculate",
        x: "recalculate",
        y: "recalculate",
        mouseOver: "mouseOver",
        dir: "mouseOver",
        pageX: "mouseOver",
        pageY: "mouseOver",
      },
      updaters: {
        recalculate: function(attr){
          this.createSprites(attr);
        },
        mouseOver: function(attr){
          if(attr.mouseOver){
            this.texts.forEach((text) => {
              if(text.text === attr.dir){
                text.setAttributes({
                  scalingX: 1.2,
                  scalingY: 1.2,
                  fontWeight: "bold",
                });
              }
            });
          } else{
            this.texts.forEach((text) => {
              text.setAttributes({
                scalingX: 1,
                scalingY: 1,
                fontWeight: "normal",
              });
            });
          }
        },
      },
    },
  },
  config: {
    fontSize: 10,
    fontFamily: "arial",
    fontWeight: "normal",
  },
  createSprites: function(attr){
    var x = attr.x;
    this.texts = [];
    attr.dirs.forEach((dir, index) => {
      this.add({
        type: "rect",
        x: x,
        y: attr.y,
        width: 10,
        height: 10,
        fill: attr.colors[index],
        strokeStyle: "black",
        text: dir,
      });

      this.texts.push(this.add({
        type: "text",
        x: x + 15,
        y: attr.y,
        text: dir,
        fill: "black",
        textAlign: "left",
        textBaseline: "top",
      }));
      if(x + this.measureText(dir) + 30 > attr.width){
        x = attr.x;
        attr.y += 20;
      } else{
        x += this.measureText(dir) + 30;
      }
    }, this);
  },
  hitTest: function(point){
    var x = point[0],
      y = point[1],
      sprites = this.sprites;
    for(var i = 0; i < sprites.length; i++){
      if(this.isOnSprite(sprites[i].getBBox(), x, y)){
        return {
          sprite: Ext.apply({dir: sprites[i].text}, this),
        };
      }
    }
  },
  isOnSprite: function(bbox, x, y){
    if(bbox && x >= bbox.x && x <= (bbox.x + bbox.width) && y >= bbox.y && y <= (bbox.y + bbox.height)){
      return true;
    }
    return false;
  },
  measureText: function(text){
    var font = Ext.String.format("{0} {1}px {2}", this.getFontWeight(), this.getFontSize(), this.getFontFamily());
    return Ext.draw.TextMeasurer.measureText(text, font).width;
  },
});