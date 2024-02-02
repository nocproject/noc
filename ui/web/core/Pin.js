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
                internalLabel: "string",
                internalLabelWidth: "number",
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
                actualScale: "number"
            },
            triggers: {
                pinColor: "recalculate",
                internalColor: "recalculate",
                isSelected: "recalculate",
                isInternalFixed: "recalculate",
                labelBold: "recalculate",
                pinName: "recalculate",
                internalLabel: "recalculate",
                labelAlign: "recalculate",
                remoteId: "recalculate",
                remoteName: "recalculate",
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
                    me.label.setAttributes({
                        text: attr.pinName,
                        textAlign: attr.labelAlign === "left" ? "end" : "start",
                    });
                    if(me.internal) {
                        me.internal.setAttributes({
                            fillStyle: attr.internalColor,
                            stroke: attr.isSelected && attr.isInternalFixed ? "lightgreen" : "black",
                            lineWidth: attr.isSelected && attr.isInternalFixed ? 3 : 1
                        });
                        if(attr.internalLabel) {
                            var font = Ext.String.format("{0} {1}px {2}", me.getFontWeight(), me.getFontSize(), me.getFontFamily()),
                                width = Ext.draw.TextMeasurer.measureText(attr.internalLabel, font).width,
                                suffix = "...",
                                text = attr.internalLabel;

                            if(width > Math.abs(attr.internalLabelWidth)) {
                                me.fullInternalLabel = attr.internalLabel;
                                if(!me.internalLabelTooltip) {
                                    me.internalLabelTooltip = Ext.create("Ext.tip.ToolTip", {
                                        html: me.fullInternalLabel,
                                        hidden: true
                                    });
                                }
                                while(width > Math.abs(attr.internalLabelWidth)) {
                                    text = text.slice(0, -1);
                                    width = Ext.draw.TextMeasurer.measureText(text + suffix, font).width;
                                }
                                text += suffix;
                            }
                            me.internalLabel.setAttributes({
                                text: text,
                                textAlign: attr.labelAlign === "left" ? "start" : "end",
                            });
                        }
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
                        me.internal.setAttributes({
                            translationX: ((me.attr.labelAlign === "left" ? 2.25 : -1.25) * me.getBoxWidth()) + attr.x,
                            translationY: attr.y + me.getBoxHeight() / 2
                        });
                        me.internalLabel.setAttributes({
                            translationX: attr.x + (me.attr.labelAlign === "left" ? me.box.width * 1.5 : 0),
                            translationY: attr.y + me.getBoxHeight() / 2,
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
                    lineWidth: 2,
                    x: me.internalLabelWidth,
                    y: 0
                });
                me.internalLabel = me.add({
                    type: "text",
                    fontFamily: me.getFontFamily(),
                    fontWeight: me.getFontWeight(),
                    fontSize: me.getFontSize(),
                    textBaseline: "middle",
                });
            }
        }
    }
});
