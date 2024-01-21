//---------------------------------------------------------------------
// NOC.core.ConnectionInternal
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
                labelAlign: "string",
                fromPort: "string",
                fromPortId: "string",
                toPortId: "string",
                toPort: "string",
                path: "string",
                toXY: "data",
                fromXY: "data",
                connectionColor: "string",
                fromHasArrow: "bool",
                toHasArrow: "bool",
                actualScale: "number"
            },
            triggers: {
                path: "recalculate",
                connectionColor: "recalculate",
            },
            defaults: {
                labelAlign: "left", // "left" | "right"
            },
            updaters: {
                recalculate: function(attr) {
                    var me = this;

                    me.createSprites(attr);
                    me.line.setAttributes({
                        labelAlign: attr.labelAlign,
                        fromPortId: attr.fromPortId,
                        toPortId: attr.toPortId,
                        connectionType: attr.connectionType,
                        path: attr.path,
                        strokeStyle: attr.connectionColor,
                        "marker-end": "url(#arrow)"
                    });

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
    hitTest: function(point, options) {
        var me = this,
            x = point[0],
            y = point[1];

        if(me.line.isPointInPath(x, y)) {
            return {
                sprite: me
            };
        }
        return null;
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
                me.toArrowMarker = me.add(me.getMarker("arrow", attr.labelAlign, attr.actualScale));
            }
            if(attr.fromHasArrow) {
                me.fromArrowMarker = me.add(me.getMarker("arrow", attr.labelAlign, attr.actualScale));
            }
        }
    },

    getMarker: function(id, labelAlign, scale) {
        var point1X = (labelAlign === "left" ? 1 : -1) * scale * 20,
            point1Y = (labelAlign === "left" ? 1 : -1) * scale * 7.5,
            path = Ext.String.format("M{0},{1} L{2},{3} L0,0 Z", point1X, point1Y, point1X, (-1) * point1Y);
        return {
            type: "path",
            id: id,
            fillStyle: "red",
            path: path,
            hidden: true,
        };
    }
});
