//---------------------------------------------------------------------
// NOC.inv.inv.plugins.opm.OPMChannelSprite
//---------------------------------------------------------------------
// Copyright (C) 2007-2025 The NOC Project
// See LICENSE for details
//---------------------------------------------------------------------
console.debug("Defining NOC.inv.inv.plugins.opm.OPMChannelSprite");

Ext.define("NOC.inv.inv.plugins.opm.OPMChannelSprite", {
  extend: "Ext.draw.sprite.Composite",
  alias: "sprite.channel",
  inheritableStatics: {
    def: {
      processors: {
        power: "data",
        band: "string",
        dir: "string",
        barColor: "string",
        selectedBarColor: "string",
        id: "number",
        x: "number",
        diagHeight: "number",
        diagPadding: "data",
        barSpacing: "number",
        barWidth: "number",
        value: "number",
        mouseOver: "string", // all | withoutTooltip | none
        pageX: "number",
        pageY: "number",
      },
      triggers: {
        power: "recalculate",
        band: "recalculate",
        dir: "recalculate",
        barColor: "recalculate",
        selectedBarColor: "recalculate",
        id: "recalculate",
        x: "recalculate",
        diagHeight: "recalculate",
        diagPadding: "recalculate",
        barSpacing: "recalculate",
        barWidth: "recalculate",
        mouseOver: "mouseOver",
        pageX: "mouseOver",
        pageY: "mouseOver",
      },
      updaters: {
        recalculate: function(attr){
          var x = attr.x,
            diagHeight = attr.diagHeight - attr.diagPadding[0] - attr.diagPadding[2];
          this.createSprites(attr);
          attr.power.forEach((value, index) => {
            // var randomValue = this.getRandomNumber();
            var barHeight = this.transformValue(attr.diagHeight, attr.diagPadding, value),
              y = diagHeight + attr.diagPadding[0] - barHeight,
              rect = this.rects[index],
              tooltip = this.tooltips[index];
            rect.setAttributes({
              x: x,
              y: y,
              value: value,
              height: barHeight,
              width: attr.barWidth,
            }, this);
            rect.setAnimation({
              duration: 500,
              easing: "easeInOut",
            });
            if(tooltip.isVisible()){
              var text = attr.band + rect.id + ", " + rect.attr.value+ "dBm" + (Ext.isEmpty(attr.dir) ? "" : ", " + attr.dir);
              tooltip.setHtml(text);
              tooltip.showAt(this.canvasToPageCoordinates(attr.x, y - 40));
            }
            x += attr.barWidth + attr.barSpacing;
          }, this);
          if(this.label){
            this.label.setAttributes({
              x: attr.x - 5,
              y: attr.diagHeight - attr.diagPadding[2],
              text: attr.band + attr.id,
              rotation: {
                degrees: -90,
                centerX: attr.x,
                centerY: attr.diagHeight - attr.diagPadding[2],
              },
            });
          }
        },
        mouseOver: function(attr){
          if(["all", "withoutTooltip"].includes(attr.mouseOver)){
            var selectedRect = this.rects[this.selectedRectIndex || 0],
              tooltip = this.tooltips[this.selectedRectIndex || 0],
              y = attr.diagHeight - attr.diagPadding[2] - this.transformValue(attr.diagHeight, attr.diagPadding, selectedRect.attr.value),
              text = attr.band + selectedRect.id + ", " + selectedRect.attr.value+ "dBm" + (Ext.isEmpty(attr.dir) ? "" : ", " + attr.dir);
            selectedRect.setAnimation({duration: 0});
            if(attr.mouseOver === "all"){
              tooltip.setHtml(text);
              tooltip.showAt(this.canvasToPageCoordinates(attr.x, y - 40));
            }
            selectedRect.setAttributes({
              fill: attr.selectedBarColor,
              lineWidth: 2,
            });
            this.label.setAttributes({
              scalingX: 1.2,
              scalingY: 1.2,
              fontWeight: "bold",
            });
          } else if(attr.mouseOver === "none"){
            this.tooltips.forEach(tooltip => {tooltip.hide()});
            this.rects.forEach(rect => {
              rect.setAttributes({
                lineWidth: 1,
                fill: attr.barColor, 
              })
            });
            this.label.setAttributes({
              scalingX: 1,
              scalingY: 1,
              fontWeight: "normal",
            });
          }
        },
      },
    },
  },
  createSprites: function(attr){
    if(!this.label){
      this.label = this.add({
        type: "text",
        fill: "black",
        textAlign: "end",
        textBaseline: "top",
      });
      this.rects = attr.power.map((power, index) => {
        return this.add({
          id: attr.id + "-" + index,
          type: "rect",
          fill: attr.barColor,
          strokeStyle: attr.barColor,
          lineWidth: 1,
        });
      });
      this.tooltips = attr.power.map(() => {
        return Ext.create("Ext.tip.ToolTip", {
          hidden: true,
          autoHide: false,
        });
      });
    }
  },
  hitTest: function(point){
    var x = point[0],
      y = point[1];

    this.selectedRectIndex = null;
    for(var i = 0; i < this.rects.length; i++){
      if(this.isOnSprite(this.rects[i].getBBox(), x, y)){
        this.selectedRectIndex = i;
        return {
          sprite: this,
        };
      }
      this.selectedRectIndex = null;
    }
    if(this.label && this.isOnSprite(this.label.getBBox(), x, y)){
      this.selectedRectIndex = 0;
      return {
        sprite: this,
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
  canvasToPageCoordinates: function(canvasX, canvasY){
    var canvas = this.getSurface().el.dom.querySelector("canvas"),
      rect = canvas.getBoundingClientRect(),
      scrollLeft = window.scrollX || document.documentElement.scrollLeft,
      scrollTop = window.scrollY || document.documentElement.scrollTop;
            
    return [
      canvasX + rect.left + scrollLeft,
      canvasY + rect.top + scrollTop,
    ];
  },
  transformValue(diagHeight, diagPadding, value){
    return (value + 62) * ((diagHeight - diagPadding[0] - diagPadding[2]) / 72);
  },
  // for testing purposes
  getRandomNumber: function(){
    return Math.floor(Math.random() * (10 - (-62) + 1)) + (-62);
  },
});