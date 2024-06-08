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
    plugins: ["spriteevents"],
    listeners: {
        spritemouseover: "onSpriteMouseOver",
        spritemouseout: "onSpriteMouseOut",
    },
    /**
 * Draw a diagram based on the provided data and size.
 *
 * @param {Object} data - the data used to draw the diagram
 * @param {number[]} size - the [width, height] of the diagram in pixels
 * @return {void} 
 */
    drawDiagram: function(data, size) {
        var outputOffsetX, inputOffsetX,
            groupBy = (array, key) => array.reduce((result, item) => {
                (result[item[key]] = result[item[key]] || []).push(item);
                return result;
            }, {}),
            sortGroups = (groups, sortBy) => {
                return Object.values(groups)
                    .filter(group => group.length > 1)
                    .map(group => group.sort((a, b) => a[sortBy].localeCompare(b[sortBy])))
                    .sort((a, b) => b.length - a.length);
            },
            me = this,

            groupedByOutput = groupBy(data.cross, 'output'),
            outputGroups = sortGroups(groupedByOutput, 'input'),
            groupedByInput = groupBy(data.cross, 'input'),
            inputGroups = sortGroups(groupedByInput, 'output'),
            remainingItems = [data.cross.filter(item =>
                !outputGroups.some(group => group.includes(item)) &&
                !inputGroups.some(group => group.includes(item))
            ).sort((a, b) => a.input.localeCompare(b.input))],

            surface = me.getSurface(),
            inputPins = Ext.Array.unique(Ext.Array.map(data.cross || [], function(connection) {return connection.input})),
            outputPins = Ext.Array.unique(Ext.Array.map(data.cross || [], function(connection) {return connection.output})),
            // maxPins = Ext.Array.reduce([...outputGroups, ...inputGroups, ...remainingItems],
            //     function(prev, group) {
            //         console.log(group);
            //         var inputPins = Ext.Array.unique(Ext.Array.map(group || [], function(connection) {return connection.input})),
            //             outputPins = Ext.Array.unique(Ext.Array.map(group || [], function(connection) {return connection.output})),
            //             value = Ext.Array.max([inputPins.length, outputPins.length]);
            //         return prev + value
            //     }, 0),
            // maxPins = Ext.Array.max([inputPins.length, outputPins.length]),
            maxPins = data.cross.length,
            pinRadius = 8,
            gap = pinRadius * 2.5,
            // by vertical center
            // inputOffsetY = (maxPins - inputPins.length) * gap / 2,
            // outputOffsetY = (maxPins - outputPins.length) * gap / 2,
            inputOffsetY = 0,
            outputOffsetY = 0,
            filledPinRow = 0,
            topPadding = pinRadius,
            fontFamily = "arial",
            pinFontSize = pinRadius * 1.8,
            discriminatorFontSize = pinRadius * 1.4,
            drawContainerHeight = topPadding + maxPins * gap,
            scale = size[1] / drawContainerHeight;

        pinRadius *= scale;
        gap *= scale;
        pinFontSize = Math.round(scale * pinFontSize);
        discriminatorFontSize = Math.round(scale * discriminatorFontSize);
        inputOffsetY *= scale;
        outputOffsetY *= scale;

        outputOffsetX = size[0] - Ext.Array.max(Ext.Array.map(outputPins, function(pin) {return me.measureText(pin, pinFontSize, fontFamily);})) - pinRadius * 2;
        inputOffsetX = Ext.Array.max(Ext.Array.map(inputPins, function(pin) {return me.measureText(pin, pinFontSize, fontFamily);})) + pinRadius * 2;
        inputDiscriminatorLength = Ext.Array.max(Ext.Array.map(data.cross, function(connection) {return me.measureText(connection.input_discriminator, discriminatorFontSize, fontFamily);})) + pinRadius * 0;
        outputDiscriminatorLength = Ext.Array.max(Ext.Array.map(data.cross, function(connection) {return me.measureText(connection.output_discriminator, discriminatorFontSize, fontFamily);})) + pinRadius * 0;
        outputGroups = Ext.Array.map(outputGroups, function(group) {
            return Ext.apply(group, {
                type: "inputMany"
            });
        });
        inputGroups = Ext.Array.map(inputGroups, function(group) {
            return Ext.apply(group, {
                type: "outputMany"
            });
        });
        remainingItems = Ext.Array.map(remainingItems, function(group) {
            return Ext.apply(group, {
                type: "single"
            });
        });

        surface.removeAll(true);
        Ext.Array.each([...outputGroups, ...inputGroups, ...remainingItems], function(group, i, allGroups) {
            var inputPins = Ext.Array.unique(Ext.Array.map(group || [], function(connection) {return connection.input})),
                outputPins = Ext.Array.unique(Ext.Array.map(group || [], function(connection) {return connection.output})),
                inputOffsetY = filledPinRow * gap;
            outputOffsetY = filledPinRow * gap;

            Ext.Array.each(inputPins, function(pin, j) {
                surface.add({
                    type: "cross_pin",
                    id: "input" + pin,
                    radius: pinRadius,
                    x: inputOffsetX,
                    y: inputOffsetY + j * gap,
                    fontFamily: fontFamily,
                    fontSize: pinFontSize,
                    text: pin,
                    textAlign: "end",
                });
            });
            Ext.Array.each(outputPins, function(pin, j) {
                surface.add({
                    type: "cross_pin",
                    id: "output" + pin,
                    radius: pinRadius,
                    x: outputOffsetX,
                    y: outputOffsetY + j * gap,
                    fontFamily: fontFamily,
                    fontSize: pinFontSize,
                    text: pin,
                    textAlign: "start",
                });
            });
            //
            filledPinRow += Ext.Array.max([inputPins.length, outputPins.length]);
            //
            Ext.Array.each(group, function(connection, j) {
                var inputSprite = surface.get("input" + connection.input),
                    outputSprite = surface.get("output" + connection.output),
                    startXY = [inputSprite.x, inputSprite.y + pinRadius * 2],
                    endXY = [outputSprite.x, outputSprite.y + pinRadius * 2];

                surface.add({
                    type: "cross_connection",
                    pathType: group.type,
                    indexes: [j, group.length],
                    inputId: inputSprite.id,
                    outputId: outputSprite.id,
                    startXY: startXY,
                    toXY: endXY,
                    fontFamily: fontFamily,
                    fontSize: discriminatorFontSize,
                    pinRadius: pinRadius,
                    discriminators: [connection.input_discriminator, connection.output_discriminator],
                    discriminatorsLength: [inputDiscriminatorLength, outputDiscriminatorLength],
                    offsetsX: [inputOffsetX, outputOffsetX],
                    scaleFactor: scale,
                });
            });
        });
        surface.renderFrame();
    },
    onSpriteMouseOver: function(sprite) {
        switch(sprite.type) {
            case "cross_connection": {
                var inputSprite = sprite.getSurface().get(sprite.inputId),
                    outputSprite = sprite.getSurface().get(sprite.outputId);

                this.unselectAllConnections();

                Ext.Array.each([inputSprite, outputSprite, sprite], function(s) {
                    s.setAttributes({
                        isSelected: true,
                    });
                });
                break;
            }
            case "cross_pin": {
                var connections = Ext.Array.filter(sprite.getSurface().getItems(),
                    function(s) {
                        return s.type === "cross_connection" && (s.outputId === sprite.id || s.inputId === sprite.id)
                    });

                Ext.Array.each([sprite, ...connections], function(s) {
                    s.setAttributes({
                        isSelected: true,
                        zIndex: 50,
                    });
                });
                break;
            }
        }
        this.getSurface().renderFrame();
    },
    onSpriteMouseOut: function(sprite) {
        switch(sprite.type) {
            case "cross_connection": {
                var inputSprite = sprite.getSurface().get(sprite.inputId),
                    outputSprite = sprite.getSurface().get(sprite.outputId);

                Ext.Array.each([inputSprite, outputSprite, sprite], function(s) {
                    s.setAttributes({
                        isSelected: false,
                    });
                });
                break;
            }
            case "cross_pin": {
                var connections = Ext.Array.filter(sprite.getSurface().getItems(),
                    function(s) {
                        return s.type === "cross_connection" && (s.outputId === sprite.id || s.inputId === sprite.id)
                    });

                Ext.Array.each([sprite, ...connections], function(s) {
                    s.setAttributes({
                        isSelected: false,
                    });
                });
                break;
            }
        }
        this.getSurface().renderFrame();
    },
    measureText: function(text, fontSize, fontFamily) {
        var font = Ext.String.format("{0} {1}px {2}", "normal", fontSize, fontFamily);

        if(Ext.isEmpty(text)) {
            return 0;
        }
        return Ext.draw.TextMeasurer.measureText(text, font).width;
    },
    selectConnection: function(record) {
        var input = record.get("input"),
            output = record.get("output");

        this.unselectAllConnections();
        Ext.Array.each(
            Ext.Array.filter(this.getSurface().getItems(),
                function(sprite) {return sprite.type === "cross_connection" && sprite.inputId === "input" + input && sprite.outputId === "output" + output}),
            function(connectionSprite) {connectionSprite.setAttributes({isSelected: true})}
        );
        this.getSurface().renderFrame();
    },
    unselectAllConnections: function() {
        var connections = Ext.Array.filter(this.getSurface().getItems(),
            function(sprite) {
                return sprite.type === "cross_connection"
            });

        Ext.Array.each(connections, function(connectionSprite) {
            connectionSprite.setAttributes({isSelected: false});
        });
    }
});
