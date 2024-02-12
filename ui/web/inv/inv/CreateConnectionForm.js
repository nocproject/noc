//---------------------------------------------------------------------
// inv.inv CreateConnection form
//---------------------------------------------------------------------
// Copyright (C) 2007-2024 The NOC Project
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
    discriminatorWidth: {left: -155, right: 155},
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
            cable: null,
            isDirty: false,
        },
        // formulas: {
        //     isValid: function(get) {
        //         return get("leftSelectedPin") && get("rightSelectedPin");
        //     }
        // }
    },
    initComponent: function() {
        var me = this;
        me.flag = 0;

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
            triggers: {
                clear: {
                    cls: 'x-form-clear-trigger',
                    hidden: true,
                    weight: -1,
                    handler: function(field) {
                        field.setValue(null);
                        field.fireEvent("select", field);
                    }
                },
            },
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
                change: me.reloadStatuses
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
                    handler: me.onCloseClick
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
                    text: __("Save"),
                    scope: me,
                    bind: {
                        disabled: "{!isDirty}"
                    },
                    handler: me.onSaveClick
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

        title = (leftObject ? leftObject.get("name") : __("none")) + " <==> " + (rightObject ? rightObject.get("name") : __("none"));
        me.setTitle(title);
        params = "o1=" + leftObject.get("id") + (rightObject ? "&o2=" + rightObject.get("id") : "");
        // params += leftSelected ? "&left_filter=" + leftSelected : "";
        // params += rightSelected ? "&right_filter=" + rightSelected : "";
        params += cable ? "&cable_filter=" + cable : "";
        me.mask(__("Loading..."));
        Ext.Ajax.request({
            // url: "/inv/inv/crossing_proposals/?" + params,
            url: "http://localhost:3000/crossing_proposals/?" + params,
            method: "GET",
            success: function(response) {
                var drawPanel = me.drawPanel,
                    mainSurface = drawPanel.getSurface(),
                    data = Ext.decode(response.responseText);

                me.maxPins = Math.max(data.left.connections.length, data.right.connections.length);
                me.unmask();
                NOC.msg.complete(__("The data was successfully loaded"));
                mainSurface.removeAll(true);
                me.getViewModel().set("isDirty", false);
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
    reloadStatuses: function() {
        var params, me = this,
            vm = me.getViewModel(),
            leftObject = vm.get("leftObject"),
            rightObject = vm.get("rightObject"),
            cable = me.cableCombo.getValue(),
            leftObjectId = leftObject ? leftObject.id : undefined,
            rightObjectId = rightObject ? rightObject.id : undefined;

        if(me.cableCombo.getValue()) {
            me.cableCombo.getTrigger("clear").show();
        } else {
            me.cableCombo.getTrigger("clear").hide();
        }
        params = "o1=" + leftObjectId + (rightObjectId ? "&o2=" + rightObjectId : "");
        params += cable ? "&cable_filter=" + cable : "";
        me.mask(__("Loading..."));
        Ext.Ajax.request({
            // url: "/inv/inv/crossing_proposals/?" + params,
            url: "http://localhost:3000/crossing_proposals/?" + params,
            method: "GET",
            success: function(response) {
                var data = Ext.decode(response.responseText);

                Ext.Array.each(["left", "right"], function(side) {
                    if(data[side].connections && data[side].connections.length) {
                        me.updatePinsStatus(data[side].connections);
                    }
                });
                me.unmask();
                NOC.msg.complete(__("The data was successfully updated"));
            },
            failure: function() {
                me.unmask();
                NOC.msg.failed(__("Error updating statuses"));
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
        var me = this,
            wiresToRemove = Ext.Array.filter(surface.getItems(), function(sprite) {
                return sprite.type === "connection";
            });

        Ext.Array.each(wiresToRemove, function(sprite) {
            sprite.remove();
        });
        console.log("renderFrame: drawWire");
        surface.add(me.makeWires(wires));
        surface.renderFrame();
    },
    updatePinsStatus: function(pinObjList, side) {
        var me = this,
            mainSurface = me.drawPanel.getSurface(),
            leftSurface = me.drawPanel.getSurface("left_internal_conn"),
            rightSurface = me.drawPanel.getSurface("right_internal_conn"),
            newWires = Ext.Array.filter(mainSurface.getItems(), function(sprite) {return sprite.type === "connection" && sprite.isNew}),
            leftInternal = Ext.Array.filter(leftSurface.getItems(), function(sprite) {return sprite.type === "connection" && sprite.isNew}),
            rightInternal = Ext.Array.filter(rightSurface.getItems(), function(sprite) {return sprite.type === "connection" && sprite.isNew}),
            pinsWithNewConnections = me.flattenArray(Ext.Array.map(leftInternal.concat(newWires).concat(rightInternal), function(connection) {
                var type = connection.connectionType === "internal" ? "internal" : "external";
                return [{
                    pin: connection.fromPortId,
                    type: type,
                },
                {
                    pin: connection.toPortId,
                    type: type
                }];
            }));

        me.cancelDrawConnection();
        Ext.Array.each(pinObjList, function(pinObj) {
            var pinStripe = mainSurface.get(pinObj.id),
                pinHasNewInternalConnection = Ext.Array.filter(pinsWithNewConnections, function(item) {return item.pin === pinObj.id && item.type === "internal"}).length > 0,
                pinHasNewExternalConnection = Ext.Array.filter(pinsWithNewConnections, function(item) {return item.pin === pinObj.id && item.type === "external"}).length > 0,
                {
                    pinColor,
                    internalColor,
                    name,
                    remoteId,
                    remoteName,
                    internalEnabled,
                    enabled
                } = me.portStatus(pinObj, side),
                _pinColor = pinHasNewExternalConnection ? pinStripe.pinColor : pinColor,
                _enabled = pinHasNewExternalConnection ? pinStripe.enabled : enabled,
                _internalColor = pinHasNewInternalConnection ? pinStripe.internalColor : internalColor,
                _internalEnabled = pinHasNewInternalConnection ? pinStripe.internalEnabled : internalEnabled;

            pinStripe.setAttributes({
                isSelected: false,
                pinColor: _pinColor,
                enabled: _enabled,
                internalColor: _internalColor,
                internalEnabled: _internalEnabled,
            });
        });
    },
    flattenArray: function(array) {
        var me = this,
            result = [];

        array.forEach(function(item) {
            if(Ext.isArray(item)) {
                result = result.concat(me.flattenArray(item));
            } else {
                result.push(item);
            }
        });

        return result;
    },
    /**
     * Redraws labels on the given surface, workaround for zIndex, 
     *    zIndex doesn't work with subsprites in custom sprite
     *
     * @param {type} surface - the surface to redraw the labels on
     * @return {type} undefined - no return value
     */
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
            wire = me.wireSort(wire);
            return me.makeWire(mainSurface.get(wire[0].id), mainSurface.get(wire[1].id), wire[0].side, wire[1].side, offsetX[0], offsetX[1], wire[0].isNew, wire[0].cable);
        });
    },
    makeWire: function(firstPort, secondPort, firstSide, secondSide, firstOffset, secondOffset, isNew, cable) {
        return {
            type: "connection",
            connectionType: firstSide === secondSide ? "loopback" : "wire",
            fromPortId: firstPort.id,
            fromPort: firstPort.pinNameOrig,
            toPortId: secondPort.id,
            toPort: secondPort.pinNameOrig,
            fromXY: [firstPort.x + firstPort.box.width / 2, firstPort.y + firstPort.box.height / 2],
            toXY: [secondPort.x + secondPort.box.width / 2, secondPort.y + secondPort.box.height / 2],
            fromSide: firstSide,
            toSide: secondSide,
            isNew: isNew ? isNew : false,
            offset: [firstOffset, secondOffset],
            connectionColor: this.WIRE_COLOR,
            cable: cable,
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
            var {pinColor,
                internalColor,
                name,
                remoteId,
                remoteName,
                internalEnabled,
                enabled} = me.portStatus(port, side);

            sprites.push({
                type: "pin",
                id: port.id,
                boxWidth: me.boxWidth,
                boxHeight: me.boxHeight,
                fontSize: 12,
                pinName: name,
                pinNameOrig: port.name,
                pinColor: pinColor,
                internalColor: internalColor,
                isSelected: port.name === selectedPin,
                remoteId: remoteId,
                remoteName: remoteName,
                enabled: enabled,
                internalEnabled: internalEnabled,
                hasInternalLabel: hasDiscriminator,
                allowDiscriminators: port.internal ? port.internal.allow_discriminators : [],
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
                    betweenLine = sprite.fromSide === "left" ? -1 : 1;

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
                fromPortId: from.id,
                fromPort: from.pinNameOrig,
                fromXY: f,
                fromHasArrow: from.has_arrow,
                fromDiscriminator: attr.from.discriminator,
                fromSide: side,
                toPortId: to.id,
                toPort: to.pinNameOrig,
                toXY: t,
                toHasArrow: to.has_arrow,
                toDiscriminator: attr.to.discriminator,
                toSide: side,
                isDeleted: attr.is_delete,
                gainDb: attr.gain_db,
                actualScale: me.scale,
                boxWidth: me.boxWidth,
                boxHeight: me.boxHeight,
                discriminatorWidth: me.discriminatorWidth[side],
                connectionColor: attr.is_delete ? me.WIRE_COLOR : me.DISABLED_WIRE_COLOR,
                length: Math.abs(f[1] - t[1]),
                isNew: attr.isNew ? true : false,
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
    portStatus: function(port, side) {
        var me = this,
            pinColor = me.AVAILABLE_COLOR,
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
                var remoteLink = port.remote_device.slot ? port.remote_device.slot : "",
                    remoteName = port.remote_device.name ? port.remote_device.name + "/" : "";
                remoteId = port.remote_device.id;
                if(side === "left") {
                    name += " => " + remoteName + remoteLink;
                } else {
                    name = remoteName + remoteLink + " <= " + port.name;
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

        return {
            pinColor: pinColor,
            internalColor: internalColor,
            name: name,
            remoteId: remoteId,
            remoteName: remoteName,
            internalEnabled: internalEnabled,
            enabled: enabled,
        };
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
    createWire(prevPinSprite, pinSprite) {
        var me = this,
            vm = me.getViewModel(),
            cable = me.cableCombo.getValue(),
            mainSurface = me.drawPanel.getSurface(),
            wires = me.getWires(mainSurface),
            fromName = prevPinSprite.pinName,
            toName = pinSprite.pinName,
            wire = [
                {id: pinSprite.id, side: pinSprite.side, isNew: true, cable: cable},
                {id: prevPinSprite.id, side: prevPinSprite.side, isNew: true, cable: cable},
            ];

        if(cable) {
            if(prevPinSprite && prevPinSprite.side !== pinSprite.side && prevPinSprite.side === "left") {
                fromName = prevPinSprite.pinName + " => " + pinSprite.pinName;
                toName = prevPinSprite.pinName + " <= " + pinSprite.pinName;
            }
            if(prevPinSprite && prevPinSprite.side !== pinSprite.side && prevPinSprite.side === "right") {
                fromName = pinSprite.pinName + " <= " + prevPinSprite.pinName;
                toName = pinSprite.pinName + " => " + prevPinSprite.pinName;
            }

            prevPinSprite.setAttributes({
                pinColor: me.OCCUPIED_COLOR,
                enabled: false,
                pinName: fromName,
            });
            // reDraw label for zIndex workaround
            mainSurface.get("label" + prevPinSprite.id).setAttributes({
                labelText: fromName,
                backgroundTranslationX: prevPinSprite.labelBackground.attr.translationX,
                backgroundWidth: prevPinSprite.labelBackground.attr.width,
            });
            pinSprite.setAttributes({
                pinColor: me.OCCUPIED_COLOR,
                enabled: false,
                pinName: toName,
            });
            // reDraw label for zIndex workaround
            mainSurface.get("label" + pinSprite.id).setAttributes({
                labelText: toName,
                backgroundTranslationX: pinSprite.labelBackground.attr.translationX,
                backgroundWidth: pinSprite.labelBackground.attr.width
            });
            wires.push(wire);
            me.drawWires(wires, mainSurface);
            me.getViewModel().set("isDirty", true);
        } else {
            NOC.error(__("Cable is not selected"));
        }
    },
    wireSort: function(wire) {
        return Ext.Array.sort(wire, function(a, b) {
            return a.side === 'left' ? -1 : (b.side === 'left' ? 1 : 0);
        });
    },
    createInternalConnection: function(fromSprite, toSprite, side) {
        var me = this,
            internalConnectionSurface = me.drawPanel.getSurface(side + "_internal_conn"),
            mainSurface = me.drawPanel.getSurface(),
            connections = me.getInternalConnections(internalConnectionSurface),
            fromDiscriminators = fromSprite.allowDiscriminators,
            toDiscriminators = toSprite.allowDiscriminators;

        Ext.create("Ext.window.Window", {
            autoShow: true,
            width: 400,
            reference: "createConnFrm",
            modal: true,
            layout: "form",
            title: __("Create internal connection from") + " " + fromSprite.attr.pinName + " " + __("to") + " " + toSprite.pinName,
            referenceHolder: true,
            defaultFocus: "numberfield",
            defaultButton: "createBtn",
            items: [
                {
                    xtype: "combobox",
                    fieldLabel: __("Discriminator From"),
                    store: fromDiscriminators,
                    disabled: !fromDiscriminators.length,
                    queryMode: "local",
                    name: "fromDiscriminator"
                },
                {
                    xtype: "combobox",
                    fieldLabel: __("Discriminator To"),
                    store: toDiscriminators,
                    disabled: !toDiscriminators.length,
                    queryMode: "local",
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
                                from: from,
                                isNew: true,
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
                        me.getViewModel().set("isDirty", true);
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
                    side = sprite.fromSide,
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
    removeConnection: function(connection) {
        if(connection.connectionType === "internal") {
            this.removeInternalConnection();
        } else {
            this.removeWire(connection);
        }
    },
    removeWire: function(wireSprite) {
        var connections,
            me = this,
            drawPanel = me.drawPanel,
            mainSurface = drawPanel.getSurface(),
            fromSprite = mainSurface.get(wireSprite.fromPortId),
            fromLabelSprite = mainSurface.get("label" + wireSprite.fromPortId),
            toSprite = mainSurface.get(wireSprite.toPortId),
            toLabelSprite = mainSurface.get("label" + wireSprite.toPortId);

        if(wireSprite.fromPort.indexOf(" => ") !== -1) {
            wireSprite.fromPort = wireSprite.fromPort.split(" => ")[0];
        }
        // if(wireSprite.fromPort.indexOf(" <= ") !== -1) {
        //     wireSprite.fromPort = wireSprite.fromPort.split(" <= ")[0];
        // }
        // if(wireSprite.toPort.indexOf(" => ") !== -1) {
        //     wireSprite.toPort = wireSprite.toPort.split(" => ")[0];
        // }
        if(wireSprite.toPort.indexOf(" <= ") !== -1) {
            wireSprite.toPort = wireSprite.toPort.split(" <= ")[1];
        }
        console.log(wireSprite.toPort, wireSprite.fromPort);
        fromSprite.setAttributes({
            pinColor: me.AVAILABLE_COLOR,
            enabled: true,
            pinName: wireSprite.fromPort,
        });
        fromLabelSprite.setAttributes({
            labelText: wireSprite.fromPort,
            backgroundTranslationX: fromSprite.labelBackground.attr.translationX,
            backgroundWidth: fromSprite.labelBackground.attr.width,
        });
        toSprite.setAttributes({
            pinColor: me.AVAILABLE_COLOR,
            enabled: true,
            pinName: wireSprite.toPort,
        });
        toLabelSprite.setAttributes({
            labelText: wireSprite.toPort,
            backgroundTranslationX: toSprite.labelBackground.attr.translationX,
            backgroundWidth: toSprite.labelBackground.attr.width,
        });
        wireSprite.remove();
        connections = me.getWires(mainSurface);
        me.drawWires(connections, mainSurface);
        console.log("renderFrame: deleteWires");
        mainSurface.renderFrame();
    },
    removeInternalConnection: function(connection) {
        console.error("removeInternalConnection not implemented");
    },
    deleteWireMsg: function(wireSprite) {
        var me = this,
            drawPanel = me.drawPanel;

        console.log("deleteWire", wireSprite.fromPortId, wireSprite.toPortId);
        Ext.Msg.confirm(__("Confirm"), __("Are you sure you want to delete this wire") + " " + wireSprite.fromPort + "=>" + wireSprite.toPort, function(btn) {
            if(btn === "yes") {
                var vm = me.getViewModel(),
                    leftObject = vm.get("leftObject"),
                    rightObject = vm.get("rightObject"),
                    params = {
                        object: leftObject.id,
                        name: wireSprite.fromPort,
                        remote_object: rightObject.id,
                        remote_name: wireSprite.toPort,
                        is_internal: wireSprite.connectionType === "internal",
                    };

                if(wireSprite.isNew) {
                    me.removeWire(wireSprite);
                } else {
                    Ext.Ajax.request({
                        url: "/inv/inv/disconnect/",
                        method: "POST",
                        jsonData: params,
                        scope: me,
                        success: function(response) {
                            me.removeWire(wireSprite);
                            NOC.msg.complete(__("Wire was successfully disconnected"));
                        },
                        failure: function(response) {
                            NOC.error(__("Failed to disconnect objects : ") + response.responseText);
                        }
                    });
                }
            }
            drawPanel.isModalOpen = false;
        });
    },
    switchInternalLabel: function(body, state) {
        var me = this,
            mainSurface = me.drawPanel.getSurface(),
            internalPins = Ext.Array.filter(mainSurface.getItems(), function(sprite) {return sprite.type === "pin" && sprite.side === body.side});

        console.log("switchInternalLabel", body.side, state);
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
                    isNew: sprite.attr.isNew,
                    gain_db: sprite.attr.gainDb,
                    is_delete: sprite.attr.isDeleted
                }
            })
        }
    },
    getWires: function(surface) {
        return Ext.Array.map(
            Ext.Array.filter(surface.getItems(), function(sprite) {return sprite.type === "connection"}),
            function(wire) {
                return [
                    {id: wire.fromPortId, side: wire.fromSide, cable: wire.cable, isNew: wire.isNew},
                    {id: wire.toPortId, side: wire.toSide, cable: wire.cable, isNew: wire.isNew}
                ]
            });
    },
    getWiresOffset: function(firstSide, secondSide) {
        var me = this,
            mainSurface = me.drawPanel.getSurface(),
            sprites = mainSurface.getItems(),
            firstPins = Ext.Array.filter(sprites, function(sprite) {return sprite.type === "pin" && sprite.side === firstSide}),
            secondPins = secondSide ? Ext.Array.filter(sprites, function(sprite) {return sprite.type === "pin" && sprite.side === secondSide}) : [{pinNameWidth: 0}];

        return [Ext.Array.max(Ext.Array.map(firstPins, function(pin) {return pin.pinNameWidth})) + me.boxWidth,
        (Ext.Array.max(Ext.Array.map(secondPins, function(pin) {return pin.pinNameWidth})) || 0) + me.boxWidth];
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
        if(isSelectedPinInternal && firstSide !== sprite.side) {
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
    onCloseClick: function() {
        var me = this,
            action = function() {
                me.app.mainPanel.remove(me.app.connectionPanel, false);
                me.app.mainPanel.add(me.app.tabPanel);
            };

        if(me.getViewModel().get("isDirty")) {
            Ext.Msg.confirm(__("Confirm"), __("There is unsaved data, do you really want to close the application?"), function(btn) {
                if(btn === "yes") {
                    action();
                }
            });
        } else {
            action();
        }
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
                    var pointer = mainSurface.get("pointer");

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
                    if(pointer) {
                        pointer.setAttributes({
                            lineType: "line",
                        });
                    }
                    if(sprite.connectionType === "internal") {
                        me.drawPanel.selectedSprite = sprite;
                        sprite.setAttributes(me.drawPanel.selectedWire);
                        // console.log("renderFrame (internal): onSpriteMouseOver");
                        // me.drawPanel.getSurface(sprite.side + "_internal_conn").renderFrame();
                        if(sprite.toDiscriminatorTooltip && sprite.toDiscriminatorTooltip.isHidden()) {
                            sprite.toDiscriminatorTooltip.showAt([event.pageX + (sprite.side === "left" ? 20 : -20), event.pageY + 20]);
                        }
                        if(sprite.fromDiscriminatorTooltip && sprite.fromDiscriminatorTooltip.isHidden()) {
                            sprite.fromDiscriminatorTooltip.showAt([event.pageX + (sprite.side === "left" ? 20 : -20), event.pageY - 20]);
                        }
                    }
                    if(Ext.Array.contains(["wire", "loopback"], sprite.connectionType)) {
                        sprite.setAttributes(me.drawPanel.selectedWire);
                        // console.log("renderFrame (main): onSpriteMouseOver");
                        me.drawPanel.getSurface().renderFrame();
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
            prevSprite = surface.get(prevSelectPinId),
            pointer = surface.get("pointer"),
            side = sprite.side || "left",
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
                    offset = (side === "left" ? 1 : -1) * me.getWiresOffset(side, undefined)[0];
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
                    me.deleteWireMsg(sprite);
                }
                break;
            }
        }
        console.log("renderFrame: onSpriteClick");
        surface.renderFrame();
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
    onSaveClick: function() {
        var params, leftObjectId, rightObjectId,
            me = this,
            vm = me.getViewModel(),
            mainSurface = me.drawPanel.getSurface(),
            leftSurface = me.drawPanel.getSurface("left_internal_conn"),
            rightSurface = me.drawPanel.getSurface("right_internal_conn"),
            leftObject = vm.get("leftObject"),
            rightObject = vm.get("rightObject"),
            newWires = Ext.Array.filter(mainSurface.getItems(), function(sprite) {return sprite.type === "connection" && sprite.isNew}),
            leftInternal = Ext.Array.filter(leftSurface.getItems(), function(sprite) {return sprite.type === "connection" && sprite.isNew}),
            rightInternal = Ext.Array.filter(rightSurface.getItems(), function(sprite) {return sprite.type === "connection" && sprite.isNew}),
            connections = leftInternal.concat(newWires).concat(rightInternal);

        leftObjectId = leftObject.get("id");
        if(rightObject) {
            rightObjectId = rightObject.get("id");
        } else {
            rightObjectId = leftObjectId;
        }
        console.log(leftObjectId, rightObjectId);
        console.log(connections);

        params = Ext.Array.map(connections, function(connection) {
            var param = {
                object: leftObjectId,
                name: connection.fromPort,
                remote_object: rightObjectId,
                remote_name: connection.toPort,
                is_internal: connection.connectionType === "internal",
            };
            if(connection.cable) {
                param.cable = connection.cable;
            }
            return param;
        });
        Ext.Ajax.request({
            url: "/inv/inv/connect/",
            method: "POST",
            jsonData: params,
            scope: me,
            success: function(response) {
                var invalidConnections,
                    data = Ext.decode(response.responseText);

                Ext.Array.each(connections, function(connection) {
                    connection.setAttributes({isNew: false});
                });
                vm.set("isDirty", false);
                if(data && data.status) {
                    NOC.msg.complete(__("Objects was successfully connected"));
                } else {
                    NOC.error(__("Failed to connect objects : ") + data.text);
                    invalidConnections = data.invalid_connections;
                    if(invalidConnections && invalidConnections.length) {
                        var title = __("Invalid Connections will be deleted") + ":<br/><br/>",
                            msg = Ext.Array.map(invalidConnections, function(connection) {
                                return connection.error;
                            });
                        Ext.Msg.show({
                            title: __("Invalid connections"),
                            message: title + msg.join("<br/>") + "<br/><br/><br/>" + __("This message will automatically close in 5 seconds."),
                            buttons: Ext.Msg.OK,
                            icon: Ext.Msg.INFO
                        });

                        Ext.Array.each(invalidConnections, function(invalid) {
                            Ext.Array.each(connections, function(connection) {
                                if(connection.fromPort === invalid.name && connection.toPort === invalid.remote_name) {
                                    connection.remove();
                                    me.removeConnection(connection);
                                    return false;
                                }
                            });
                        });
                        if(rightSurface) {
                            rightSurface.renderFrame();
                        }
                        Ext.defer(function() {
                            Ext.Msg.hide();
                        }, 5000);
                    }
                }
                mainSurface.renderFrame();
                leftSurface.renderFrame();
                rightSurface.renderFrame();
            },
            failure: function(response) {
                NOC.error(__("Failed to connect objects : ") + response.responseText);
            }
        });
    },
    cleanViewModel: function() {
        this.getViewModel().set("leftObject", null);
        this.getViewModel().set("rightObject", null);
        this.getViewModel().set("selectedPin", null);
        this.getViewModel().set("selectedPinId", null);
        this.getViewModel().set("isSelectedPinInternal", null);
        this.getViewModel().set("cable", null);
        this.getViewModel().set("isDirty", false);
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
