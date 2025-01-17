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
          this.createSprites();
          this.rect.setAttributes({
            x: attr.x,
            y: attr.y,
            width: attr.width,
            height: attr.height,
          });
          if(this.tooltip.isVisible()){
            this.tooltip.setHtml(attr.name + " : " + attr.value); 
            this.tooltip.showAt(this.canvasToPageCoordinates(attr.x, attr.y - 40));
          }
          this.rect.setAnimation({
            duration: 500,
            easing: "easeInOut",
          });
        },
        mouseOver: function(attr){
          this.rect.setAnimation({duration: 0}); 
          if(attr.mouseOver){
            this.tooltip.setHtml(attr.name + " : " + attr.value);
            this.tooltip.showAt(this.canvasToPageCoordinates(attr.x, attr.y - 40));
            this.rect.setAttributes({
              scalingX: 2,
              fill: "red",
            });
          } else{
            this.tooltip.hide();
            this.rect.setAnimation(false); 
            this.rect.setAttributes({
              scalingX: 1,
              fill: "blue",
            });
          }
        },
      },
    },
  },
  createSprites: function(){
    if(!this.rect){
      this.rect = this.add({
        type: "rect",
        fill: "blue",
      });
      this.tooltip = Ext.create("Ext.tip.ToolTip", {
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