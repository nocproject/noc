//---------------------------------------------------------------------
// NOC.core.PinInternal
// Render SVG pin internal image
//---------------------------------------------------------------------
// Copyright (C) 2007-2023 The NOC Project
// See LICENSE for details
//---------------------------------------------------------------------
console.debug("Defining NOC.core.PinInternal");

Ext.define("NOC.core.PinInternal", {
    extend: "Ext.draw.sprite.Composite",
    alias: "sprite.pininternal",
    inheritableStatics: {
        def: {
            processors: {
                pinColor: "string",
                pinName: "string",
                labelAlign: "string",
                remoteId: "string",
                remoteName: "string",
                isSelected: "bool",
                labelBold: "bool",
                enabled: "bool",
                x: "number",
                y: "number",
                scale: "number"
            },
            triggers: {
                pinColor: "recalculate",
                pinName: "recalculate",
                labelAlign: "recalculate",
                remoteId: "recalculate",
                remoteName: "recalculate",
                isSelected: "recalculate",
                labelBold: "recalculate",
                x: "translate",
                y: "translate",
                scale: "rescale"
            },
            defaults: {
                pinColor: "#2c3e50",
                pinName: "Undefined",
                remoteId: "none",
                remoteName: "none",
                isSelected: false,
                labelBold: false,
                enabled: true,
                labelAlign: "left", // "left" | "right"
                scale: 1
            },
            updaters: {
                recalculate: function(attr) {
                    var me = this, fontWeight = (attr.isSelected || attr.labelBold) ? "bold" : "normal";

                    me.createSprites();
                    me.box.setAttributes({
                        fillStyle: attr.pinColor,
                        stroke: attr.isSelected ? "lightgreen" : "black",
                        lineWidth: attr.isSelected ? 3 : 1
                    });
                    me.label.setAttributes({
                        text: attr.pinName,
                        textAlign: attr.labelAlign === "left" ? "end" : "start",
                        fontWeight: fontWeight
                    });
                },
                translate: function(attr) {
                    var me = this;

                    me.createSprites();
                    me.box.setAttributes({
                        translationX: attr.x,
                        translationY: attr.y
                    });
                    me.label.attr.x = me.attr.labelAlign === "left" ? -10 : me.getBoxWidth() + 10
                    me.label.setAttributes({
                        translationX: attr.x,
                        translationY: attr.y
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
                }
            }
        }
    },
    config: {
        boxWidth: 15,
        boxHeight: 15,
        fontSize: 12,
    },
    hitTest: function(point, options) {
        // Removed the isVisible check since pin will always be visible.
        var me = this,
            x = point[0],
            y = point[1],
            bbox = me.getBBox(),
            isBBoxHit = bbox && x >= bbox.x && x <= (bbox.x + bbox.width) && y >= bbox.y && y <= (bbox.y + bbox.height);

        if(isBBoxHit) {
            return {
                sprite: this
            };
        }
        return null;
    },
    createSprites: function() {
        var me = this;

        console.log()
        if(!me.box) {
            me.box = me.add({
                type: "circle",
                radius: me.getBoxWidth() / 2,
                stroke: "black",
                lineWidth: 2
            });
            me.label = me.add({
                type: "text",
                fontFamily: "arial",
                fontWeight: "normal",
                fontSize: me.getFontSize(),
                textBaseline: "middle",
                x: 0,
                y: me.box.height / 2
            });
        }
    }
});
