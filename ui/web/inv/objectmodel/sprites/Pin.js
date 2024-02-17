//---------------------------------------------------------------------
// NOC.inv.objectmodel.sprites.Pin
// Render SVG pin image
//---------------------------------------------------------------------
// Copyright (C) 2007-2024 The NOC Project
// See LICENSE for details
//---------------------------------------------------------------------
console.debug("Defining NOC.inv.objectmodel.sprites.Pin");

Ext.define("NOC.inv.objectmodel.sprites.Pin", {
    extend: "Ext.draw.sprite.Composite",
    alias: "sprite.cross_pin",
    inheritableStatics: {
        def: {
            processors: {
                text: "string",
                textAlign: "string",
                fontSize: "number",
                radius: "number",
                isSelected: "bool",
                x: "number",
                y: "number",
            },
            triggers: {
                text: "recalculate",
                isSelected: "recalculate",
                textAlign: "recalculate",
                fontSize: "recalculate",
                radius: "recalculate",
                x: "recalculate",
                y: "recalculate",
            },
            defaults: {
                // radius: 7,
                // fontSize: 12,
            },
            updaters: {
                recalculate: function(attr, updated) {
                    var me = this;

                    me.createSprites(attr);
                    if(attr.isSelected) {
                        me.pin.setAttributes({
                            stroke: "lightgreen",
                            lineWidth: 3
                        });
                        me.label.setAttributes({
                            fontWeight: "bold",
                        });
                    } else {
                        me.pin.setAttributes({
                            stroke: me.getDisabledColor(),
                            lineWidth: 2
                        });
                        me.label.setAttributes({
                            fontWeight: "normal",
                        });
                    }
                },
            }
        },
    },
    config: {
        availableColor: "#1F6D91",
        newColor: "lightgreen",
        disabledColor: "#d0d0d0",
        selectedColor: "#f5d63c",
    },
    hitTest: function(point, options) {
        // Removed the isVisible check since pin will always be visible.
        var me = this,
            x = point[0],
            y = point[1];

        if(me.isOnSprite(me.pin.getBBox(), x, y)) {
            return me;
        }
        if(me.isOnSprite(me.label.getBBox(), x, y)) {
            return me;
        }

        return null;
    },
    isOnSprite: function(bbox, x, y) {
        if(bbox && x >= bbox.x && x <= (bbox.x + bbox.width) && y >= bbox.y && y <= (bbox.y + bbox.height)) {
            return true;
        }
        return false;
    },
    createSprites: function(attr) {
        var me = this;

        if(!me.pin) {
            me.pin = me.add({
                type: "circle",
                radius: attr.radius,
                stroke: "black",
                lineWidth: 2,
                x: attr.x,
                y: attr.y + attr.radius * 2,
            });

            me.label = me.add({
                type: "text",
                text: attr.text,
                fontFamily: attr.fontFamily || "arial",
                fontWeight: attr.fontWeight || "normal",
                fontSize: attr.fontSize,
                textBaseline: "middle",
                textAlign: attr.textAlign,
                x: attr.x + attr.radius * 1.5 * (attr.textAlign === "end" ? -1 : 1),
                y: attr.y + attr.radius * 2,
            });
        }
    },
});