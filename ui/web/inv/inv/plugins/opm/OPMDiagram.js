//---------------------------------------------------------------------
// inv.inv OPM Diagram
//---------------------------------------------------------------------
// Copyright (C) 2007-2025 The NOC Project
// See LICENSE for details
//---------------------------------------------------------------------
console.debug("Defining NOC.inv.inv.plugins.opm.OPMDiagram");

Ext.define("NOC.inv.inv.plugins.opm.OPMDiagram", {
  extend: "Ext.draw.Container",
  xtype: "opm.diagram",
  alias: "widget.spectrogram",
  scrollable: "x",

  config: {
    diagPadding: 35,
    barSpacing: 2,
    maxBarWidth: 20,
    data: [],
  },

  draw: function(data, band, isReload){
    var surface = this.getSurface(),
      padding = this.getDiagPadding(),
      barSpacing = this.getBarSpacing(),
      maxBarWidth = this.getMaxBarWidth(),
      width = this.getWidth() - padding * 2,
      height = this.getHeight() - padding * 2,
      numChannels = data.reduce((acc, channel) => acc + channel.power.length, 0),
      barWidth = Math.min(maxBarWidth, (width - (numChannels - 1) * barSpacing) / numChannels),
      x = padding;
    console.log(isReload);
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
      powerValues.forEach(value => {
        var barHeight = (value + 62) * (height / 72);
        surface.add({
          type: "rect",
          x: x,
          y: height + padding - barHeight,
          width: barWidth,
          height: barHeight,
          fill: "blue",
        });
        x += barWidth + barSpacing;
      });
    });

    this.yAxis();
    surface.renderFrame();
  },

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
});