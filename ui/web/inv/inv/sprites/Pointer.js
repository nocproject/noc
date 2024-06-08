//---------------------------------------------------------------------
// NOC.inv.inv.sprites.Pointer
// Render SVG pointer for make connections
//---------------------------------------------------------------------
// Copyright (C) 2007-2024 The NOC Project
// See LICENSE for details
//---------------------------------------------------------------------
console.debug("Defining NOC.inv.inv.sprites.Pointer");

Ext.define("NOC.inv.inv.sprites.Pointer", {
  extend: "Ext.draw.sprite.Composite",
  alias: "sprite.pointer",

  inheritableStatics: {
    def: {
      processors: {
        fromX: "number",
        fromY: "number",
        toX: "number",
        toY: "number",
        arrowLength: "number",
        arrowAngle: "number",
        lineType: "string",
        side: "string",
        xOffsets: "data",
        actualScale: "number",
      },
      triggers: {
        fromX: "recalculate",
        fromY: "recalculate",
        toX: "recalculate",
        toY: "recalculate",
        arrowLength: "recalculate",
        arrowAngle: "recalculate",
        lineType: "recalculate",
        xOffsets: "recalculate",
        actualScale: "recalculate",
      },
      defaults: {
        arrowLength: 20,
        lineType: "line",
        arrowAngle: Math.PI / 8,
        actualScale: 1,
      },
      updaters: {
        recalculate: function(attr){
          var arrowX, arrowY,
            me = this,
            fromX = attr.fromX,
            fromY = attr.fromY,
            toX = attr.toX,
            toY = attr.toY,
            dx = toX - fromX,
            dy = toY - fromY,
            alpha = Math.atan2(dy, dx),
            sin = Math.sin,
            cos = Math.cos,
            beta = Math.PI - attr.arrowAngle,
            x = attr.arrowLength * cos(beta) * attr.actualScale,
            y = attr.arrowLength * sin(beta) * attr.actualScale,
            mat = Ext.draw.Matrix.fly([cos(alpha), sin(alpha), -sin(alpha), cos(alpha), toX, toY]);

          me.createSprites();
          var offset = me.getBoxWidth() * (attr.side === "left" ? (-4) : 4),
            baselinePath = Ext.String.format("M{0} {1} L{2} {3}", fromX, fromY, toX, toY),
            arrowLeftPath = Ext.String.format("M{0} {1} L{2} {3}", toX, toY, mat.x(x, y), mat.y(x, y)),
            arrowRightPath = Ext.String.format("M{0} {1} L{2} {3}", toX, toY, mat.x(x, -y), mat.y(x, -y));

          if(attr.lineType === "internal"){
            arrowX = (attr.side === "left" ? 1 : -1) * attr.arrowLength * cos(attr.arrowAngle) * attr.actualScale;
            arrowY = attr.arrowLength * sin(attr.arrowAngle) * attr.actualScale;

            baselinePath = Ext.String.format("M{0},{1} L{2},{3} L{4},{5} L{6},{7}",
                                             fromX, fromY, fromX + offset, fromY, fromX + offset, toY, toX, toY);
            arrowLeftPath = Ext.String.format("M{0} {1} L{2} {3}", toX, toY, toX - arrowX, toY + arrowY);
            arrowRightPath = Ext.String.format("M{0} {1} L{2} {3}", toX, toY, toX - arrowX, toY - arrowY);
          }
          if(attr.lineType === "wire"){
            arrowX = (attr.side === "left" ? -1 : 1) * attr.arrowLength * cos(attr.arrowAngle) * attr.actualScale;
            arrowY = attr.arrowLength * sin(attr.arrowAngle) * attr.actualScale;

            offset = attr.xOffsets || [offset, offset];
            baselinePath = Ext.String.format("M{0},{1} L{2},{3} L{4},{5} L{6},{7}",
                                             fromX, fromY, fromX + (attr.side === "left" ? -1 : 1) * offset[0], fromY, toX + (attr.side === "left" ? 1 : -1) * offset[1], toY, toX, toY);
            arrowLeftPath = Ext.String.format("M{0} {1} L{2} {3}", toX, toY, toX - arrowX, toY + arrowY);
            arrowRightPath = Ext.String.format("M{0} {1} L{2} {3}", toX, toY, toX - arrowX, toY - arrowY);
          }
          if(attr.lineType === "loopback"){
            arrowX = (attr.side === "left" ? -1 : 1) * attr.arrowLength * cos(attr.arrowAngle) * attr.actualScale;
            arrowY = attr.arrowLength * sin(attr.arrowAngle) * attr.actualScale;

            offset = attr.xOffsets || [offset, offset];
            baselinePath = Ext.String.format("M{0},{1} L{2},{3} L{4},{5} L{6},{7}",
                                             fromX, fromY, fromX + (attr.side === "left" ? 1 : -1) * offset[0], fromY, fromX + (attr.side === "left" ? 1 : -1) * offset[0], toY, toX, toY);
            arrowLeftPath = Ext.String.format("M{0} {1} L{2} {3}", toX, toY, toX - arrowX, toY + arrowY);
            arrowRightPath = Ext.String.format("M{0} {1} L{2} {3}", toX, toY, toX - arrowX, toY - arrowY);
          }
          me.baseLine.setAttributes({
            path: baselinePath,
            strokeStyle: "black",
          });
          me.arrowLeft.setAttributes({
            path: arrowLeftPath,
            strokeStyle: attr.strokeStyle,
          });
          me.arrowRight.setAttributes({
            path: arrowRightPath,
            strokeStyle: attr.strokeStyle,
          });
        },
      },
    },
  },
  config: {
    boxWidth: 15,
    boxHeight: 15,
    xLabelOffsets: [0, 0],
  },
  createSprites: function(){
    var me = this;

    // Only create sprites if they haven't been created yet.
    if(!me.baseLine){
      me.baseLine = me.add({
        type: "path",
        lineDash: [8, 8],
        lineWidth: 2,
      });
      me.arrowLeft = me.add({
        type: "path",
        lineWidth: 2,
      });
      me.arrowRight = me.add({
        type: "path",
        lineWidth: 2,
      });
    }
  },
});