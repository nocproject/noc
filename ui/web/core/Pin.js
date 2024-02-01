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
                labelAlign: "string",
                remoteId: "string",
                remoteName: "string",
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
                scale: "number"
            },
            triggers: {
                pinColor: "recalculate",
                internalColor: "recalculate",
                isSelected: "recalculate",
                isInternalFixed: "recalculate",
                labelBold: "recalculate",
                pinName: "recalculate",
                labelAlign: "recalculate",
                remoteId: "recalculate",
                remoteName: "recalculate",
                allowInternal: "recalculate",
                enabled: "recalculate",
                internalEnabled: "recalculate",
                x: "translate",
                y: "translate",
                scale: "rescale"
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
                scale: 1
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
                    if(me.internal) {
                        me.internal.setAttributes({
                            fillStyle: attr.internalColor,
                            stroke: attr.isSelected && attr.isInternalFixed ? "lightgreen" : "black",
                            lineWidth: attr.isSelected && attr.isInternalFixed ? 3 : 1
                        });
                    }
                    me.label.setAttributes({
                        text: attr.pinName,
                        textAlign: attr.labelAlign === "left" ? "end" : "start",
                        fontWeight: fontWeight,
                        fontFamily: me.defaultConfig.fontFamily,
                        fontSize: me.defaultConfig.fontSize,
                    });
                },
                translate: function(attr) {
                    var me = this;

                    me.createSprites();
                    me.box.setAttributes({
                        translationX: attr.x,
                        translationY: attr.y
                    });
                    if(me.internal) {
                        me.internal.setAttributes({
                            translationX: ((me.attr.labelAlign === "left" ? 2.25 : -1.25) * me.getBoxWidth()) + attr.x,
                            translationY: attr.y + me.getBoxHeight() / 2
                        });
                    }
                    me.label.setAttributes({
                        translationX: ((me.attr.labelAlign === "left" ? -0.25 : 1.25) * me.getBoxWidth()) + attr.x,
                        translationY: attr.y - me.getBoxHeight() / 2
                    });
                },
                rescale: function(attr) {
                    var me = this;

                    me.createSprites();
                    me.box.setAnimation({
                        duration: 200,
                        easing: "easeInOut"
                    });
                    me.box.setAttributes({
                        scalingX: attr.scale,
                        scalingY: attr.scale
                    });
                    me.label.setAttributes({
                        scalingX: attr.scale,
                        scalingY: attr.scale
                    });
                    if(me.internal) {
                        me.internal.setAttributes({
                            scalingX: attr.scale,
                            scalingY: attr.scale
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
        // pinName: "Undefined",
        // pinColor: "#2c3e50",
        // labelAlign: "left",
        // allowInternal: false,
    },
    hitTest: function(point, options) {
        // Removed the isVisible check since pin will always be visible.
        var bbox, me = this,
            x = point[0],
            y = point[1];
        if(me.internal) {
            bbox = me.internal.getBBox();
            if(bbox && x >= bbox.x && x <= (bbox.x + bbox.width) && y >= bbox.y && y <= (bbox.y + bbox.height)) {
                me.setAttributes({cursorOn: "internal"});
                return {
                    sprite: me
                }
            }
        }
        bbox = me.box.getBBox();
        if(bbox && x >= bbox.x && x <= (bbox.x + bbox.width) && y >= bbox.y && y <= (bbox.y + bbox.height)) {
            me.setAttributes({cursorOn: "external"});
            return {
                sprite: me
            };
        }
        return null;
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
            me.label = me.add({
                type: "text",
                fontFamily: me.getFontFamily(),
                fontWeight: me.getFontWeight(),
                fontSize: me.getFontSize(),
                textBaseline: "middle",
                x: 0,
                y: me.box.height / 2
            });
            if(me.allowInternal) {
                me.internal = me.add({
                    type: "circle",
                    radius: me.getBoxWidth() / 2,
                    stroke: "black",
                    lineWidth: 2
                });
            }
        }
    }
});
