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
    boxWidth: undefined,
    boxHeight: undefined,
    schemaPadding: undefined,
    gap: undefined,
    scale: undefined,
    discriminatorWidth: undefined,
    requires: [
        "NOC.core.ComboBox",
        "NOC.core.Connection",
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
            isModalOpen: false,
            wire: {
                connectionColor: me.WIRE_COLOR,
                lineWidth: 2,
                zIndex: 10,
            },
            disabledWire: {
                connectionColor: me.DISABLED_WIRE_COLOR,
                lineWidth: 2,
                zIndex: 10,
            },
            selectedWire: {
                connectionColor: me.SELECTED_WIRE_COLOR,
                lineWidth: 4,
                zIndex: 110,
            },
            sprites: [],
            listeners: {
                spritemouseover: me.onSpriteMouseOver,
                spritemouseout: me.onSpriteMouseOut,
                spriteclick: me.onSpriteClick,
                scope: me,
                afterrender: function(container) {
                    container.getEl().on('keydown', me.cancelDrawConnection);
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
    load: function() {
        var params, title,
            mainPanel = this,
            cable = mainPanel.cableCombo.getValue(),
            // leftSelected = mainPanel.getViewModel().get("leftSelectedPin"),
            // rightSelected = mainPanel.getViewModel().get("rightSelectedPin"),
            leftObject = mainPanel.getViewModel().get("leftObject"),
            rightObject = mainPanel.getViewModel().get("rightObject");

        title = leftObject.get("name") + " <==> " + (rightObject ? rightObject.get("name") : __("none"));
        mainPanel.setTitle(title);
        params = "o1=" + leftObject.get("id") + (rightObject ? "&o2=" + rightObject.get("id") : "");
        // params += leftSelected ? "&left_filter=" + leftSelected : "";
        // params += rightSelected ? "&right_filter=" + rightSelected : "";
        params += cable ? "&cable_filter=" + cable : "";
        mainPanel.mask(__("Loading..."));
        Ext.Ajax.request({
            url: "/inv/inv/crossing_proposals/?" + params,
            method: "GET",
            success: function(response) {
                var sprites,
                    drawPanel = mainPanel.drawPanel,
                    surface = drawPanel.getSurface(),
                    data = Ext.decode(response.responseText),
                    maxPins = Math.max(data.left.connections.length, data.right.connections.length),
                    // isValid = function(pins, name) {
                    //     return Ext.each(pins, function(pin) {
                    //         if(pin.name === name) {
                    //             return pin.valid;
                    //         }
                    //     });
                    // },
                    left = [
                        data.left.connections,
                        "left", // side
                        "right", // label Alignment
                        maxPins
                    ],
                    right = [
                        data.right.connections,
                        "right", // side
                        "left", // label Alignment
                        maxPins
                    ];

                mainPanel.unmask();
                whichDraw = leftObject ? left : right;
                NOC.msg.complete(__("The data was successfully loaded"));
                surface.removeAll();
                // if(!isValid(data.right.connections, rightSelected)) {
                //     mainPanel.getViewModel().set("rightSelectedPin", null);
                //     mainPanel.getViewModel().set("rightSelectedPinId", null);
                // }
                // if(!isValid(data.left.connections, leftSelected)) {
                //     mainPanel.getViewModel().set("leftSelectedPin", null);
                //     mainPanel.getViewModel().set("leftSelectedPinId", null);
                // }
                mainPanel.cableCombo.getStore().loadData(data.cable);
                sprites = mainPanel.drawObject.apply(mainPanel, whichDraw);
                // var surface = drawPanel.getSurface();
                surface.add(sprites.pins);
                if(rightObject) {
                    surface.add(mainPanel.drawWire(data.wires));
                }

                mainPanel.drawConnections.apply(mainPanel, [data.left.internal_connections].concat([drawPanel.getSurface(whichDraw[1] + "_internal_conn")].concat(whichDraw)));
                surface.add(sprites.legend);
                sprites.body[1].text = leftObject ? leftObject.get("name") : rightObject.gat("name");
                surface.add(sprites.body);
                // drawPanel.getSurface(whichDraw[1] + "_internal_conn");
                surface.renderFrame();
            },
            failure: function() {
                mainPanel.unmask();
                NOC.msg.failed(__("Error loading data"));
            }
        });
    },
    onDrop: function(ddSource, e, data) {
        var mainPanel = this,
            selectedRecord = ddSource.dragData.records[0];

        if(mainPanel.getViewModel().get("leftObject")) {
            mainPanel.getViewModel().set("rightObject", selectedRecord);
        }
        if(!mainPanel.getViewModel().get("leftObject")) {
            mainPanel.getViewModel().set("leftObject", selectedRecord);
        }
        this.load();
        return true;
    },
    drawObject: function(pins, side, labelAlign, maxPins) {
        var surfaceHeight,
            bodyWidth,
            bodyOffset,
            me = this,
            selectedPin = me.getViewModel().get("selectedPin"),
            containerHeight = me.drawPanel.getHeight() - 20, // 20 is legend height
            countInternal = 0,
            sprites = {pins: [], legend: [], body: {}};

        me.boxWidth = 20;
        me.boxHeight = 20;
        me.discriminatorWidth = (side === "left" ? -150 : 150);
        me.schemaPadding = me.boxHeight * 3;
        me.gap = 12.5;
        me.scale = 1;
        countInternal = pins.filter(function(pin) {return pin.internal;}).length;
        countInternal = countInternal ? countInternal : me.boxWidth / me.gap + 1;
        bodyWidth = (side === "left" ? -1 : 1) * (countInternal + 3) * me.gap + me.discriminatorWidth;
        bodyOffset = (side === "left" ? 0 : me.boxWidth);
        // calculate needed vertical space for diagram
        // ToDo calculate width of schema, when two objects and select optimal scale factor, need width body of objects
        surfaceHeight = maxPins * (me.boxHeight + me.gap) + me.gap + me.schemaPadding * 4;
        me.scale = Math.min(containerHeight / surfaceHeight, 0.6);
        me.boxHeight *= me.scale;
        me.boxWidth *= me.scale;
        me.discriminatorWidth *= me.scale;
        me.gap *= me.scale;
        me.schemaPadding *= me.scale;
        bodyWidth *= me.scale;
        bodyOffset *= me.scale
        countInternal = countInternal ? countInternal : me.boxWidth / me.gap + 1;
        xOffset = me.xOffset(side, countInternal);
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
            sprites.pins.push({
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
                side: side,
                labelAlign: labelAlign,
                allowInternal: !Ext.isEmpty(port.internal),
                internalLabelWidth: me.discriminatorWidth,
                x: xOffset,
                y: index * (me.boxHeight + me.gap) + me.gap + me.schemaPadding,
                zIndex: 5
            });
        }, me);
        sprites.body = [
            {
                type: "rect",
                id: "body",
                width: bodyWidth,
                height: maxPins * (me.boxHeight + me.gap) + me.gap,
                stroke: "black",
                lineWidth: 2,
                x: xOffset + bodyOffset,
                y: me.schemaPadding
            },
            {
                type: "text",
                id: "title",
                fontWeight: "bold",
                fontSize: 14,
                textAlign: side === "left" ? "start" : "end",
                x: xOffset + bodyWidth + bodyOffset,
                y: me.schemaPadding - me.gap
            }
        ];
        // add legend
        sprites.legend = sprites.legend.concat(me.legend(__("Free and valid slot"), me.AVAILABLE_COLOR, 2.5, containerHeight));
        sprites.legend = sprites.legend.concat(me.legend(__("Occupied slot"), me.OCCUPIED_COLOR, 250, containerHeight));
        sprites.legend = sprites.legend.concat(me.legend(__("Invalid slot"), me.INVALID_COLOR, 500, containerHeight));
        return sprites;
    },
    drawConnections: function(connections, surface, _externalConnections, side) {
        var me = this,
            sprites;

        surface.removeAll();
        sprites = me.makeInternalConnections(connections, side);
        surface.add(sprites);
        surface.renderFrame();
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
            if(connection.from.discriminator) {
                from.setAttributes({internalLabel: connection.from.discriminator});
            }
            if(connection.to.discriminator) {
                to.setAttributes({internalLabel: connection.to.discriminator});
            }
            if(conn = me.makeConnection(from, to, side, "internal", connection.is_delete, connection.gain_db)) sprites.push(conn);
        });
        return Ext.Array.map(Ext.Array.sort(sprites, function(a, b) {
            return a.length - b.length;
        }), function(sprite, index) {
            var f = sprite.fromXY,
                t = sprite.toXY,
                betweenLine = sprite.side === "left" ? -1 : 1;
            sprite.trace = index + 3;
            sprite.path = Ext.String.format("M{0},{1} L{2},{3} L{4},{5} L{6},{7}",
                f[0], f[1], f[0] + betweenLine * me.gap * sprite.trace, f[1], f[0] + betweenLine * me.gap * sprite.trace, t[1], t[0], t[1]);
            return sprite;
        });
    },
    makeConnection: function(from, to, side, type, is_delete, gain_db) {
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
                fromDiscriminator: from.discriminator,
                toPortId: to.id,
                toPort: to.pinName,
                toXY: t,
                toHasArrow: to.has_arrow,
                toDiscriminator: to.discriminator,
                isDeleted: is_delete,
                gainDb: gain_db,
                actualScale: me.scale,
                connectionColor: is_delete ? me.WIRE_COLOR : me.DISABLED_WIRE_COLOR,
                length: Math.abs(f[1] - t[1])
            };
        }
    },
    createInternalConnection: function(fromSprite, toSprite, side) {
        var body, bodyWidth,
            me = this,
            surface = me.drawPanel.getSurface(side + "_internal_conn"),
            countInternal = surface.getItems().length + 3;

        var from = {
            discriminator: "",
            has_arrow: false,
            id: fromSprite.id,
            name: fromSprite.attr.pinName
        },
            to = {
                discriminator: "",
                has_arrow: true,
                id: toSprite.id,
                name: toSprite.pinName

            };
        connection = {
            gain_db: 1,
            is_delete: true,
            to: to,
            from: from
        };
        body = me.drawPanel.getSurface().get("body");
        bodyWidth = (side === "left" ? -1 : 1) * (countInternal + 3) * me.gap + me.discriminatorWidth;
        if(Math.abs(bodyWidth) > Math.abs(body.attr.width)) {
            body.setAttributes({
                width: bodyWidth,
            });
        }
        me.drawConnections(me.getInternalConnections(surface).concat(connection), surface, undefined, side);
    },
    getInternalConnections: function(surface) {
        return Ext.Array.map(surface.getItems(), function(sprite) {
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
        });
    },
    drawWire: function(wires) {
        var mainPanel = this,
            sprites = [];

        Ext.each(wires, function(wire) {
            var surface = mainPanel.drawPanel.getSurface(),
                leftPort = surface.get(wire.left.id),
                rightPort = sprites.get(wire.right.id);

            sprites.push({
                type: "line",
                leftPortId: leftPort.id,
                rightPortId: rightPort.id,
                fromX: leftPort.x + leftPort.box.width / 2,
                fromY: leftPort.y + leftPort.box.height / 2,
                toX: rightPort.x + rightPort.box.width / 2,
                toY: rightPort.y + rightPort.box.height / 2,
                strokeStyle: mainPanel.WIRE_COLOR,
                lineWidth: 2,
                zIndex: 10,
            });
        });
        return sprites;
    },
    legend: function(text, color, x, h) {
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
    onSpriteMouseOver: function(element, event, args) {
        var me = this,
            surface = me.drawPanel.getSurface(),
            sprite = element.sprite;

        if(!me.drawPanel.isModalOpen) {
            switch(sprite.type) {
                case "pin": {
                    sprite.setAttributes({
                        actualScale: 1.02,
                        labelBold: true,
                    });
                    // illumination of ALL external connections
                    Ext.each(surface.getItems(), function(s) {
                        if(s.config.leftPortId === sprite.id || s.config.rightPortId === sprite.id) {
                            s.setAttributes({
                                strokeStyle: me.SELECTED_WIRE_COLOR,
                                lineWidth: 4,
                                zIndex: 100,
                            });
                        }
                    });
                    // illumination of ALL internal connections
                    Ext.each(me.drawPanel.getSurface(sprite.side + "_internal_conn").getItems(), function(s) {
                        if(s.fromPortId === sprite.id || s.toPortId === sprite.id) {
                            s.setAttributes(me.drawPanel.selectedWire);
                        }
                    });
                    if(me.isPinAvailableForSelect(sprite)) {
                        sprite.setAttributes({
                            isSelected: true,
                            isInternalFixed: sprite.attr.cursorOn === "internal",
                            pinOver: true,
                        });
                        surface.get("pointer").setAttributes({
                            lineType: "path",
                            side: sprite.side
                        })
                    }
                    if(sprite.internalLabelTooltip && sprite.internalLabelTooltip.isHidden()) {
                        sprite.internalLabelTooltip.showAt([event.pageX, event.pageY + 20]);
                    }
                    me.drawPanel.getSurface().renderFrame();
                    me.drawPanel.getSurface(sprite.side + "_internal_conn").renderFrame();
                    break;
                }
                case "connection": {
                    if(sprite.connectionType === "internal") {
                        me.drawPanel.selectedSprite = sprite;
                        sprite.setAttributes(me.drawPanel.selectedWire);
                        me.drawPanel.getSurface(sprite.side + "_internal_conn").renderFrame();
                    }
                    break;
                }
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

        if(!firstSelectedPinId) {
            return false;
        }
        if(isSelectedPinInternal !== firstIsSelectedPinInternal && firstSide === sprite.side) {
            return false;
        }
        if(sprite.id === firstSelectedPinId) {
            return false;
        }
        if(isSelectedPinInternal && !sprite.internalEnabled) {
            return false;
        }
        if(!isSelectedPinInternal && !sprite.enabled) {
            return false;
        }
        if(firstSide === sprite.side && !isSelectedPinInternal) {
            return false;
        }
        return true;
    },
    onSpriteMouseOut: function(element, event, args) {
        var me = this,
            viewModel = me.getViewModel(),
            selectedPinId = viewModel.get("selectedPinId"),
            surface = me.drawPanel.getSurface(),
            sprite = element.sprite;

        if(!me.drawPanel.isModalOpen) {
            switch(sprite.type) {
                case "pin": {
                    if(selectedPinId !== sprite.id) {
                        var pointer = surface.get("pointer");
                        sprite.setAttributes({
                            isSelected: false,
                            pinOver: false,
                        });
                        if(pointer) {
                            pointer.setAttributes({
                                lineType: "line",
                            });
                        }
                    }
                    sprite.setAttributes({
                        actualScale: 1,
                        labelBold: false,
                    });
                    // external connections
                    Ext.each(me.drawPanel.getSurface().getItems(), function(s) {
                        if(s.config.leftPortId === sprite.id || s.config.rightPortId === sprite.id) {
                            s.setAttributes({
                                strokeStyle: me.WIRE_COLOR,
                                lineWidth: 2,
                                zIndex: 10,
                            });
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
                    if(sprite.internalLabelTooltip && !sprite.internalLabelTooltip.isHidden()) {
                        sprite.internalLabelTooltip.hide();
                    }
                    me.drawPanel.getSurface().renderFrame();
                    me.drawPanel.getSurface(sprite.side + "_internal_conn").renderFrame();
                    break;
                }
                case "connection": {
                    if(sprite.connectionType === "internal") {
                        me.drawPanel.selectedSprite = undefined;
                        if(sprite.isDeleted) {
                            sprite.setAttributes(me.drawPanel.wire);
                        } else {
                            sprite.setAttributes(me.drawPanel.disabledWire);
                        }
                        me.drawPanel.getSurface(sprite.side + "_internal_conn").renderFrame();
                    }
                    break;
                }
            }
        }
    },
    onSpriteClick: function(element, event) {
        var offset,
            pointerX, pointerY,
            mainPanel = this,
            sprite = element.sprite,
            viewModel = mainPanel.getViewModel(),
            surface = mainPanel.drawPanel.getSurface(),
            prevSelectPinId = viewModel.get("selectedPinId"),
            prevIsInternal = viewModel.get("isSelectedPinInternal"),
            side = viewModel.get("side"),
            prevSprite = surface.get(prevSelectPinId),
            pointer = surface.get("pointer"),
            side = sprite.side,
            isInternal = sprite.attr.cursorOn === "internal",
            isExternal = sprite.attr.cursorOn === "external";

        if(!sprite.enabled && isExternal) {
            return;
        }
        if(!sprite.internalEnabled && isInternal) {
            return;
        }

        if(isInternal && sprite.attr.isSelected && prevSprite && prevSprite.attr.isSelected) {
            mainPanel.createInternalConnection(prevSprite, sprite, side);
        }

        switch(sprite.type) {
            case "pin": {
                mainPanel.selectPin(element, prevSelectPinId, isInternal, prevIsInternal);
                sprite.setAttributes({
                    isInternalFixed: isInternal
                });
                // add pointer
                if(isInternal) {
                    pointerX = sprite.internal.attr.translationX + mainPanel.discriminatorWidth;
                    pointerY = sprite.internal.attr.translationY;
                    offset = (side === "left" ? -50 : 50)
                }
                if(isExternal) {
                    pointerX = sprite.box.attr.translationX + sprite.box.attr.width / 2;
                    pointerY = sprite.box.attr.translationY + sprite.box.attr.height / 2;
                    offset = (side === "left" ? 50 : -50)
                }
                if(!pointer) {
                    pointer = surface.add({
                        type: "pointer",
                        id: "pointer",
                        fromX: pointerX,
                        fromY: pointerY,
                        toX: pointerX + offset,
                        toY: pointerY,
                        actualScale: mainPanel.scale,
                        strokeStyle: "red",
                        zIndex: 150,
                    });
                } else {
                    pointer.setAttributes({
                        fromX: pointerX,
                        fromY: pointerY,
                        toX: pointerX + offset,
                        toY: pointerY,
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
                if(mainPanel.drawPanel.selectedSprite.isDeleted && !pointer) {
                    mainPanel.drawPanel.isModalOpen = true;
                    mainPanel.deleteInternalConnection();
                }
                break;
            }
        }
        surface.renderFrame();
        // mainPanel.load();
    },
    onCleanClick: function() {
        var me = this;

        me.setTitle(__("Object connections"));
        me.cleanViewModel();
        me.drawPanel.removeAll(true);
        me.drawPanel.renderFrame();
    },
    onReload: function() {
        this.load();
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
    deleteInternalConnection: function() {
        var drawPanel = Ext.ComponentQuery.query("#canvas")[0],
            me = this,
            drawPanel = me.drawPanel,
            sprite = drawPanel.selectedSprite,
            surface = sprite.getSurface();
        console.log("deleteInternalConnection", sprite.fromPortId, sprite.toPortId);
        // sprite.setAttributes(drawPanel.selectedWire);
        // surface.renderFrame();
        Ext.Msg.confirm(__("Confirm"), __("Are you sure you want to delete this connection") + " " + sprite.fromPort + "=>" + sprite.toPort, function(btn) {
            if(btn === "yes") {
                var side = sprite.side;

                sprite.remove();
                me.drawConnections(me.getInternalConnections(surface), surface, undefined, side);
                // drawPanel.renderFrame();
            }
            drawPanel.isModalOpen = false;
        });
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
            // selectedPin = surface.get(viewModel.get("selectedPinId")),
            // isSelectedPinInternal = viewModel.get("isSelectedPinInternalId"),
            pointer = surface.get("pointer");

        // if(selectedPin) {
        // selectedPin.setAttributes({
        //     isSelected: false,
        //     // pinOver: false,
        //     // isInternalFixed: isSelectedPinInternal
        // });
        Ext.Array.each(surface.getItems(), function(element) {
            if(element.attr.isSelected) element.setAttributes({isSelected: false});
        });
        viewModel.set("selectedPin", null);
        viewModel.set("selectedPinId", null);
        viewModel.set("isSelectedPinInternal", null);
        // }
        if(pointer) {
            pointer.remove();
        }
        canvas.getSurface().renderFrame();
    },
    xOffset: function(side, pins) {
        if(side === "left") {
            return pins * this.gap + 100 - this.discriminatorWidth;
        }
        return this.getWidth() - pins * this.gap - 100 - this.discriminatorWidth;
    }
});
