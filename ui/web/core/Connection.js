//---------------------------------------------------------------------
// NOC.core.Connection
// Render SVG connection
//---------------------------------------------------------------------
// Copyright (C) 2007-2023 The NOC Project
// See LICENSE for details
//---------------------------------------------------------------------
console.debug("Defining NOC.core.Connection");

Ext.define("NOC.core.Connection", {
    extend: "Ext.draw.sprite.Composite",
    alias: "sprite.connection",
    inheritableStatics: {
        def: {
            processors: {
                connectionType: "string",
                side: "string",
                fromPortId: "string",
                fromPort: "string",
                fromXY: "data",
                fromHasArrow: "bool",
                fromDiscriminator: "string",
                fromSide: "string",
                toPortId: "string",
                toPort: "string",
                toXY: "data",
                toHasArrow: "bool",
                toDiscriminator: "string",
                toSide: "string",
                offset: "data",
                isDeleted: "bool",
                discriminatorWidth: "number",
                gainDb: "number",
                actualScale: "number",
                trace: "number",
                path: "string",
                connectionColor: "string",
                length: "number",
            },
            triggers: {
                path: "recalculate",
                connectionColor: "recalculate",
                fromDiscriminator: "recalculate",
                toDiscriminator: "recalculate",
                discriminatorWidth: "recalculate",
            },
            defaults: {
                side: "left", // "left" | "right"
            },
            updaters: {
                recalculate: function(attr) {
                    var me = this,
                        path = attr.path;

                    me.createSprites(attr);
                    if(attr.connectionType === "wire") {
                        path = Ext.String.format("M{0},{1} L{2},{3} L{4},{5} L{6},{7}",
                            attr.fromXY[0], attr.fromXY[1],
                            attr.fromXY[0] + attr.offset[0], attr.fromXY[1],
                            attr.toXY[0] - attr.offset[1], attr.toXY[1],
                            attr.toXY[0], attr.toXY[1]);
                    }
                    if(attr.connectionType === "loopback") {
                        path = Ext.String.format("M{0},{1} L{2},{3} L{4},{5} L{6},{7}",
                            attr.fromXY[0], attr.fromXY[1],
                            attr.fromXY[0] + (attr.fromSide === "left" ? attr.offset[0] : -1 * attr.offset[1]), attr.fromXY[1],
                            attr.fromXY[0] + (attr.fromSide === "left" ? attr.offset[0] : -1 * attr.offset[1]), attr.toXY[1],
                            attr.toXY[0], attr.toXY[1]);
                    }
                    me.line.setAttributes({
                        side: attr.side,
                        fromPortId: attr.fromPortId,
                        toPortId: attr.toPortId,
                        connectionType: attr.connectionType,
                        path: path,
                        strokeStyle: attr.connectionColor,
                        zIndex: attr.zIndex,
                        "marker-end": "url(#arrow)"
                    });

                    if(!Ext.isEmpty(attr.fromDiscriminator)) {
                        me.fromDiscriminator.setAttributes({
                            text: me.makeEllipses(attr.fromDiscriminator, attr.discriminatorWidth),
                            textAlign: attr.side === "left" ? "start" : "end",
                            translationX: parseFloat(attr.fromXY[0], 10) + me.getBoxWidth() * (attr.side === "left" ? 1 : -1),
                            translationY: parseFloat(attr.fromXY[1], 10),
                        });
                        if(!me.fromDiscriminatorTooltip && me.measureText(attr.fromDiscriminator) > me.measureText(me.fromDiscriminator.attr.text)) {
                            me.fromDiscriminatorTooltip = Ext.create("Ext.tip.ToolTip", {
                                html: attr.fromDiscriminator,
                                hidden: true
                            });
                        }
                    }
                    if(!Ext.isEmpty(attr.toDiscriminator)) {
                        me.toDiscriminator.setAttributes({
                            text: me.makeEllipses(attr.toDiscriminator, attr.discriminatorWidth),
                            textAlign: attr.side === "left" ? "start" : "end",
                            translationX: parseFloat(attr.toXY[0], 10) + me.getBoxWidth() * (attr.side === "left" ? 1 : -1),
                            translationY: parseFloat(attr.toXY[1], 10),
                        });
                        if(!me.toDiscriminatorTooltip && me.measureText(attr.toDiscriminator) > me.measureText(me.toDiscriminator.attr.text)) {
                            me.toDiscriminatorTooltip = Ext.create("Ext.tip.ToolTip", {
                                html: attr.toDiscriminator,
                                hidden: true
                            });
                        }
                    }
                    if(me.toArrowMarker) {
                        me.toArrowMarker.setAttributes({
                            translationX: parseFloat(attr.toXY[0], 10),
                            translationY: parseFloat(attr.toXY[1], 10),
                            zIndex: 100,
                            hidden: false
                        });
                    }
                    if(me.fromArrowMarker) {
                        me.fromArrowMarker.setAttributes({
                            translationX: parseFloat(attr.fromXY[0], 10),
                            translationY: parseFloat(attr.fromXY[1], 10),
                            zIndex: 100,
                            hidden: false
                        });
                    }
                },
            }
        }
    },
    config: {
        boxWidth: 15,
        boxHeight: 15,
        fontSize: 10,
        fontFamily: "arial",
        fontWeight: "normal",
    },
    hitTest: function(point, options) {
        var me = this,
            x = point[0],
            y = point[1];

        if(me.line.isPointInPath(x, y)) {
            return {
                sprite: me
            };
        }

        if(me.toDiscriminator) {
            if(me.isOnSprite(me.toDiscriminator.getBBox(), x, y)) {
                return {
                    sprite: me
                };
            }
        }
        if(me.fromDiscriminator) {
            if(me.isOnSprite(me.fromDiscriminator.getBBox(), x, y)) {
                return {
                    sprite: me
                };
            }
        }
        return null;
    },
    isOnSprite: function(bbox, x, y) {
        var me = this;

        if(bbox && x >= bbox.x && x <= (bbox.x + bbox.width) && y >= bbox.y && y <= (bbox.y + bbox.height)) {
            return true;
        }
        return false;
    },
    createSprites: function(attr) {
        var me = this;

        if(!me.line) {
            me.line = me.add({
                type: "path",
                lineWidth: 2,
                zIndex: 100,
            });
            if(attr.toHasArrow) {
                me.toArrowMarker = me.add(me.getMarker("arrow", attr.side, attr.actualScale));
            }
            if(attr.fromHasArrow) {
                me.fromArrowMarker = me.add(me.getMarker("arrow", attr.side, attr.actualScale));
            }
            if(attr.toDiscriminator) {
                me.toDiscriminator = me.add({
                    type: "text",
                    fontFamily: me.getFontFamily(),
                    fontWeight: me.getFontWeight(),
                    fontSize: me.getFontSize(),
                    textBaseline: "middle",
                });
            }
            if(attr.fromDiscriminator) {
                me.fromDiscriminator = me.add({
                    type: "text",
                    fontFamily: me.getFontFamily(),
                    fontWeight: me.getFontWeight(),
                    fontSize: me.getFontSize(),
                    textBaseline: "middle",
                });
            }
        }
    },
    getMarker: function(id, side, scale) {
        var point1X = (side === "left" ? -1 : 1) * scale * 20,
            point1Y = (side === "left" ? -1 : 1) * scale * 7.5,
            path = Ext.String.format("M{0},{1} L{2},{3} L0,0 Z", point1X, point1Y, point1X, (-1) * point1Y);
        return {
            type: "path",
            id: id,
            fillStyle: "red",
            path: path,
            hidden: true,
        };
    },
    makeEllipses: function(text, reservedWidth) {
        var me = this,
            width = me.measureText(text),
            suffix = "...",
            reservedWidth = Math.abs(reservedWidth) - me.getBoxWidth() * 1.1;

        if(reservedWidth > 0 && width > reservedWidth) {
            if(!me.internalLabelTooltip) {
                me.internalLabelTooltip = Ext.create("Ext.tip.ToolTip", {
                    html: me.fullInternalLabel,
                    hidden: true
                });
            }
            while(width > reservedWidth) {
                text = text.slice(0, -1);
                width = me.measureText(text + suffix);
            }
            text += suffix;
        }
        return text;
    },
    measureText: function(text) {
        var me = this,
            font = Ext.String.format("{0} {1}px {2}", me.getFontWeight(), me.getFontSize(), me.getFontFamily());
        return Ext.draw.TextMeasurer.measureText(text, font).width;
    }
});
