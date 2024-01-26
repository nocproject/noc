//---------------------------------------------------------------------
// NOC.core.Pin
// Render SVG pointer for make connections
//---------------------------------------------------------------------
// Copyright (C) 2007-2023 The NOC Project
// See LICENSE for details
//---------------------------------------------------------------------
console.debug("Defining NOC.core.Pointer");

Ext.define("NOC.core.Pointer", {
    extend: 'Ext.draw.sprite.Composite',
    alias: 'sprite.pointer',

    inheritableStatics: {
        def: {
            processors: {
                fromX: "number",
                fromY: "number",
                toX: "number",
                toY: "number",
                arrowLength: 'number',
                arrowAngle: 'number',
            },
            triggers: {
                fromX: "recalculate1",
                fromY: "recalculate1",
                toX: "recalculate1",
                toY: "recalculate1",
                arrowLength: 'recalculate1',
                arrowAngle: 'recalculate1',
            },
            defaults: {
                arrowLength: 10,
                arrowAngle: Math.PI / 8
            },
            updaters: {
                recalculate1: function(attr) {
                    var me = this,
                        fromX = attr.fromX,
                        fromY = attr.fromY,
                        toX = attr.toX,
                        toY = attr.toY,
                        dx = toX - fromX,
                        dy = toY - fromY;
                    // if(dx === 0 || dy === 0) {
                    //     return;
                    // }

                    var alpha = Math.atan2(dy, dx),
                        sin = Math.sin,
                        cos = Math.cos,
                        beta = Math.PI - attr.arrowAngle,
                        x = attr.arrowLength * cos(beta),
                        y = attr.arrowLength * sin(beta),
                        mat = Ext.draw.Matrix.fly([cos(alpha), sin(alpha), -sin(alpha), cos(alpha), toX, toY]);

                    me.createSprites();
                    me.baseLine.setAttributes({
                        fromX: attr.fromX,
                        fromY: attr.fromY,
                        toX: attr.toX,
                        toY: attr.toY,
                    });
                    me.arrowLeft.setAttributes({
                        fromX: toX,
                        fromY: toY,
                        toX: mat.x(x, y),
                        toY: mat.y(x, y),
                        strokeStyle: attr.strokeStyle
                    });
                    me.arrowRight.setAttributes({
                        fromX: toX,
                        fromY: toY,
                        toX: mat.x(x, -y),
                        toY: mat.y(x, -y),
                        strokeStyle: attr.strokeStyle
                    });
                },
                recalculate: function(attr) {
                    var me = this,
                        fromX = attr.fromX,
                        fromY = attr.fromY,
                        toX = attr.toX,
                        toY = attr.toY,
                        dx = toX - fromX,
                        dy = toY - fromY,
                        PI = Math.PI,
                        radius = Math.sqrt(dx * dx + dy * dy);

                    if(dx === 0 || dy === 0) {
                        return;
                    }

                    var alpha = Math.atan2(dy, dx),
                        sin = Math.sin,
                        cos = Math.cos,
                        arcRadius = attr.arcRadius,
                        beta = PI - attr.arrowAngle,
                        x = attr.arrowLength * cos(beta),
                        y = attr.arrowLength * sin(beta),
                        // Coordinates of the arc arrow tip.
                        ax = arcRadius * cos(alpha) + fromX,
                        ay = arcRadius * sin(alpha) + fromY,
                        mat = Ext.draw.Matrix.fly([cos(alpha), sin(alpha), -sin(alpha), cos(alpha), toX, toY]),
                        angleArrowThreshold = Ext.draw.Draw.radian * me.getAngleArrowThreshold(),
                        isSmallAngle = alpha < angleArrowThreshold && alpha > -angleArrowThreshold,
                        angleTextRadius = arcRadius * 1.2,
                        isSmallRadius = radius < angleTextRadius,
                        radiusTextFlip, fontSize,
                        theta = 0;

                    if(alpha > 0) {
                        theta = alpha + PI / 2 - attr.arrowAngle / (arcRadius * 0.1);
                    } else if(alpha < 0) {
                        theta = alpha - PI / 2 + attr.arrowAngle / (arcRadius * 0.1);
                    }

                    me.createSprites();

                    me.baseLine.setAttributes({
                        fromX: fromX,
                        fromY: fromY,
                        toX: fromX + attr.baseLineLength,
                        toY: fromY,
                        hidden: isSmallRadius
                    });
                    me.radiusLine.setAttributes({
                        fromX: fromX,
                        fromY: fromY,
                        toX: toX,
                        toY: toY,
                        strokeStyle: attr.strokeStyle
                    });
                    me.radiusArrowLeft.setAttributes({
                        fromX: toX,
                        fromY: toY,
                        toX: mat.x(x, y),
                        toY: mat.y(x, y),
                        strokeStyle: attr.strokeStyle
                    });
                    me.radiusArrowRight.setAttributes({
                        fromX: toX,
                        fromY: toY,
                        toX: mat.x(x, -y),
                        toY: mat.y(x, -y),
                        strokeStyle: attr.strokeStyle
                    });

                    mat = Ext.draw.Matrix.fly([cos(theta), sin(theta), -sin(theta), cos(theta), ax, ay]);

                    me.angleLine.setAttributes({
                        startAngle: 0,
                        endAngle: alpha,
                        cx: fromX,
                        cy: fromY,
                        r: arcRadius,
                        anticlockwise: alpha < 0,
                        hidden: isSmallRadius
                    });
                    me.angleArrowLeft.setAttributes({
                        fromX: ax,
                        fromY: ay,
                        toX: mat.x(x, y),
                        toY: mat.y(x, y),
                        hidden: isSmallAngle || isSmallRadius
                    });
                    me.angleArrowRight.setAttributes({
                        fromX: ax,
                        fromY: ay,
                        toX: mat.x(x, -y),
                        toY: mat.y(x, -y),
                        hidden: isSmallAngle || isSmallRadius
                    });
                    me.angleText.setAttributes({
                        x: angleTextRadius * cos(alpha / 2) + fromX,
                        y: angleTextRadius * sin(alpha / 2) + fromY,
                        text: me.getAngleText() + ': ' + (alpha * 180 / PI).toFixed(me.getPrecision()) + '°',
                        hidden: isSmallRadius
                    });
                    radiusTextFlip = ((alpha > -0.5 * PI && alpha < 0.5 * PI) || (alpha > 1.5 * PI && alpha < 2 * PI)) ? 1 : -1;
                    fontSize = parseInt(me.radiusText.attr.fontSize, 10);
                    x = 0.5 * radius * cos(alpha) + fromX + radiusTextFlip * fontSize * sin(alpha);
                    y = 0.5 * radius * sin(alpha) + fromY - radiusTextFlip * fontSize * cos(alpha);
                    me.radiusText.setAttributes({
                        x: x,
                        y: y,
                        rotationRads: radiusTextFlip === 1 ? alpha : alpha - PI,
                        rotationCenterX: x,
                        rotationCenterY: y,
                        text: me.getRadiusText() + ': ' + radius.toFixed(me.getPrecision()),
                        hidden: isSmallRadius
                    });
                }
            }
        }
    },
    createSprites: function() {
        var me = this;

        // Only create sprites if they haven't been created yet.
        if(!me.baseLine) {
            me.baseLine = me.add({
                type: 'line',
                lineDash: [2, 2]
            });
            me.arrowLeft = me.add({
                type: 'line'
            });
            me.arrowRight = me.add({
                type: 'line'
            });
        }
    }

});