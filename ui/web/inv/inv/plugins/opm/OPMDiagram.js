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
    "NOC.inv.inv.plugins.opm.OPMLegendSprite",
  ],
  xtype: "opm.diagram",
  alias: "widget.spectrogram",
  scrollable: false,
  defaultListenerScope: true,
  colorList: {},
  colorIndex: 0,
  config: {
    diagPadding: "35 35 80 35", // top right bottom left
    barSpacing: 2,
    maxBarWidth: 20,
    minBarWidth: 5,
    defaultBarColor: "blue",
    barColors: ["#FF0000", "#FF4500", "#FF8C00", "#FFD700", "#ADFF2F", "#32CD32", "#008000", "#006400"],
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
      barSpacing = this.getBarSpacing(),
      maxBarWidth = this.getMaxBarWidth(),
      minBarWidth = this.getMinBarWidth(),
      diagWidth = this.getWidth() - this.getPaddingBySide("left") - this.getPaddingBySide("right"),
      numChannels = data.reduce((acc, channel) => acc + channel.power.length, 0),
      barSpacingTotal = (numChannels - 1) * barSpacing,
      barWidth = Math.max(minBarWidth, Math.min(maxBarWidth, (diagWidth - barSpacingTotal) / numChannels)),
      requiredWidth = barWidth * numChannels + barSpacingTotal + this.getPaddingBySide("left") + this.getPaddingBySide("right"), 
      height = this.up().getHeight(),
      x = this.getPaddingBySide("left");

    // Set the width and height of the diagram container
    this.getEl().dom.style.width = `${requiredWidth}px`;
    this.getEl().dom.style.height = `${height}px`;
    this.getSurface().setRect([0, 0, requiredWidth, height]);

    surface.removeAll();
    this.colorList = {};
    this.colorIndex = 0;
    data.forEach((channel) => {
      var barColor = this.mapColor(channel.dir),
        diagPadding = this.getDiagPadding().split(" ").map(value => parseInt(value, 10));
      surface.add({
        type: "channel",
        x: x,
        power: channel.power,
        band: band,
        dir: channel.dir,
        barColor: barColor,
        id: channel.ch,
        barWidth: barWidth,
        barSpacing: barSpacing,
        diagHeight: this.getHeight(),
        diagPadding: diagPadding,
      });
      x += (barWidth + barSpacing) * channel.power.length;
    });
    this.yAxis();
    surface.add({
      type: "legend",
      dirs: Ext.Object.getKeys(this.colorList),
      colors: Ext.Object.getValues(this.colorList),
      x: this.getPaddingBySide("left"),
      y: this.getHeight() - this.getPaddingBySide("bottom") + this.getPaddingBySide("top"),
      width: diagWidth,
    });
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
    var yAxisValues = [-62, -50, -40, -30, -20, -10, 0, 10],
      height = this.getHeight() - this.getPaddingBySide("top") - this.getPaddingBySide("bottom"),
      positionY = this.getHeight() - this.getPaddingBySide("bottom"),
      rangeWidth = height / (yAxisValues.length - 1),
      leftPadding = this.getPaddingBySide("left"),
      rightPadding = this.getPaddingBySide("right"),
      lineWidth = this.getWidth() - rightPadding,
      surface = this.getSurface();
    
    yAxisValues.forEach(function(value){
      surface.add({
        type: "line",
        fromX: leftPadding, 
        fromY: positionY,
        toX: lineWidth,
        toY: positionY,
        stroke: "gray",
        lineWidth: 1,
      });

      surface.add({
        type: "text",
        x: leftPadding - 10,
        y: positionY,
        text: value.toString(),
        fill: "black",
        textAlign: "right",
        textBaseline: "middle",
      });

      positionY -= rangeWidth;
    });
  },
  //
  onSpriteMouseOver: function(el, event){
    console.log("Mouse over", el.sprite);
    if(el.sprite.type === "channel"){
      el.sprite.setAttributes({
        mouseOver: "all",
        pageX: event.pageX,
        pageY: event.pageY,
      });
      this.getSurface().renderFrame();
    } else if(el.sprite.type === "legend"){
      this.getSurface().getItems()
        .filter(sprite => sprite.dir === el.sprite.dir)
        .forEach(sprite => sprite.setAttributes({
          mouseOver: "withoutTooltip",
          pageX: event.pageX,
          pageY: event.pageY,
        }));
      el.sprite.setAttributes({
        mouseOver: true,
        dir: el.sprite.dir,
      });
      this.getSurface().renderFrame();
    }
  },
  //
  onSpriteMouseOut: function(el){
    console.log("Mouse out", el.sprite);
    if(el.sprite.type === "channel"){
      el.sprite.setAttributes({
        mouseOver: "none",
      });
      this.getSurface().renderFrame();
    } else if(el.sprite.type === "legend"){
      this.getSurface().getItems()
      .filter(sprite => sprite.dir === el.sprite.dir)
      .forEach(sprite => sprite.setAttributes({
        mouseOver: "none",
      }));
      el.sprite.setAttributes({
        mouseOver: false,
        dir: el.sprite.dir,
      });
      this.getSurface().renderFrame();
    }
  },
  //
  onSpriteClick: function(sprite){
    console.log("Mouse click", sprite);
  },
  //
  mapColor: function(output){
    var colors = this.getBarColors();
    if(Ext.isEmpty(output)) return this.getDefaultBarColor();
    
    if(Ext.isEmpty(this.colorList[output])){
      this.colorList[output] = colors[this.colorIndex % colors.length];
      this.colorIndex = (this.colorIndex + 1) % colors.length;
    }
    return this.colorList[output];
  },
  //
  getPaddingBySide: function(side){
    var padding = this.getDiagPadding().split(" ");
    if(side === "top") return parseInt(padding[0], 10);
    if(side === "right") return parseInt(padding[1], 10) 
    if(side === "bottom") return parseInt(padding[2], 10)
    if(side === "left") return parseInt(padding[3], 10);
    return 0;
  },
});