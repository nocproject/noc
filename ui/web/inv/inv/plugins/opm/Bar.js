//---------------------------------------------------------------------
// NOC.inv.inv.plugins.opm.Bar
//---------------------------------------------------------------------
// Copyright (C) 2007-2025 The NOC Project
// See LICENSE for details
//---------------------------------------------------------------------
console.debug("Defining NOC.inv.inv.plugins.opm.Bar");

Ext.define("NOC.inv.inv.plugins.opm.Bar", {
  extend: "Ext.draw.sprite.Composite",
  alias: "sprite.bar",
  inheritableStatics: {
    def: {
      processors: {
        x: "number",
        y: "number",
        width: "number",
        height: "number",
        value: "number",
        mouseOver: "bool",
        pageX: "number",
        pageY: "number",
        name: "string",
      },
      triggers: {
        width: "recalculate",
        height: "recalculate",
        value: "recalculate",
        x: "recalculate",
        y: "recalculate",
        mouseOver: "mouseOver",
        pageX: "mouseOver",
        pageY: "mouseOver",
        name: "recalculate",
      },
      updaters: {
        recalculate: function(attr){
          this.createSprites(attr);
          this.rect.setAttributes({
            x: attr.x,
            y: attr.y,
            width: attr.width,
            height: attr.height,
          });
        },
        mouseOver: function(attr){
          this.rect.setAttributes({
            fill: attr.mouseOver ? "red" : "blue",
          });
          if(attr.mouseOver){
            this.tooltip.showAt(this.canvasToPageCoordinates(attr.x, attr.y - 40));
            this.rect.setAttributes({
              scalingX: 2,
            });
          } else{
            this.tooltip.hide();
            this.rect.setAttributes({
              scalingX: 1,
            });
          }
        //   this.rect.setAnimation({
        //     duration: 200,
        //     easing: "easeInOut",
        //   });
        },
      },
    },
  },
  createSprites: function(attr){
    if(!this.rect){
      this.rect = this.add({
        type: "rect",
        fill: "blue",
      });
      this.tooltip = Ext.create("Ext.tip.ToolTip", {
        html: attr.name + " : " + attr.value,
        hidden: true,
      });
    }
  },
  hitTest: function(point){
    var x = point[0],
      y = point[1];

    if(this.rect){
      if(this.isOnSprite(this.rect.getBBox(), x, y)){
        return {
          sprite: this,
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
  canvasToPageCoordinates: function(canvasX, canvasY){
    var canvas = this.getSurface().el.dom.querySelector("canvas"),
      rect = canvas.getBoundingClientRect(),
      scrollLeft = window.pageXOffset || document.documentElement.scrollLeft,
      scrollTop = window.pageYOffset || document.documentElement.scrollTop;
            
    return [
      canvasX + rect.left + scrollLeft,
      canvasY + rect.top + scrollTop,
    ];
  },
});