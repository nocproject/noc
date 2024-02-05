//---------------------------------------------------------------------
// NOC.core.Pointer
// Render SVG pointer for make connections
//---------------------------------------------------------------------
// Copyright (C) 2007-2023 The NOC Project
// See LICENSE for details
//---------------------------------------------------------------------
console.debug("Defining NOC.core.Pointer");

Ext.define("NOC.core.Pointer", {
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
                actualScale: "recalculate",
            },
            defaults: {
                arrowLength: 20,
                lineType: "line",
                arrowAngle: Math.PI / 8,
                actualScale: 1,
            },
            updaters: {
                recalculate: function(attr) {
                    var me = this,
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
                    var offset = (attr.side === "left" ? -50 : 50) * attr.actualScale,
                        baselinePath = Ext.String.format("M{0} {1} L{2} {3}", fromX, fromY, toX, toY),
                        arrowLeftPath = Ext.String.format("M{0} {1} L{2} {3}", toX, toY, mat.x(x, y), mat.y(x, y)),
                        arrowRightPath = Ext.String.format("M{0} {1} L{2} {3}", toX, toY, mat.x(x, -y), mat.y(x, -y));
                    if(attr.lineType === "path") {
                        var arrowX = (attr.side === "left" ? 1 : -1) * attr.arrowLength * cos(attr.arrowAngle) * attr.actualScale,
                            arrowY = attr.arrowLength * sin(attr.arrowAngle) * attr.actualScale;
                        baselinePath = Ext.String.format("M{0},{1} L{2},{3} L{4},{5} L{6},{7}",
                            fromX, fromY, fromX + offset, fromY, fromX + offset, toY, toX, toY);
                        arrowLeftPath = Ext.String.format("M{0} {1} L{2} {3}", toX, toY, toX - arrowX, toY + arrowY);
                        arrowRightPath = Ext.String.format("M{0} {1} L{2} {3}", toX, toY, toX - arrowX, toY - arrowY);
                    }
                    me.baseLine.setAttributes({
                        path: baselinePath,
                        strokeStyle: "black"
                    });
                    me.arrowLeft.setAttributes({
                        path: arrowLeftPath,
                        strokeStyle: attr.strokeStyle
                    });
                    me.arrowRight.setAttributes({
                        path: arrowRightPath,
                        strokeStyle: attr.strokeStyle
                    });
                },
            }
        }
    },
    createSprites: function() {
        var me = this;

        // Only create sprites if they haven't been created yet.
        if(!me.baseLine) {
            me.baseLine = me.add({
                type: "path",
                lineDash: [2, 2],
                // lineWidth: 2,
                // zIndex: 100
            });
            me.arrowLeft = me.add({
                type: "path"
            });
            me.arrowRight = me.add({
                type: "path"
            });
        }
    }
});