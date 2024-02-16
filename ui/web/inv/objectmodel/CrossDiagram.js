//---------------------------------------------------------------------
// inv.objectmodel Crossing diagram
//---------------------------------------------------------------------
// Copyright (C) 2007-2024 The NOC Project
// See LICENSE for details
//---------------------------------------------------------------------
console.debug("Defining NOC.inv.objectmodel.CrossDiagram");

Ext.define("NOC.inv.objectmodel.CrossDiagram", {
    extend: "Ext.draw.Container",
    alias: "widget.inv.crossdiagram",
    border: true,
    requires: [
        "NOC.inv.objectmodel.sprites.Connection",
        "NOC.inv.objectmodel.sprites.Label",
        "NOC.inv.objectmodel.sprites.Pin"
    ],
    /**
 * Draw a diagram based on the provided data and size.
 *
 * @param {Object} data - the data used to draw the diagram
 * @param {number[]} size - the [width, height] of the diagram in pixels
 * @return {void} 
 */
    drawDiagram: function(data, size) {
        var outputOffsetX, inputOffsetX,
            me = this,
            surface = me.getSurface(),
            inputPins = Ext.Array.unique(Ext.Array.map(data.cross || [], function(connection) {return connection.input})),
            outputPins = Ext.Array.unique(Ext.Array.map(data.cross || [], function(connection) {return connection.output})),
            maxPins = Ext.Array.max([inputPins.length, outputPins.length]),
            pinRadius = 8,
            gap = pinRadius * 2.5,
            inputOffsetY = (maxPins - inputPins.length) * gap / 2,
            outputOffsetY = (maxPins - outputPins.length) * gap / 2,
            topPadding = pinRadius,
            fontFamily = "arial",
            fontSize = pinRadius * 1.8,
            drawContainerHeight = topPadding + maxPins * gap,
            scale = size[1] / drawContainerHeight;

        pinRadius *= scale;
        gap *= scale;
        fontSize *= scale;
        inputOffsetY *= scale;
        outputOffsetY *= scale;
        outputOffsetX = size[0] - Ext.Array.max(Ext.Array.map(outputPins, function(pin) {return me.measureText(pin, fontSize, fontFamily);})) - pinRadius * 2;
        inputOffsetX = Ext.Array.max(Ext.Array.map(inputPins, function(pin) {return me.measureText(pin, fontSize, fontFamily);})) + pinRadius * 2;

        console.log(maxPins, inputOffsetX, outputOffsetX, inputOffsetY, outputOffsetY);
        // me.setWidth(size[0]);
        // me.setHeight(size[1]);
        // surface.add({
        // type: "rect",
        // x: 0,
        // y: 0,
        // width: size[0],
        // height: size[1],
        // stroke: "black",
        // });

        surface.removeAll(true);
        Ext.Array.each(inputPins, function(pin, i) {
            surface.add({
                type: "cross.pin",
                id: "input" + pin,
                radius: pinRadius,
                x: inputOffsetX,
                y: inputOffsetY + i * gap,
                fontFamily: fontFamily,
                fontSize: fontSize,
                text: pin,
                textAlign: "end",
            });
        });
        Ext.Array.each(outputPins, function(pin, i) {
            surface.add({
                type: "cross.pin",
                id: "output" + pin,
                radius: pinRadius,
                x: outputOffsetX,
                y: outputOffsetY + i * gap,
                fontFamily: fontFamily,
                fontSize: fontSize,
                text: pin,
                textAlign: "start",
            });
        });

        Ext.Array.each(data.cross || [], function(connection, i) {
            var inputSprite = surface.get("input" + connection.input),
                outputSprite = surface.get("output" + connection.output),
                path = Ext.String.format("M{0},{1} L{2},{3}", inputSprite.x, inputSprite.y + pinRadius * 2, outputSprite.x, outputSprite.y + pinRadius * 2);

            surface.add({
                type: "cross.connection",
                path: path,
            });
        });
        surface.renderFrame();
    },
    measureText: function(text, fontSize, fontFamily) {
        var me = this,
            font = Ext.String.format("{0} {1}px {2}", "normal", fontSize, fontFamily);
        return Ext.draw.TextMeasurer.measureText(text, font).width;
    }
});
