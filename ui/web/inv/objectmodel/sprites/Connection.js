//---------------------------------------------------------------------
// NOC.inv.objectmodel.sprites.Connection
// Render SVG pin image
//---------------------------------------------------------------------
// Copyright (C) 2007-2024 The NOC Project
// See LICENSE for details
//---------------------------------------------------------------------
console.debug("Defining NOC.inv.objectmodel.sprites.Connection");

Ext.define("NOC.inv.objectmodel.sprites.Connection", {
    extend: "Ext.draw.sprite.Composite",
    alias: "sprite.cross_connection",
    inheritableStatics: {
        def: {
            processors: {
                path: "string",
                pathType: "string",
                indexes: "data",
                offsetsX: "data",
                inputId: "string",
                outputId: "string",
                discriminators: "data",
                discriminatorsLength: "data",
                fontFamily: "string",
                fontSize: "string",
                isSelected: "bool",
                startXY: "data",
                toXY: "data",
                pinRadius: "number",
                scaleFactor: "number",
            },
            triggers: {
                path: "recalculate",
                inputId: "recalculate",
                outputId: "recalculate",
                isSelected: "recalculate",
                toXY: "recalculate",
                scaleFactor: "recalculate",
            },
            defaults: {
            },
            updaters: {
                recalculate: function(attr) {
                    var me = this;

                    me.createSprites(attr);
                    me.line.setAttributes({
                        strokeStyle: attr.isSelected ? me.getSelectedColor() : me.getAvailableColor(),
                        lineWidth: attr.isSelected ? 4 : 2,
                    });
                },
            },
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
        if(me.line.isPointOnPath(x, y)) {
            return me;
        }
        return null;
    },
    createSprites: function(attr) {
        var me = this,
            path, secondPointXY, thirdPointXY;

        if(!me.line) {
            me.inputId = attr.inputId;
            me.outputId = attr.outputId;

            switch(attr.pathType) {
                case "inputMany": {
                    secondPointXY = [attr.startXY[0] + attr.pinRadius * (attr.indexes[0] + 3) + attr.discriminatorsLength[0], attr.startXY[1]];
                    thirdPointXY = [secondPointXY[0], attr.toXY[1]];
                    path = Ext.String.format("M{0},{1} L{2},{3} L{4},{5} L{6},{7}",
                        attr.startXY[0], attr.startXY[1],
                        secondPointXY[0], secondPointXY[1],
                        thirdPointXY[0], thirdPointXY[1],
                        attr.toXY[0], attr.toXY[1]);
                    break;
                }
                case "outputMany": {
                    secondPointXY = [attr.toXY[0] - attr.pinRadius * (attr.indexes[0] + 3) - attr.discriminatorsLength[1], attr.startXY[1]];
                    thirdPointXY = [secondPointXY[0], attr.toXY[1]];
                    path = Ext.String.format("M{0},{1} L{2},{3} L{4},{5} L{6},{7}",
                        attr.startXY[0], attr.startXY[1],
                        secondPointXY[0], secondPointXY[1],
                        thirdPointXY[0], thirdPointXY[1],
                        attr.toXY[0], attr.toXY[1]);
                    break;
                }
                case "single": {
                    path = Ext.String.format("M{0},{1} L{2},{3}", attr.startXY[0], attr.startXY[1], attr.toXY[0], attr.toXY[1]);
                    break;
                }
            }

            me.line = me.add({
                type: "path",
                path: path,
                strokeStyle: me.getAvailableColor(),
                lineWidth: 2,
            });
            // input
            me.arrow = me.add(me.getMarker("arrow", attr.toXY, attr.pinRadius * 2));
            if(attr.discriminators[0]) {
                me.inputDiscriminator = me.add({
                    type: "text",
                    text: attr.discriminators[0],
                    fontFamily: attr.fontFamily,
                    fontWeight: "normal",
                    fontSize: attr.fontSize,
                    textBaseline: "middle",
                    textAlign: "start",
                    x: attr.startXY[0] + attr.pinRadius * 2,
                    y: attr.startXY[1] - attr.pinRadius,
                });
            }
            // output
            if(attr.discriminators[1]) {
                me.outputDiscriminator = me.add({
                    type: "text",
                    text: attr.discriminators[1],
                    fontFamily: attr.fontFamily,
                    fontWeight: "normal",
                    fontSize: attr.fontSize,
                    textBaseline: "middle",
                    textAlign: "end",
                    x: attr.toXY[0] - attr.pinRadius * 2.5,
                    y: attr.toXY[1] - attr.pinRadius,
                });
            }
        }
    },
    getMarker: function(id, pointXY, length) {
        var
            // length = 18 * (scale || 1),
            // width = 5.5 * (scale || 1),
            width = length / 3,
            path = Ext.String.format("M{0},{1} L{2},{3} L{4},{5} Z",
                pointXY[0], pointXY[1],
                pointXY[0] - length, pointXY[1] + width,
                pointXY[0] - length, pointXY[1] - width
            );

        return {
            type: "path",
            id: id,
            fillStyle: "red",
            x: pointXY[0],
            y: pointXY[1],
            path: path,
            hidden: false,
        };
    },
});