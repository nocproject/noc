//---------------------------------------------------------------------
// NOC.core.Pin
// Render SVG pin image
//---------------------------------------------------------------------
// Copyright (C) 2007-2020 The NOC Project
// See LICENSE for details
//---------------------------------------------------------------------
console.debug("Defining NOC.core.Pin");

Ext.define("NOC.core.Pin", {
    extend: "Ext.draw.sprite.Composite",
    alias: "sprite.pin",
    inheritableStatics: {
        def: {
            processors: {
                pinColor: "string",
                internalColor: "string",
                pinName: "string",
                pinNameWidth: "number",
                labelAlign: "string",
                internalLabelWidth: "number",
                hasInternalLabel: "bool",
                remoteId: "string",
                remoteName: "string",
                side: "string",
                isSelected: "bool",
                isInternalFixed: "bool",
                cursorOn: "string",
                labelBold: "bool",
                enabled: "bool",
                pinOver: "bool",
                internalEnabled: "bool",
                allowInternal: "bool",
                x: "number",
                y: "number",
                actualScale: "number"
            },
            triggers: {
                pinColor: "recalculate",
                internalColor: "recalculate",
                isSelected: "recalculate",
                isInternalFixed: "recalculate",
                hasInternalLabel: "translate",
                labelBold: "recalculate",
                pinName: "recalculate",
                labelAlign: "recalculate",
                remoteId: "recalculate",
                remoteName: "recalculate",
                side: "recalculate",
                allowInternal: "recalculate",
                enabled: "recalculate",
                internalEnabled: "recalculate",
                x: "translate",
                y: "translate",
                actualScale: "rescale"
            },
            defaults: {
                pinColor: "#2c3e50",
                internalColor: "#2c3e50",
                pinName: "Undefined",
                remoteId: "none",
                remoteName: "none",
                isSelected: false,
                isInternalFixed: false,
                labelBold: false,
                enabled: true,
                internalEnabled: true,
                allowInternal: false,
                side: "left",
                labelAlign: "right", // "left" | "right"
                internalLabelWidth: 10,
                hasInternalLabel: false,
                actualScale: 1
            },
            updaters: {
                recalculate: function(attr) {
                    var me = this, fontWeight = (attr.isSelected || attr.labelBold) ? "bold" : "normal";

                    me.createSprites();
                    me.box.setAttributes({
                        fillStyle: attr.pinColor,
                        stroke: attr.isSelected && !attr.isInternalFixed ? "lightgreen" : "black",
                        lineWidth: attr.isSelected && !attr.isInternalFixed ? 3 : 1
                    });
                    me.pinNameWidth = me.measureText(attr.pinName);
                    me.label.setAttributes({
                        text: attr.pinName,
                        fontWeight: fontWeight,
                        textAlign: attr.labelAlign === "left" ? "end" : "start",
                    });
                    if(me.internal) {
                        me.internal.setAttributes({
                            fillStyle: attr.internalColor,
                            stroke: attr.isSelected && attr.isInternalFixed ? "lightgreen" : "black",
                            lineWidth: attr.isSelected && attr.isInternalFixed ? 3 : 1
                        });
                    }
                },
                translate: function(attr) {
                    var me = this;

                    me.createSprites();
                    me.box.setAttributes({
                        translationX: attr.x,
                        translationY: attr.y
                    });
                    if(me.internal) {
                        var internalCirclePadding = me.getBoxWidth() * (attr.side === "left" ? -1 : 2);

                        if(attr.hasInternalLabel) {
                            internalCirclePadding = me.getBoxWidth() * (attr.side === "left" ? 0 : 1);
                        }
                        me.internal.setAttributes({
                            translationX: attr.x + (attr.hasInternalLabel ? attr.internalLabelWidth : 0) + internalCirclePadding,
                            translationY: attr.y + me.getBoxHeight() / 2
                        });
                    }
                    me.label.setAttributes({
                        translationX: ((me.attr.labelAlign === "left" ? -0.25 : 1.25) * me.getBoxWidth()) + attr.x,
                        translationY: attr.y,
                    });
                    me.labelBackground.setAttributes({
                        translationX: (me.attr.side === "left" ? me.getBoxWidth() + 1 : - me.getBoxWidth() - me.pinNameWidth - 1) + attr.x,
                        translationY: attr.y,
                        height: me.getBoxHeight(),
                        width: me.pinNameWidth + (me.side === "left" ? 1 : 1) * me.getBoxWidth(),
                    })
                },
                rescale: function(attr) {
                    var me = this;

                    me.createSprites();
                    me.box.setAnimation({
                        duration: 200,
                        easing: "easeInOut"
                    });
                    me.box.setAttributes({
                        scalingX: attr.actualScale,
                        scalingY: attr.actualScale
                    });
                    me.label.setAttributes({
                        scalingX: attr.actualScale,
                        scalingY: attr.actualScale
                    });
                    if(me.internal) {
                        me.internal.setAttributes({
                            scalingX: attr.actualScale,
                            scalingY: attr.actualScale
                        });
                    }
                }
            }
        }
    },
    config: {
        boxWidth: 15,
        boxHeight: 15,
        fontSize: 12,
        fontFamily: "arial",
        fontWeight: "normal",
    },
    hitTest: function(point, options) {
        // Removed the isVisible check since pin will always be visible.
        var me = this,
            x = point[0],
            y = point[1];
        if(me.internal) {
            if(me.isOnSprite(me.internal.getBBox(), x, y, "internal")) {
                return {
                    sprite: me
                };
            }
        }
        if(me.isOnSprite(me.box.getBBox(), x, y, "wire")) {
            return {
                sprite: me
            };
        }
        if(me.isOnSprite(me.label.getBBox(), x, y, "wire")) {
            return {
                sprite: me
            };
        }

        return null;
    },
    isOnSprite: function(bbox, x, y, on) {
        var me = this;

        if(bbox && x >= bbox.x && x <= (bbox.x + bbox.width) && y >= bbox.y && y <= (bbox.y + bbox.height)) {
            me.setAttributes({cursorOn: on});
            return true;
        }
        return false;
    },
    createSprites: function() {
        var me = this;

        if(!me.box) {
            me.box = me.add({
                type: "rect",
                width: me.getBoxWidth(),
                height: me.getBoxHeight(),
                stroke: "black",
                lineWidth: 2
            });
            me.labelBackground = me.add({
                type: "rect",
                fill: "white",
                // zIndex: 200,
            })
            me.label = me.add({
                type: "text",
                fontFamily: me.getFontFamily(),
                fontWeight: me.getFontWeight(),
                fontSize: me.getFontSize(),
                textBaseline: "middle",
                x: 0,
                y: me.box.height / 2,
                // zIndex: 250,
            });
            if(me.allowInternal) {
                me.internal = me.add({
                    type: "circle",
                    radius: me.getBoxWidth() / 2,
                    stroke: "black",
                    lineWidth: 2,
                    x: 0,
                    y: 0
                });
            }
        }
    },
    measureText: function(text) {
        var me = this,
            font = Ext.String.format("{0} {1}px {2}", me.getFontWeight(), me.getFontSize(), me.getFontFamily());
        return Ext.draw.TextMeasurer.measureText(text, font).width;
    }
});
