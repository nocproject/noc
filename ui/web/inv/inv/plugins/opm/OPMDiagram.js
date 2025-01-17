//---------------------------------------------------------------------
// inv.inv OPM Diagram
//---------------------------------------------------------------------
// Copyright (C) 2007-2025 The NOC Project
// See LICENSE for details
//---------------------------------------------------------------------
console.debug("Defining NOC.inv.inv.plugins.opm.OPMDiagram");

Ext.define("NOC.inv.inv.plugins.opm.OPMDiagram", {
  extend: "Ext.draw.Container",
  requires: [
    "NOC.inv.inv.plugins.opm.Bar",
  ],
  xtype: "opm.diagram",
  alias: "widget.spectrogram",
  scrollable: "x",
  defaultListenerScope: true,
  config: {
    diagPadding: 35,
    barSpacing: 2,
    maxBarWidth: 20,
    minBarWidth: 5,
    data: [],
  },
  plugins: ["spriteevents"],
  listeners: {
    spritemouseover: "onSpriteMouseOver",
    spritemouseout: "onSpriteMouseOut",
    spriteclick: "onSpriteClick",
  },
  //
  draw: function(data, band, isReload){
    if(isReload){
      this.updateBars(data);
    } else{
      this.createBars(data, band);
    }
  },
  //
  createBars: function(data, band){
    var surface = this.getSurface(),
      padding = this.getDiagPadding(),
      barSpacing = this.getBarSpacing(),
      maxBarWidth = this.getMaxBarWidth(),
      // minBarWidth = this.getMinBarWidth(),
      width = this.getWidth() - padding * 2,
      height = this.getHeight() - padding * 2,
      numChannels = data.reduce((acc, channel) => acc + channel.power.length, 0),
      barWidth = Math.min(maxBarWidth, (width - (numChannels - 1) * barSpacing) / numChannels),
      // barWidth = Math.max(minBarWidth, 
      // Math.min(maxBarWidth, 
      //  (width - (numChannels - 1) * barSpacing) / numChannels)),
      // requiredWidth = requiredWidth = barWidth * numChannels + (numChannels - 1) * barSpacing + padding * 2,
      x = padding;
    surface.removeAll();
    data.forEach(channel => {
      var powerValues = channel.power;
      surface.add({
        type: "text",
        x: x,
        y: height + padding * 1.3,
        text: band + channel.ch.toString(),
        fill: "black",
        textAlign: "start",
        textBaseline: "top",
        rotation: {
          degrees: -90,
        },
      });
      powerValues.forEach((value, index) => {
        var barHeight = this.transformValue(value);
        surface.add({
          id: channel.ch + "-" + index,
          type: "bar",
          x: x,
          y: height + padding - barHeight,
          width: barWidth,
          height: barHeight,
          value: value,
          name: band + channel.ch,
        });
        x += barWidth + barSpacing;
      });
    });
    this.yAxis();
    surface.renderFrame();
  },
  //
  updateBars: function(data){
    var surface = this.getSurface(),
      padding = this.getDiagPadding(),
      height = this.getHeight() - padding * 2;
    data.forEach(channel => {
      var powerValues = channel.power;
      powerValues.forEach((value, index) => {
        var bar = surface.get(channel.ch + "-" + index);
        if(bar){
          var barHeight = this.transformValue(value);
          bar.setAttributes({
            y: height + padding - barHeight,
            value: value,
            height: barHeight,
          });
        }
      });
    });
    surface.renderFrame();
  },
  //
  yAxis: function(){
    var yAxisValues = [10, 0, -10, -20, -30, -40, -50, -62],
      padding = this.getDiagPadding(),
      height = this.getHeight() - padding * 2,
      width = this.getWidth() - padding,
      positionY = padding,
      rangeWidth = height / (yAxisValues.length - 1),
      surface = this.getSurface();
    
    yAxisValues.forEach(function(value){
      surface.add({
        type: "line",
        fromX: padding,
        fromY: positionY,
        toX: width,
        toY: positionY,
        stroke: "gray",
        lineWidth: 1,
      });

      surface.add({
        type: "text",
        x: padding - 10,
        y: positionY,
        text: value.toString(),
        fill: "black",
        textAlign: "right",
        textBaseline: "middle",
      });

      positionY += rangeWidth;
    });
  },
  //
  transformValue(value){
    return (value + 62) * ((this.getHeight() - this.getDiagPadding() * 2) / 72);
  },
  //
  onSpriteMouseOver: function(el, event){
    console.log("Mouse over", el.sprite);
    if(el.sprite.type === "bar"){
      el.sprite.setAttributes({
        mouseOver: true,
        pageX: event.pageX,
        pageY: event.pageY,
      });
      this.getSurface().renderFrame();
    }
  },
  //
  onSpriteMouseOut: function(el){
    console.log("Mouse out", el.sprite);
    if(el.sprite.type === "bar"){
      el.sprite.setAttributes({
        mouseOver: false,
      });
      this.getSurface().renderFrame();
    }
  },
  //
  onSpriteClick: function(sprite){
    console.log("Mouse click", sprite);
  },
});