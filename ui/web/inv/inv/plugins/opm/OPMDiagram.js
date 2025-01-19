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
    "NOC.inv.inv.plugins.opm.OPMChannelSprite",
  ],
  xtype: "opm.diagram",
  alias: "widget.spectrogram",
  scrollable: false,
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
  draw: function(data, band){
    if(this.getSurface().getItems().length){
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
      minBarWidth = this.getMinBarWidth(),
      width = this.getWidth() - padding * 2,
      numChannels = data.reduce((acc, channel) => acc + channel.power.length, 0),
      barWidthTotal = (numChannels - 1) * barSpacing,
      barWidth = Math.max(minBarWidth, Math.min(maxBarWidth, (width - barWidthTotal) / numChannels)),
      requiredWidth = barWidth * numChannels + barWidthTotal + padding * 2,
      height = this.up().getHeight(),
      x = padding;

    this.getEl().dom.style.width = `${requiredWidth}px`;
    this.getEl().dom.style.height = `${height}px`;
    this.getSurface().setRect([0, 0, requiredWidth, height]);

    surface.removeAll();
    data.forEach(channel => {
      surface.add({
        type: "channel",
        x: x,
        power: channel.power,
        band: band,
        id: channel.ch,
        barWidth: barWidth,
        barSpacing: barSpacing,
        diagHeight: this.getHeight(),
        diagPadding: padding,
      });
      x += (barWidth + barSpacing) * channel.power.length;
    });
    this.yAxis();
    surface.renderFrame();
  },
  //
  updateBars: function(data){
    var surface = this.getSurface();
    data.forEach(channel => {
      var channelSprite = surface.get(channel.ch);
      if(channelSprite){
        channelSprite.setAttributes({
          power: channel.power,
        });
      }
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
  onSpriteMouseOver: function(el, event){
    console.log("Mouse over", el.sprite);
    if(el.sprite.type === "channel"){
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
    if(el.sprite.type === "channel"){
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