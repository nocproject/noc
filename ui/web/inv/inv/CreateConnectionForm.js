//---------------------------------------------------------------------
// inv.inv CreateConnection form
//---------------------------------------------------------------------
// Copyright (C) 2007-2020 The NOC Project
// See LICENSE for details
//---------------------------------------------------------------------
console.debug("Defining NOC.inv.inv.CreateConnectionForm");

Ext.define("NOC.inv.inv.CreateConnectionForm", {
    extend: "Ext.panel.Panel",
    alias: "widget.inv.connectionform",
    region: "center",
    layout: "fit",
    border: false,
    scrollable: true,
    app: null,
    itemId: "invConnectionForm",
    AVAILABLE_COLOR: "#2c3e50",
    OCCUPIED_COLOR: "lightgray",
    INVALID_COLOR: "lightcoral",
    WIRE_COLOR: "#1F6D91",
    DISABLED_WIRE_COLOR: "#d0d0d0",
    SELECTED_WIRE_COLOR: "#f5d63c",
    boxWidth: 20,
    boxHeight: 20,
    schemaPadding: 60, // boxHeight * 3,
    gap: 12.5,
    scale: 1,
    discriminatorWidth: {left: -150, right: 150},
    legendHeight: 20,
    firstTrace: 3,
    requires: [
        "NOC.core.Body",
        "NOC.core.ComboBox",
        "NOC.core.Connection",
        "NOC.core.Label",
        "NOC.core.Pin",
        "NOC.core.Pointer"
    ],
    viewModel: {
        data: {
            leftObject: null,
            rightObject: null,
            side: null,
            selectedPin: null,
            selectedPinId: null,
            isSelectedPinInternal: null,
        },
        formulas: {
            isValid: function(get) {
                return get("leftSelectedPin") && get("rightSelectedPin");
            }
        }
    },
    initComponent: function() {
        var me = this;

        me.drawPanel = Ext.create({
            xtype: "draw",
            itemId: "canvas",
            region: "center",
            scrollable: false,
            isModalOpen: false, // mouseOut check position when modal window is open
            wire: {
                connectionColor: me.WIRE_COLOR,
                lineWidth: 2,
            },
            disabledWire: {
                connectionColor: me.DISABLED_WIRE_COLOR,
                lineWidth: 2,
            },
            selectedWire: {
                connectionColor: me.SELECTED_WIRE_COLOR,
                lineWidth: 4,
            },
            sprites: [],
            listeners: {
                spritemouseover: me.onSpriteMouseOver,
                spritemouseout: me.onSpriteMouseOut,
                spriteclick: me.onSpriteClick,
                scope: me,
                afterrender: function(container) {
                    container.getEl().on("keydown", me.cancelDrawConnection);
                    container.getEl().set({
                        tabIndex: 0,
                        focusable: true
                    });
                    container.getEl().focus();
                }
            },
            plugins: ["spriteevents"]
        });
        me.cableCombo = Ext.create({
            xtype: "combo",
            fieldLabel: __("Cable"),
            labelAlign: "right",
            labelWidth: 50,
            width: 400,
            editable: false,
            queryMode: "local",
            displayField: "name",
            valueField: "name",
            store: {
                fields: ["name", "available"],
                data: []
            },
            bind: {
                disabled: "{!leftObject}",
                value: "{cable}"
            },
            listeners: {
                scope: me,
                change: me.load
            }
        });
        Ext.apply(me, {
            title: __("Object connections"),
            titleAlign: "center",
            items: [
                me.drawPanel
            ],
            listeners: {
                element: "el",
                scope: me,
                mousemove: this.onMouseMove,
            },
            tbar: [
                {
                    text: __("Close"),
                    scope: me,
                    glyph: NOC.glyph.arrow_left,
                    handler: me.onPressClose
                },
                {
                    glyph: NOC.glyph.eraser,
                    scope: me,
                    handler: me.onCleanClick,
                    tooltip: __("Clear objects"),
                    bind: {
                        disabled: "{!leftObject}"
                    }
                },
                {
                    glyph: NOC.glyph.refresh,
                    scope: me,
                    handler: me.onReload,
                    tooltip: __("Repaint"),
                    bind: {
                        disabled: "{!leftObject}"
                    }
                },
                me.cableCombo,
                "->",
                {
                    text: __("Connect"),
                    scope: me,
                    bind: {
                        disabled: "{!isValid}"
                    },
                    handler: me.onConnectClick
                }
            ],
        });
        me.callParent();
    },
    load: function() {
        var params, title,
            me = this,
            cable = me.cableCombo.getValue(),
            // leftSelected = mainPanel.getViewModel().get("leftSelectedPin"),
            // rightSelected = mainPanel.getViewModel().get("rightSelectedPin"),
            leftObject = me.getViewModel().get("leftObject"),
            rightObject = me.getViewModel().get("rightObject");

        title = leftObject.get("name") + " <==> " + (rightObject ? rightObject.get("name") : __("none"));
        me.setTitle(title);
        params = "o1=" + leftObject.get("id") + (rightObject ? "&o2=" + rightObject.get("id") : "");
        // params += leftSelected ? "&left_filter=" + leftSelected : "";
        // params += rightSelected ? "&right_filter=" + rightSelected : "";
        params += cable ? "&cable_filter=" + cable : "";
        me.mask(__("Loading..."));
        Ext.Ajax.request({
            url: "/inv/inv/crossing_proposals/?" + params,
            method: "GET",
            success: function(response) {
                var drawPanel = me.drawPanel,
                    mainSurface = drawPanel.getSurface(),
                    data = Ext.decode(response.responseText);

                me.maxPins = Math.max(data.left.connections.length, data.right.connections.length);
                me.unmask();
                NOC.msg.complete(__("The data was successfully loaded"));
                mainSurface.removeAll(true);
                me.cableCombo.getStore().loadData(data.cable);
                me.scaleCalculate();
                Ext.Array.each(["left", "right"], function(side) {
                    if(data[side].connections && data[side].connections.length) {
                        var hasDiscriminator = me.hasDiscriminator(data[side].internal_connections);

                        me.drawObject(data[side].connections, mainSurface, side, hasDiscriminator, me.maxPins);
                        me.drawInternalConnections(data[side], drawPanel.getSurface(side + "_internal_conn"), side, hasDiscriminator);
                    }
                });
                me.drawWires(data.wires, mainSurface);
                // workaround zIndex, redraw labels and set zIndex to 60
                me.reDrawLabels(mainSurface);
                me.drawLegend(mainSurface);
                console.log("renderFrame: load");
                mainSurface.renderFrame();
            },
            failure: function() {
                me.unmask();
                NOC.msg.failed(__("Error loading data"));
            }
        });
    },
    drawObject: function(pins, surface, side, hasDiscriminator) {
        var me = this;

        surface.add(me.makePins(pins, side, hasDiscriminator));
        surface.add(me.makeBody(pins, side));
    },
    drawInternalConnections: function(data, surface, side) {
        var me = this;
        // surface => (left|right) + _internal_conn
        surface.removeAll(true);
        surface.add(me.makeInternalConnections(data.internal_connections, side));
        console.log("renderFrame: drawInternalConnections");
        surface.renderFrame();
    },
    drawLegend: function(surface) {
        surface.add(this.makeLegend(__("Free and valid slot"), this.AVAILABLE_COLOR, 2.5, this.surfaceHeight));
        surface.add(this.makeLegend(__("Occupied slot"), this.OCCUPIED_COLOR, 250, this.surfaceHeight));
        surface.add(this.makeLegend(__("Invalid slot"), this.INVALID_COLOR, 500, this.surfaceHeight));
    },
    drawWires: function(wires, surface) {
        var me = this;

        Ext.each(surface.getItems(), function(wire) {
            if(wire.type === "connection" && wire.connectType === "wire") {
                wire.remove();
            }
        });
        surface.add(me.makeWires(wires));
        console.log("renderFrame: drawWire");
        surface.renderFrame();
    },
    reDrawLabels: function(surface) {
        Ext.Array.each(
            Ext.Array.filter(surface.getItems(), function(sprite) {return sprite.type === "pin"}),
            function(pin) {
                surface.add({
                    type: "label",
                    id: "label" + pin.id,
                    pinId: pin.id,
                    backgroundFill: pin.labelBackground.fill,
                    backgroundTranslationX: pin.labelBackground.attr.translationX,
                    backgroundTranslationY: pin.labelBackground.attr.translationY,
                    backgroundWidth: pin.labelBackground.attr.width,
                    backgroundHeight: pin.labelBackground.attr.height,
                    labelFontFamily: pin.label.attr.fontFamily,
                    labelFontWeight: pin.label.attr.fontWeight,
                    labelFontSize: pin.label.attr.fontSize,
                    labelTextBaseline: pin.label.attr.textBaseline,
                    labelTextAlign: pin.label.attr.textAlign,
                    labelText: pin.label.attr.text,
                    labelX: pin.label.attr.x,
                    labelY: pin.label.attr.y,
                    labelTranslationX: pin.label.attr.translationX,
                    labelTranslationY: pin.label.attr.translationY,
                    zIndex: 60
                });
            });
    },
    makeWires: function(wires) {
        var me = this,
            mainSurface = me.drawPanel.getSurface(),
            offsetX = me.getWiresOffset("left", "right");
        return Ext.Array.map(wires, function(wire) {

            return me.makeWire(mainSurface.get(wire[0].id), mainSurface.get(wire[1].id), wire[0].side, wire[1].side, offsetX[0], offsetX[1]);
        });
    },
    makeWire: function(firstPort, secondPort, firstSide, secondSide, firstOffset, secondOffset) {
        return {
            type: "connection",
            connectionType: firstSide === secondSide ? "loopback" : "wire",
            fromPortId: firstPort.id,
            toPortId: secondPort.id,
            fromXY: [firstPort.x + firstPort.box.width / 2, firstPort.y + firstPort.box.height / 2],
            toXY: [secondPort.x + secondPort.box.width / 2, secondPort.y + secondPort.box.height / 2],
            fromSide: firstSide,
            toSide: secondSide,
            offset: [firstOffset, secondOffset],
            connectionColor: this.WIRE_COLOR,
            zIndex: 50,
        };
    },
    makePins: function(pins, side, hasDiscriminator) {
        var me = this,
            xOffset = me.xOffset(side, pins),
            selectedPin = me.getViewModel().get("selectedPin"),
            labelAlign = side === "left" ? "right" : "left",
            sprites = [];

        Ext.each(pins, function(port, index) {
            var pinColor = me.AVAILABLE_COLOR,
                internalColor = me.AVAILABLE_COLOR,
                name = port.name,
                remoteId = "none",
                remoteName = "none",
                internalEnabled = true,
                enabled = true;

            if(!port.free) {
                pinColor = me.OCCUPIED_COLOR;
                enabled = false;
                if(port.remote_device) {
                    remoteId = port.remote_device.id;
                    remoteName = port.remote_device.name;
                    if(side === "left") {
                        name += " => " + port.remote_device.name + "/" + port.remote_device.slot;
                    } else {
                        name = port.remote_device.name + "/" + port.remote_device.slot + " <= " + port.name;
                    }
                }
            }
            if(!port.valid) {
                pinColor = me.INVALID_COLOR;
                enabled = false;
            }
            if(port.internal) {
                if(!port.internal.valid) {
                    internalColor = me.INVALID_COLOR;
                    internalEnabled = false;
                }
                if(!port.internal.free) {
                    internalColor = me.OCCUPIED_COLOR;
                    internalEnabled = false;
                }
            }
            sprites.push({
                type: "pin",
                id: port.id,
                boxWidth: me.boxWidth,
                boxHeight: me.boxHeight,
                fontSize: 12,
                pinName: name,
                pinColor: pinColor,
                internalColor: internalColor,
                isSelected: port.name === selectedPin,
                remoteId: remoteId,
                remoteName: remoteName,
                enabled: enabled,
                internalEnabled: internalEnabled,
                hasInternalLabel: hasDiscriminator,
                side: side,
                labelAlign: labelAlign,
                allowInternal: !Ext.isEmpty(port.internal),
                internalLabelWidth: me.discriminatorWidth[side],
                x: xOffset,
                y: index * (me.boxHeight + me.gap) + me.gap + me.schemaPadding,
                zIndex: 25
            });
        }, me);
        return sprites;
    },
    makeBody: function(pins, side) {
        var me = this,
            object = me.getViewModel().get(side + "Object"),
            bodyWidth = me.getBodyWidth(me, pins, side),
            xOffset = me.xOffset(side, pins),
            name = object ? object.get("name") : "none";

        return {
            type: "body",
            id: side + "Body",
            boxWidth: me.boxWidth,
            boxHeight: me.boxHeight,
            label: name,
            side: side,
            width: bodyWidth,
            height: me.maxPins * (me.boxHeight + me.gap) + me.gap,
            x: xOffset + bodyWidth * (side === "left" ? -1 : 0),
            y: me.schemaPadding,
            gap: me.gap
        };
    },
    makeInternalConnections: function(connections, side) {
        var me = this,
            surface = me.drawPanel.getSurface(),
            sprites = [];

        Ext.each(connections, function(connection) {
            var conn,
                from = surface.get(connection.from.id),
                to = surface.get(connection.to.id);

            from.has_arrow = connection.from.has_arrow;
            to.has_arrow = connection.to.has_arrow;
            if(conn = me.makeConnection(from, to, side, "internal", connection)) sprites.push(conn);
        });
        return Ext.Array.map(
            Ext.Array.sort(sprites, function(a, b) {
                return a.length - b.length;
            }), function(sprite, index) {
                var f = sprite.fromXY,
                    t = sprite.toXY,
                    betweenLine = sprite.side === "left" ? -1 : 1;

                sprite.trace = index + me.firstTrace;
                sprite.path = Ext.String.format("M{0},{1} L{2},{3} L{4},{5} L{6},{7}",
                    f[0], f[1], f[0] + betweenLine * me.gap * sprite.trace, f[1], f[0] + betweenLine * me.gap * sprite.trace, t[1], t[0], t[1]);
                return sprite;
            }
        );
    },
    makeConnection: function(from, to, side, type, attr) {
        var me = this;

        if(from.internal && to.internal) {
            var f = from.internal.getBBoxCenter(),
                t = to.internal.getBBoxCenter();

            return {
                type: "connection",
                connectionType: type,
                side: side,
                fromPortId: from.id,
                fromPort: from.pinName,
                fromXY: f,
                fromHasArrow: from.has_arrow,
                fromDiscriminator: attr.from.discriminator,
                toPortId: to.id,
                toPort: to.pinName,
                toXY: t,
                toHasArrow: to.has_arrow,
                toDiscriminator: attr.to.discriminator,
                isDeleted: attr.is_delete,
                gainDb: attr.gain_db,
                actualScale: me.scale,
                boxWidth: me.boxWidth,
                boxHeight: me.boxHeight,
                discriminatorWidth: me.discriminatorWidth[side],
                connectionColor: attr.is_delete ? me.WIRE_COLOR : me.DISABLED_WIRE_COLOR,
                length: Math.abs(f[1] - t[1]),
                zIndex: 50,
            };
        }
    },
    makeLegend: function(text, color, x, h) {
        return [
            {
                type: "rect",
                width: 15,
                height: 15,
                fillStyle: color,
                stroke: "black",
                lineWidth: 2,
                x: x,
                y: h - 2.5
            },
            {
                type: "text",
                text: text,
                textAlign: "start",
                fontFamily: "arial",
                fontWeight: "normal",
                fontSize: 12,
                textBaseline: "middle",
                x: x + 20,
                y: h + 5

            }
        ]
    },
    scaleCalculate: function() {
        var me = this,
            surfaceHeight = me.maxPins * (me.boxHeight + me.gap) + me.gap + me.schemaPadding * 4,
            containerHeight = me.drawPanel.getHeight() - me.legendHeight;
        if(surfaceHeight > containerHeight) {
            // calculate needed vertical space for diagram
            // ToDo calculate width of schema, when two objects and select optimal scale factor, need width body of objects
            me.surfaceHeight = me.maxPins * (me.boxHeight + me.gap) + me.gap + me.schemaPadding * 4;
            me.scale = Math.min(containerHeight / me.surfaceHeight, 0.6);
            me.boxHeight *= me.scale;
            me.boxWidth *= me.scale;
            me.gap *= me.scale;
            me.schemaPadding *= me.scale;
            me.discriminatorWidth.left *= me.scale;
            me.discriminatorWidth.right *= me.scale;
        }
        me.surfaceHeight = containerHeight;
    },
    createWire(prevSprite, sprite, fromSide) {
        var me = this,
            mainSurface = me.drawPanel.getSurface(),
            wires = me.getWires(mainSurface),
            wire = [
                {id: sprite.id, side: sprite.side},
                {id: prevSprite.id, side: prevSprite.side},
            ];
        Ext.Array.sort(wire, function(a, b) {
            if(a.side === 'left' && b.side === 'right') {
                return -1;
            }
            if(a.side === 'right' && b.side === 'left') {
                return 1;
            }
            return 0;
        });
        wires.push(wire);
        me.drawWires(wires, mainSurface);
    },
    createInternalConnection: function(fromSprite, toSprite, side) {
        var me = this,
            internalConnectionSurface = me.drawPanel.getSurface(side + "_internal_conn"),
            mainSurface = me.drawPanel.getSurface(),
            connections = me.getInternalConnections(internalConnectionSurface);

        Ext.create("Ext.window.Window", {
            autoShow: true,
            width: 400,
            reference: "createConnFrm",
            modal: true,
            layout: "form",
            title: __("Create internal connection from") + " " + fromSprite.attr.pinName + " " + __("to") + " " + toSprite.pinName,
            referenceHolder: true,
            defaultFocus: "textfield",
            defaultButton: "createBtn",
            items: [
                {
                    xtype: "textfield",
                    fieldLabel: __("Discriminator From"),
                    name: "fromDiscriminator"
                },
                {
                    xtype: "textfield",
                    fieldLabel: __("Discriminator To"),
                    name: "toDiscriminator"
                },
                {
                    xtype: "numberfield",
                    fieldLabel: __("Gain DB"),
                    step: 0.1,
                    minValue: 0,
                    maxValue: 100,
                    name: "gainDb",
                    value: 0,
                    listeners: {
                        validitychange: function(field, isValid) {
                            field.up("window").lookupReference("createBtn").setDisabled(!isValid);
                        }
                    }
                }
            ],
            buttons: [
                {
                    text: __("Create"),
                    reference: "createBtn",
                    handler: function(button) {
                        var hasDiscriminator, internalConnectionQty, calculatedWidth,
                            win = button.up("window"),
                            body = mainSurface.get(side + "Body"),
                            gainDb = win.down("[name=gainDb]").getValue(),
                            fromDiscriminator = win.down("[name=fromDiscriminator]").getValue(),
                            toDiscriminator = win.down("[name=toDiscriminator]").getValue(),
                            from = {
                                discriminator: fromDiscriminator,
                                has_arrow: false,
                                id: fromSprite.id,
                                name: fromSprite.attr.pinName
                            },
                            to = {
                                discriminator: toDiscriminator,
                                has_arrow: true,
                                id: toSprite.id,
                                name: toSprite.pinName
                            },
                            connection = {
                                gain_db: gainDb,
                                is_delete: true,
                                to: to,
                                from: from
                            };


                        internalConnectionQty = connections.internal_connections.push(connection);
                        if(hasDiscriminator = me.hasDiscriminator(connections.internal_connections)) {
                            me.switchInternalLabel(body, true);
                        }
                        calculatedWidth = (internalConnectionQty + me.firstTrace) * me.gap + (hasDiscriminator ? Math.abs(me.discriminatorWidth[side]) : 0);
                        if(body.width <= calculatedWidth) {
                            var increment = (side === "left" ? calculatedWidth - body.attr.width : 0);
                            body.setAttributes({
                                width: calculatedWidth,
                                x: body.attr.x - increment,
                            });
                        }
                        me.drawInternalConnections(connections, internalConnectionSurface, side);
                        console.log("renderFrame: createInternalConnections");
                        mainSurface.renderFrame();
                        button.up("window").close();
                    },
                },
                {
                    text: __("Cancel"),
                    handler: function() {
                        this.up("window").close();
                    }
                }
            ]
        });
    },
    deleteInternalConnection: function() {
        var me = this,
            drawPanel = me.drawPanel,
            sprite = drawPanel.selectedSprite,
            mainSurface = drawPanel.getSurface(),
            surface = sprite.getSurface();

        console.log("deleteInternalConnection", sprite.fromPortId, sprite.toPortId);
        Ext.Msg.confirm(__("Confirm"), __("Are you sure you want to delete this connection") + " " + sprite.fromPort + "=>" + sprite.toPort, function(btn) {
            if(btn === "yes") {
                var connections,
                    side = sprite.side,
                    body = mainSurface.get(side + "Body");

                sprite.remove();
                connections = me.getInternalConnections(surface);
                if(!me.hasDiscriminator(connections.internal_connections)) {
                    me.switchInternalLabel(body, false);
                }
                me.drawInternalConnections(connections, surface, side);
                console.log("renderFrame: deleteInternalConnections");
                mainSurface.renderFrame();
            }
            drawPanel.isModalOpen = false;
        });
    },
    deleteWire: function(sprite) {
        var me = this,
            drawPanel = me.drawPanel,
            mainSurface = drawPanel.getSurface();

        console.log("deleteWire", sprite.fromPortId, sprite.toPortId);
        Ext.Msg.confirm(__("Confirm"), __("Are you sure you want to delete this wire") + " " + sprite.fromPort + "=>" + sprite.toPort, function(btn) {
            if(btn === "yes") {
                var connections,
                    side = sprite.side,
                    body = mainSurface.get(side + "Body");

                sprite.remove();
                connections = me.getWires(mainSurface);
                me.drawWires(connections, mainSurface);
                console.log("renderFrame: deleteWires");
                mainSurface.renderFrame();
            }
            drawPanel.isModalOpen = false;
        });
    },
    switchInternalLabel: function(body, state) {
        var me = this,
            mainSurface = me.drawPanel.getSurface(),
            internalPins = Ext.Array.filter(mainSurface.getItems(), function(sprite) {return sprite.type === "pin" && sprite.side === body.side});

        Ext.Array.map(internalPins, function(pin) {
            pin.setAttributes({
                hasInternalLabel: state,
            })
        });
    },
    getInternalConnections: function(surface) {
        return {
            internal_connections: Ext.Array.map(surface.getItems(), function(sprite) {
                return {
                    from: {
                        id: sprite.attr.fromPortId,
                        name: sprite.attr.fromPort,
                        discriminator: sprite.attr.fromDiscriminator,
                        has_arrow: sprite.attr.fromHasArrow,
                    },
                    to: {
                        id: sprite.attr.toPortId,
                        name: sprite.attr.toPort,
                        discriminator: sprite.attr.toDiscriminator,
                        has_arrow: sprite.attr.toHasArrow,

                    },
                    gain_db: sprite.attr.gainDb,
                    is_delete: sprite.attr.isDeleted
                }
            })
        }
    },
    getWires: function(surface) {
        return Ext.Array.map(
            Ext.Array.filter(surface.getItems(), function(sprite) {return sprite.type === "connection" && sprite.connectType === "wire"}),
            function(wire) {
                return [
                    {id: wire.fromPortId, side: wire.side[0]},
                    {id: wire.toPortId, side: wire.side[1]}
                ]
            });
    },
    getWiresOffset: function(firstSide, secondSide) {
        var me = this,
            mainSurface = me.drawPanel.getSurface(),
            sprites = mainSurface.getItems(),
            firstPins = Ext.Array.filter(sprites, function(sprite) {return sprite.type === "pin" && sprite.side === firstSide}),
            secondPins = secondSide ? Ext.Array.filter(sprites, function(sprite) {return sprite.type === "pin" && sprite.side === secondSide}) : [{pinNameWidth: 0}];

        return [(firstSide === "left" ? 1 : -1) * Ext.Array.max(Ext.Array.map(firstPins, function(pin) {return pin.pinNameWidth})),
        (firstSide === "left" ? 1 : -1) * Ext.Array.max(Ext.Array.map(secondPins, function(pin) {return pin.pinNameWidth}))];
    },
    selectPin: function(element, prevSelectPinId, isInternal, preIsInternal) {
        var sprite = element.sprite,
            isSelected = sprite.attr.isSelected;
        if((sprite.id !== prevSelectPinId) ||
            (sprite.id === prevSelectPinId && isInternal === preIsInternal)) {
            isSelected = !isSelected;
        }
        sprite.setAttributes({
            isSelected: isSelected,
            isInternalFixed: isInternal
        });
        if(sprite.id !== prevSelectPinId) {
            // deselect previous selection
            var preSelectedSprite = this.drawPanel.getSurface().get(prevSelectPinId);
            if(preSelectedSprite) {
                preSelectedSprite.setAttributes({isSelected: false});
            }
        }
    },
    isPinAvailableForSelect: function(sprite) {
        // check is mouse over pin available to make connection
        var me = this,
            viewModel = me.getViewModel(),
            firstSelectedPinId = viewModel.get("selectedPinId"),
            firstIsSelectedPinInternal = viewModel.get("isSelectedPinInternal"),
            firstSide = viewModel.get("side"),
            isSelectedPinInternal = sprite.attr.cursorOn === "internal";

        if(!firstSelectedPinId) { // no pin selected
            return false;
        }
        if(firstSelectedPinId === sprite.id && firstSide === sprite.side) {
            return false;
        }
        if(isSelectedPinInternal === !firstIsSelectedPinInternal) {
            return false;
        }
        if(!isSelectedPinInternal && !sprite.enabled) {
            return false;
        }
        if(isSelectedPinInternal && !sprite.internalEnabled) {
            return false;
        }
        return true;
    },
    beforeDestroy: function() {
        var me = this,
            target = me.formPanelDropTarget;
        if(target) {
            target.unreg();
            me.formPanelDropTarget = null;
        }
        me.getEl().un("keydown", me.cancelDrawConnection);
        this.callParent();
    },
    onDrop: function(ddSource, e, data) {
        var me = this,
            selectedRecord = ddSource.dragData.records[0];

        if(me.getViewModel().get("leftObject")) {
            me.getViewModel().set("rightObject", selectedRecord);
        }
        if(!me.getViewModel().get("leftObject")) {
            me.getViewModel().set("leftObject", selectedRecord);
        }
        this.load();
        return true;
    },
    onPressClose: function() {
        var me = this;
        me.app.mainPanel.remove(me.app.connectionPanel, false);
        me.app.mainPanel.add(me.app.tabPanel);
    },
    onBoxReady: function() {
        this.callParent(arguments);
        var me = this,
            body = me.body;

        me.formPanelDropTarget = new Ext.dd.DropTarget(body, {
            ddGroup: "navi-tree-to-form",
            notifyEnter: function() {
                body.stopAnimation();
                body.highlight();
            },
            notifyDrop: Ext.bind(me.onDrop, me),
        });
    },
    onSpriteMouseOver: function(element, event) {
        var me = this,
            mainSurface = me.drawPanel.getSurface(),
            sprite = element.sprite;

        if(!me.drawPanel.isModalOpen) {
            switch(sprite.type) {
                case "pin": {
                    sprite.setAttributes({
                        actualScale: 1.2,
                    });
                    // illumination of ALL wire connections
                    Ext.each(mainSurface.getItems(), function(s) {
                        if(s.fromPortId === sprite.id || s.toPortId === sprite.id) {
                            s.setAttributes(me.drawPanel.selectedWire);
                        }
                    });
                    // illumination of ALL internal connections
                    Ext.each(me.drawPanel.getSurface(sprite.side + "_internal_conn").getItems(), function(s) {
                        if(s.fromPortId === sprite.id || s.toPortId === sprite.id) {
                            s.setAttributes(me.drawPanel.selectedWire);
                        }
                    });
                    // illumination of selected label
                    mainSurface.get("label" + sprite.id).setAttributes({
                        isSelected: true,
                    });
                    if(me.isPinAvailableForSelect(sprite)) {
                        var viewModel = me.getViewModel(),
                            pointer = mainSurface.get("pointer"),
                            firstSide = viewModel.get("side");

                        sprite.setAttributes({
                            isSelected: true,
                            isInternalFixed: sprite.attr.cursorOn === "internal",
                            pinOver: true,
                        });
                        pointer.setAttributes({
                            lineType: firstSide === sprite.side && sprite.attr.cursorOn !== "internal" ? "loopback" : sprite.attr.cursorOn,
                            side: sprite.side,
                            xOffsets: me.getWiresOffset(firstSide, sprite.side),
                        });
                    }
                    // console.log("renderFrame (main): onSpriteMouseOver");
                    // me.drawPanel.getSurface().renderFrame();
                    // console.log("renderFrame (internal): onSpriteMouseOver");
                    // me.drawPanel.getSurface(sprite.side + "_internal_conn").renderFrame();
                    break;
                }
                case "connection": {
                    mainSurface.get(sprite.fromPortId).setAttributes({
                        actualScale: 1.2,
                    });
                    mainSurface.get(sprite.toPortId).setAttributes({
                        actualScale: 1.2,
                    });
                    mainSurface.get("label" + sprite.fromPortId).setAttributes({
                        isSelected: true,
                    });
                    mainSurface.get("label" + sprite.toPortId).setAttributes({
                        isSelected: true,
                    });
                    if(sprite.connectionType === "internal") {
                        me.drawPanel.selectedSprite = sprite;
                        sprite.setAttributes(me.drawPanel.selectedWire);
                        // console.log("renderFrame (internal): onSpriteMouseOver");
                        // me.drawPanel.getSurface(sprite.side + "_internal_conn").renderFrame();
                        if(sprite.toDiscriminatorTooltip && sprite.toDiscriminatorTooltip.isHidden()) {
                            sprite.toDiscriminatorTooltip.showAt([event.pageX, event.pageY]);
                        }
                        if(sprite.fromDiscriminatorTooltip && sprite.fromDiscriminatorTooltip.isHidden()) {
                            sprite.fromDiscriminatorTooltip.showAt([event.pageX, event.pageY]);
                        }
                    }
                    if(Ext.Array.contains(["wire", "loopback"], sprite.connectionType)) {
                        sprite.setAttributes(me.drawPanel.selectedWire);
                        // console.log("renderFrame (main): onSpriteMouseOver");
                        // me.drawPanel.getSurface().renderFrame();
                    }
                    break;
                }
            }
        }
    },
    onSpriteMouseOut: function(element, event, args) {
        var me = this,
            viewModel = me.getViewModel(),
            selectedPinId = viewModel.get("selectedPinId"),
            mainSurface = me.drawPanel.getSurface(),
            sprite = element.sprite;

        if(!me.drawPanel.isModalOpen) {
            switch(sprite.type) {
                case "pin": {
                    if(selectedPinId !== sprite.id) {
                        var pointer = mainSurface.get("pointer");
                        sprite.setAttributes({
                            isSelected: false,
                            pinOver: false,
                        });
                        if(pointer) {
                            pointer.setAttributes({
                                lineType: "line",
                                side: sprite.side,
                            });
                        }
                    }
                    sprite.setAttributes({
                        actualScale: 1,
                    });
                    // wire connections
                    Ext.each(me.drawPanel.getSurface().getItems(), function(s) {
                        if(s.fromPortId === sprite.id || s.toPortId === sprite.id) {
                            s.setAttributes(me.drawPanel.wire);
                        }
                    });
                    // internal connections
                    Ext.each(me.drawPanel.getSurface(sprite.side + "_internal_conn").getItems(), function(s) {
                        if(s.fromPortId === sprite.id || s.toPortId === sprite.id) {
                            if(s.isDeleted) {
                                s.setAttributes(me.drawPanel.wire);
                            } else {
                                s.setAttributes(me.drawPanel.disabledWire);
                            }
                        }
                    });
                    mainSurface.get("label" + sprite.id).setAttributes({
                        isSelected: false,
                    });
                    // console.log("renderFrame (main): onSpriteMouseOut");
                    // me.drawPanel.getSurface().renderFrame();
                    // console.log("renderFrame (internal): onSpriteMouseOut");
                    // me.drawPanel.getSurface(sprite.side + "_internal_conn").renderFrame();
                    break;
                }
                case "connection": {
                    mainSurface.get("label" + sprite.fromPortId).setAttributes({
                        isSelected: false,
                    });
                    mainSurface.get("label" + sprite.toPortId).setAttributes({
                        isSelected: false,
                    });
                    mainSurface.get(sprite.fromPortId).setAttributes({
                        actualScale: 1,
                    });
                    mainSurface.get(sprite.toPortId).setAttributes({
                        actualScale: 1,
                    });
                    if(sprite.connectionType === "internal") {
                        me.drawPanel.selectedSprite = undefined;
                        if(sprite.isDeleted) {
                            sprite.setAttributes(me.drawPanel.wire);
                        } else {
                            sprite.setAttributes(me.drawPanel.disabledWire);
                        }
                        if(sprite.toDiscriminatorTooltip && !sprite.toDiscriminatorTooltip.isHidden()) {
                            sprite.toDiscriminatorTooltip.hide();
                        }
                        if(sprite.fromDiscriminatorTooltip && !sprite.fromDiscriminatorTooltip.isHidden()) {
                            sprite.fromDiscriminatorTooltip.hide();
                        }
                        // console.log("renderFrame (internal): onSpriteMouseOut");
                        // me.drawPanel.getSurface(sprite.side + "_internal_conn").renderFrame();
                    }
                    if(Ext.Array.contains(["wire", "loopback"], sprite.connectionType)) {
                        sprite.setAttributes(me.drawPanel.wire);
                        // console.log("renderFrame (main): onSpriteMouseOver");
                        // me.drawPanel.getSurface().renderFrame();
                    }
                    break;
                }
            }
        }
    },
    onSpriteClick: function(element, event) {
        var offset,
            pointerX, pointerY,
            me = this,
            sprite = element.sprite,
            viewModel = me.getViewModel(),
            surface = me.drawPanel.getSurface(),
            prevSelectPinId = viewModel.get("selectedPinId"),
            prevIsInternal = viewModel.get("isSelectedPinInternal"),
            side = viewModel.get("side"),
            prevSprite = surface.get(prevSelectPinId),
            pointer = surface.get("pointer"),
            side = sprite.side,
            isInternal = sprite.attr.cursorOn === "internal",
            isWire = sprite.attr.cursorOn === "wire";

        if(!sprite.enabled && isWire) {
            return;
        }
        if(!sprite.internalEnabled && isInternal) {
            return;
        }

        if(prevSprite && (prevSprite.id === sprite.id)) {
            return;
        }

        if(isInternal && sprite.attr.isSelected && prevSprite && prevSprite.attr.isSelected) {
            me.createInternalConnection(prevSprite, sprite, side);
        }

        if(!isInternal && sprite.attr.isSelected && prevSprite && prevSprite.attr.isSelected) {
            me.createWire(prevSprite, sprite, side);
        }

        switch(sprite.type) {
            case "pin": {
                me.selectPin(element, prevSelectPinId, isInternal, prevIsInternal);
                sprite.setAttributes({
                    isInternalFixed: isInternal
                });
                // add pointer
                if(isInternal) {
                    pointerX = sprite.internal.attr.translationX;
                    pointerY = sprite.internal.attr.translationY;
                    offset = (side === "left" ? -4 * me.boxWidth : 4 * me.boxWidth);
                }
                if(isWire) {
                    pointerX = sprite.box.attr.translationX + sprite.box.attr.width / 2;
                    pointerY = sprite.box.attr.translationY + sprite.box.attr.height / 2;
                    offset = me.getWiresOffset(side, undefined)[0];
                }
                if(!pointer) {
                    pointer = surface.add({
                        type: "pointer",
                        id: "pointer",
                        fromX: pointerX,
                        fromY: pointerY,
                        toX: pointerX + offset,
                        toY: pointerY,
                        actualScale: me.scale,
                        strokeStyle: "red",
                        boxWidth: me.boxWidth,
                        boxHeight: me.boxHeight,
                        zIndex: 75,
                    });
                } else {
                    pointer.setAttributes({
                        fromX: pointerX,
                        fromY: pointerY,
                        toX: pointerX + offset,
                        toY: pointerY,
                        actualScale: me.scale,
                    });
                }
                if(sprite.attr.isSelected) {
                    viewModel.set("selectedPinId", sprite.id);
                    viewModel.set("selectedPin", sprite.pinName);
                    viewModel.set("isSelectedPinInternal", isInternal);
                    viewModel.set("side", side);
                } else {
                    // self selected
                    viewModel.set("selectedPinId", null);
                    viewModel.set("selectedPin", null);
                    viewModel.set("isSelectedPinInternal", null);
                    viewModel.set("side", null);
                    surface.get("pointer").remove();
                }
                break;
            }
            case "connection": {
                if(sprite.connectionType === "internal" && sprite.isDeleted) {
                    me.drawPanel.isModalOpen = true;
                    me.deleteInternalConnection();
                }
                if(Ext.Array.contains(["wire", "loopback"], sprite.connectionType)) {
                    me.drawPanel.isModalOpen = true;
                    me.deleteWire(sprite);
                }
                break;
            }
        }
        console.log("renderFrame: onSpriteClick");
        surface.renderFrame();
        // mainPanel.load();
    },
    onCleanClick: function() {
        var me = this;

        me.setTitle(__("Object connections"));
        me.cleanViewModel();
        me.drawPanel.removeAll(true);
        console.log("renderFrame: onCleanClick");
        me.drawPanel.renderFrame();
    },
    onReload: function() {
        this.load();
    },
    onMouseMove: function(event) {
        var me = this;
        if(me.getViewModel().get("selectedPinId")) {
            var surface = me.drawPanel.getSurface(),
                pointer = surface.get("pointer");
            if(pointer) {
                var surfaceEl = surface.el.dom,
                    surfaceXY = Ext.fly(surfaceEl).getXY();
                pointer.setAttributes({
                    toX: event.pageX - surfaceXY[0],
                    toY: event.pageY - surfaceXY[1]
                });
                me.drawPanel.getSurface().renderFrame();
            }
        }
    },
    onConnectClick: function() {
        // var me = this,
        //     cable = me.getViewModel().get("cable"),
        //     leftObject = me.getViewModel().get("leftObject").get("id"),
        //     rightObject = me.getViewModel().get("rightObject").get("id"),
        //     leftPin = me.getViewModel().get("leftSelectedPin"),
        //     rightPin = me.getViewModel().get("rightSelectedPin"),
        //     leftPinId = me.getViewModel().get("leftSelectedPinId"),
        //     rightPinId = me.getViewModel().get("rightSelectedPinId"),
        //     param = {
        //         object: leftObject,
        //         name: leftPin,
        //         remote_object: rightObject,
        //         remote_name: rightPin,
        //     };

        // if(cable) {
        //     param.cable = cable;
        // }
        // Ext.Ajax.request({
        //     url: "/inv/inv/connect/",
        //     method: "POST",
        //     jsonData: param,
        //     scope: me,
        //     success: function() {
        //         this.drawPanel.getSurface().add(this.drawWire([
        //             {
        //                 left: {id: leftPinId}, right: {id: rightPinId}
        //             }
        //         ]));
        //         this.drawPanel.renderFrame();
        //         NOC.msg.complete(__("Objects was successfully connected"));
        //     },
        //     failure: function(response) {
        //         NOC.error(__("Failed to connect objects : ") + response.responseText);
        //     }
        // });
    },
    cleanViewModel: function() {
        this.getViewModel().set("leftObject", null);
        this.getViewModel().set("rightObject", null);
        this.getViewModel().set("selectedPin", null);
        this.getViewModel().set("selectedPinId", null);
        this.getViewModel().set("isSelectedPinInternal", null);
    },
    cancelDrawConnection: function() {
        var canvas = Ext.ComponentQuery.query("#canvas")[0],
            viewModel = canvas.up().getViewModel(),
            surface = canvas.getSurface(),
            pointer = surface.get("pointer");

        Ext.Array.each(surface.getItems(), function(element) {
            if(element.attr.isSelected) element.setAttributes({isSelected: false});
        });
        viewModel.set("selectedPin", null);
        viewModel.set("selectedPinId", null);
        viewModel.set("isSelectedPinInternal", null);
        if(pointer) {
            pointer.remove();
        }
        console.log("renderFrame: cancelDrawConnection");
        canvas.getSurface().renderFrame();
    },
    xOffset: function(side, pins) {
        var internalPinQty = this.internalPinQty(pins);

        if(side === "left") {
            return internalPinQty * this.gap + 100 - this.discriminatorWidth[side];
        }
        return this.getWidth() - internalPinQty * this.gap - 100 - this.discriminatorWidth[side];
    },
    getBodyWidth: function(me, pins, side) {
        return (this.internalPinQty(pins) + 1) * me.gap + Math.abs(me.discriminatorWidth[side]);
    },
    internalPinQty: function(pins) {
        return Ext.Array.filter(pins, (function(pin) {return pin.internal;})).length || 1;
    },
    hasDiscriminator: function(connections) {
        var hasDiscriminator = false;
        Ext.each(connections, function(connection) {
            if(!Ext.isEmpty(connection.from.discriminator) || !Ext.isEmpty(connection.to.discriminator)) {
                hasDiscriminator = true;
                return false;
            }
        });
        return hasDiscriminator;
    }
});
