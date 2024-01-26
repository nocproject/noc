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
            leftSelectedPin: null,
            leftSelectedPinId: null,
            leftIsInternalConnection: null,
            rightSelectedPin: null,
            rightSelectedPinId: null,
            rightIsInternalConnection: null,
        },
        formulas: {
            isValid: function(get) {
                return get("leftSelectedPin") && get("rightSelectedPin");
            }
        }
    },
    initComponent: function() {
        var me = this;

        me.boxWidth = 20;
        me.boxHeight = 20;
        me.schemaPadding = me.boxHeight * 3;
        me.gap = 12.5;
        me.scale = 1;
        me.drawPanel = Ext.create({
            xtype: "draw",
            itemId: "canvas",
            region: "center",
            scrollable: false,
            isMenuOpen: false,
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
                zIndex: 100,
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
        me.menu = Ext.create("Ext.menu.Menu", {
            autoDestroy: true,
            items: [
                {
                    text: __("Delete Connection"),
                    handler: me.deleteInternalConnection
                }
            ],
            listeners: {
                scope: me,
                hide: function() {
                    var drawPanel = this.drawPanel;
                    drawPanel.isMenuOpen = false;
                    drawPanel.selectedSprite.setAttributes(drawPanel.wire);
                    drawPanel.getSurface(drawPanel.selectedSprite.labelAlign + "_internal_conn").renderFrame();
                }
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

        me.drawPanel.getEl().on("contextmenu", me.showMenu);
    },
    load: function() {
        var params, title,
            mainPanel = this,
            cable = mainPanel.cableCombo.getValue(),
            leftSelected = mainPanel.getViewModel().get("leftSelectedPin"),
            rightSelected = mainPanel.getViewModel().get("rightSelectedPin"),
            leftObject = mainPanel.getViewModel().get("leftObject"),
            rightObject = mainPanel.getViewModel().get("rightObject");

        title = leftObject.get("name") + " <==> " + (rightObject ? rightObject.get("name") : __("none"));
        mainPanel.setTitle(title);
        params = "o1=" + leftObject.get("id") + (rightObject ? "&o2=" + rightObject.get("id") : "");
        params += leftSelected ? "&left_filter=" + leftSelected : "";
        params += rightSelected ? "&right_filter=" + rightSelected : "";
        params += cable ? "&cable_filter=" + cable : "";
        mainPanel.mask(__("Loading..."));
        Ext.Ajax.request({
            url: "/inv/inv/crossing_proposals/?" + params,
            method: "GET",
            success: function(response) {
                var sprites, data = Ext.decode(response.responseText),
                    maxPins = Math.max(data.left.connections.length, data.right.connections.length),
                    isValid = function(pins, name) {
                        return Ext.each(pins, function(pin) {
                            if(pin.name === name) {
                                return pin.valid;
                            }
                        });
                    },
                    left = [data.left.connections,
                    mainPanel.getWidth() / 2 - 100,
                        "right",
                        // "left",
                        maxPins],
                    right = [data.right.connections,
                    mainPanel.getWidth() / 2 + 100,
                        "left", maxPins];

                mainPanel.unmask();
                whichDraw = leftObject ? left : right;
                NOC.msg.complete(__("The data was successfully loaded"));
                mainPanel.drawPanel.getSurface().removeAll();
                if(!isValid(data.right.connections, rightSelected)) {
                    mainPanel.getViewModel().set("rightSelectedPin", null);
                    mainPanel.getViewModel().set("rightSelectedPinId", null);
                }
                if(!isValid(data.left.connections, leftSelected)) {
                    mainPanel.getViewModel().set("leftSelectedPin", null);
                    mainPanel.getViewModel().set("leftSelectedPinId", null);
                }
                mainPanel.cableCombo.getStore().loadData(data.cable);
                sprites = mainPanel.drawObject.apply(mainPanel, whichDraw);
                mainPanel.drawPanel.getSurface().add(sprites.pins);
                if(rightObject) {
                    mainPanel.drawPanel.getSurface().add(mainPanel.drawWire(data.wires));
                }
                mainPanel.drawPanel.getSurface(whichDraw[2] + "_internal_conn").add(mainPanel.drawInternalConnections(data.left.internal_connections, whichDraw));
                mainPanel.drawPanel.getSurface().add(sprites.legend);
                sprites.body[1].text = leftObject ? leftObject.get("name") : rightObject.gat("name");
                mainPanel.drawPanel.getSurface().add(sprites.body);
                mainPanel.drawPanel.renderFrame();
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
    drawObject: function(pins, xOffset, labelAlign, maxPins) {
        var me = this,
            selectedPin = me.getViewModel().get(labelAlign + "SelectedPin"),
            containerHeight = me.drawPanel.getHeight() - 20, // 20 is legend height
            surfaceHeight = maxPins * (me.boxHeight + me.gap) + me.gap + me.schemaPadding * 4,
            countInternal = 0,
            sprites = {pins: [], legend: [], body: {}};

        me.scale = containerHeight / surfaceHeight;
        me.boxHeight *= me.scale;
        me.boxWidth *= me.scale;
        me.gap *= me.scale;
        me.schemaPadding *= me.scale;
        countInternal = pins.filter(function(pin) {return pin.internal;}).length;
        countInternal = countInternal ? countInternal : me.boxWidth / me.gap + 1;
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
                    if(labelAlign === "left") {
                        name = port.remote_device.name + "/" + port.remote_device.slot + " <= " + port.name;
                    } else {
                        name += " => " + port.remote_device.name + "/" + port.remote_device.slot;
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
                labelAlign: labelAlign,
                allowInternal: !Ext.isEmpty(port.internal),
                x: xOffset,
                y: index * (me.boxHeight + me.gap) + me.gap + me.schemaPadding,
                zIndex: 5
            });
        }, me);
        sprites.body = [
            {
                type: "rect",
                width: (labelAlign === "left" ? 1 : -1) * (countInternal + 1) * me.gap,
                height: maxPins * (me.boxHeight + me.gap) + me.gap,
                stroke: "black",
                lineWidth: 2,
                x: xOffset + (labelAlign === "left" ? me.boxWidth : 0),
                y: me.schemaPadding
            },
            {
                type: "text",
                fontWeight: "bold",
                fontSize: 14,
                x: xOffset + (labelAlign === "left" ? 1 : -1) * countInternal * me.gap,
                y: me.schemaPadding - me.gap
            }
        ];
        // add legend
        sprites.legend = sprites.legend.concat(me.legend(__("Free and valid slot"), me.AVAILABLE_COLOR, 2.5, containerHeight));
        sprites.legend = sprites.legend.concat(me.legend(__("Occupied slot"), me.OCCUPIED_COLOR, 250, containerHeight));
        sprites.legend = sprites.legend.concat(me.legend(__("Invalid slot"), me.INVALID_COLOR, 500, containerHeight));
        return sprites;
    },
    drawInternalConnections: function(connections, args) {
        var me = this,
            sprites = [];

        Ext.each(connections, function(connection, index) {
            var from = undefined,
                to = undefined;
            Ext.each(me.drawPanel.getSurface().getItems(), function(fromPin) {
                if(connection.from.id === fromPin.id) {
                    from = fromPin;
                    Ext.each(me.drawPanel.getSurface().getItems(), function(toPin) {
                        if(connection.to.id === toPin.id) {
                            to = toPin;
                        }
                        if(from && to) {
                            return false;
                        }
                    });
                    if(from.internal && to.internal) {
                        var f = from.internal.getBBoxCenter(),
                            t = to.internal.getBBoxCenter(),
                            betweenLine = args[2] === "left" ? 1 : -1;

                        sprites.push({
                            type: "connection",
                            connectionType: "internal",
                            labelAlign: args[2],
                            fromPort: from.pinName,
                            fromPortId: from.id,
                            toPort: to.pinName,
                            toPortId: to.id,
                            actualScale: me.scale,
                            toXY: t,
                            fromXY: f,
                            fromHasArrow: connection.from.has_arrow,
                            toHasArrow: connection.to.has_arrow,
                            isDeleted: connection.is_delete,
                            connectionColor: connection.is_delete ? me.WIRE_COLOR : me.DISABLED_WIRE_COLOR,
                            path: Ext.String.format("M{0},{1} L{2},{3} L{4},{5} L{6},{7}", f[0], f[1], f[0] + betweenLine * me.gap * (index + 1), f[1], f[0] + betweenLine * me.gap * (index + 1), t[1], t[0], t[1]),
                        });
                    }
                    return false;
                }
            });
        });
        return sprites;
    },
    drawWire: function(wires) {
        var mainPanel = this,
            sprites = [];

        Ext.each(wires, function(wire) {
            var leftPort, rightPort;

            Ext.each(mainPanel.drawPanel.getSurface().getItems(), function(sprite) {
                if(wire.left.id === sprite.id) {
                    leftPort = sprite;
                }
                if(wire.right.id === sprite.id) {
                    rightPort = sprite;
                }
                if(rightPort && leftPort) {
                    return false;
                }
            });
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
    deSelectPin: function(pin, prevSelectPinId, isInternal, preIsInternal) {
        var sprite = pin.sprite,
            isSelected = sprite.attr.isSelected;
        if((sprite.id !== prevSelectPinId) ||
            (sprite.id === prevSelectPinId && isInternal === preIsInternal)) {
            isSelected = !isSelected;
        }
        sprite.setAttributes({
            isSelected: isSelected,
            isInternal: isInternal
        });
        if(sprite.id !== prevSelectPinId) {
            // deselect previous selection
            Ext.each(this.drawPanel.getSurface().getItems(), function(sprite) {
                if(sprite.id === prevSelectPinId) {
                    sprite.setAttributes({
                        isSelected: false
                    });
                    return false;
                }
            });
        }
    },
    beforeDestroy: function() {
        var me = this,
            target = me.formPanelDropTarget;
        if(target) {
            target.unreg();
            me.formPanelDropTarget = null;
        }
        me.drawPanel.getEl().un("contextmenu", me.showMenu);
        me.getEl().un("keydown", me.cancelDrawConnection);
        this.callParent();
    },
    onSpriteMouseOver: function(element, event, args) {
        var me = this,
            sprite = element.sprite;

        if(!me.drawPanel.isMenuOpen) {
            if(sprite.type === "pin") {
                sprite.setAttributes({
                    scale: 1.02,
                    labelBold: true,
                });
                Ext.each(me.drawPanel.getSurface().getItems(), function(sprite) {
                    if(sprite.config.leftPortId === sprite.id || sprite.config.rightPortId === sprite.id) {
                        sprite.setAttributes({
                            strokeStyle: me.SELECTED_WIRE_COLOR,
                            lineWidth: 4,
                            zIndex: 100,
                        });
                    }
                });
                Ext.each(me.drawPanel.getSurface(sprite.labelAlign + "_internal_conn").getItems(), function(sprite) {
                    if(sprite.isDeleted && (sprite.fromPortId === sprite.id || sprite.toPortId === sprite.id)) {
                        sprite.setAttributes(me.drawPanel.selectedWire);
                    }
                });
                me.drawPanel.getSurface().renderFrame();
                me.drawPanel.getSurface(sprite.labelAlign + "_internal_conn").renderFrame();
            }
            if(sprite.type === "connection" && sprite.connectionType === "internal" && sprite.isDeleted) {
                me.drawPanel.selectedSprite = sprite;
                sprite.setAttributes(me.drawPanel.selectedWire);
                me.drawPanel.getSurface(sprite.labelAlign + "_internal_conn").renderFrame();
            }
        }
    },
    onSpriteMouseOut: function(element, event, args) {
        var me = this,
            sprite = element.sprite;

        if(!me.drawPanel.isMenuOpen) {
            if(sprite.type === "pin") {
                sprite.setAttributes({
                    scale: 1,
                    labelBold: false,
                });
                Ext.each(me.drawPanel.getSurface().getItems(), function(sprite) {
                    if(sprite.config.leftPortId === sprite.id || sprite.config.rightPortId === sprite.id) {
                        sprite.setAttributes({
                            strokeStyle: me.WIRE_COLOR,
                            lineWidth: 2,
                            zIndex: 10,
                        });
                    }
                });
                Ext.each(me.drawPanel.getSurface(sprite.labelAlign + "_internal_conn").getItems(), function(sprite) {
                    if(sprite.isDeleted && (sprite.fromPortId === sprite.id || sprite.toPortId === sprite.id)) {
                        sprite.setAttributes(me.drawPanel.wire);
                    }
                });
                me.drawPanel.getSurface().renderFrame();
                me.drawPanel.getSurface(sprite.labelAlign + "_internal_conn").renderFrame();
            }
            if(sprite.type === "connection" && sprite.connectionType === "internal" && sprite.isDeleted) {
                me.drawPanel.selectedSprite = undefined;
                sprite.setAttributes(me.drawPanel.wire);
                me.drawPanel.getSurface(sprite.labelAlign + "_internal_conn").renderFrame();
            }
        }
    },
    onSpriteClick: function(pin, event) {
        var offset,
            mainPanel = this,
            sprite = pin.sprite,
            isInternal = sprite.attr.cursorOn === "internal",
            isExternal = sprite.attr.cursorOn === "external";

        if(sprite.remoteId !== "none") {
            var leftObject, rightObject;
            if(sprite.config.labelAlign === "left") {
                leftObject = mainPanel.getViewModel().get("leftObject");
                rightObject = Ext.create("Ext.data.Model", {id: sprite.remoteId, name: sprite.remoteName});
            } else {
                rightObject = mainPanel.getViewModel().get("rightObject");
                leftObject = Ext.create("Ext.data.Model", {id: sprite.remoteId, name: sprite.remoteName});
            }
            mainPanel.getViewModel().set("leftObject", rightObject);
            mainPanel.getViewModel().set("rightObject", leftObject);
            mainPanel.getViewModel().set("leftSelectedPin", null);
            mainPanel.getViewModel().set("rightSelectedPin", null);
            // mainPanel.load();
            return;
        }
        if(!sprite.enabled && isExternal) {
            return;
        }
        if(!sprite.internalEnabled && isInternal) {
            return;
        }
        var label = sprite.labelAlign,
            prevSelectPinId = mainPanel.getViewModel().get(label + "SelectedPinId"),
            prevIsInternal = mainPanel.getViewModel().get(label + "IsInternalConnection"),

            pointer = mainPanel.drawPanel.getSurface().get("pointer"),
            pointerX, pointerY;
        mainPanel.deSelectPin(pin, prevSelectPinId, isInternal, prevIsInternal);
        sprite.setAttributes({
            isInternalFixed: isInternal
        });
        // add pointer
        if(isInternal) {
            pointerX = sprite.internal.attr.translationX;
            pointerY = sprite.internal.attr.translationY;
            offset = (label === "left" ? 50 : -50)
        }
        if(isExternal) {
            pointerX = sprite.box.attr.translationX + sprite.box.attr.width / 2;
            pointerY = sprite.box.attr.translationY + sprite.box.attr.height / 2;
            offset = (label === "left" ? -50 : 50)
        }
        if(!pointer) {
            pointer = mainPanel.drawPanel.getSurface().add({
                type: "pointer",
                id: "pointer",
                fromX: pointerX,
                fromY: pointerY,
                toX: pointerX + offset,
                toY: pointerY,
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
            mainPanel.getViewModel().set(label + "SelectedPinId", sprite.id);
            mainPanel.getViewModel().set(label + "SelectedPin", sprite.pinName);
            mainPanel.getViewModel().set(label + "IsInternalConnection", isInternal);
            if(prevIsInternal && isInternal && prevSelectPinId) { // draw internal connection
                console.log("draw internal connection", prevSelectPinId, sprite.id);
                mainPanel.isConnectionExist(sprite.labelAlign, prevSelectPinId, sprite.id);
            }
        } else {
            // self selected
            mainPanel.getViewModel().set(label + "SelectedPinId", null);
            mainPanel.getViewModel().set(label + "SelectedPin", null);
        }
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
        var me = this,
            cable = me.getViewModel().get("cable"),
            leftObject = me.getViewModel().get("leftObject").get("id"),
            rightObject = me.getViewModel().get("rightObject").get("id"),
            leftPin = me.getViewModel().get("leftSelectedPin"),
            rightPin = me.getViewModel().get("rightSelectedPin"),
            leftPinId = me.getViewModel().get("leftSelectedPinId"),
            rightPinId = me.getViewModel().get("rightSelectedPinId"),
            param = {
                object: leftObject,
                name: leftPin,
                remote_object: rightObject,
                remote_name: rightPin,
            };

        if(cable) {
            param.cable = cable;
        }
        Ext.Ajax.request({
            url: "/inv/inv/connect/",
            method: "POST",
            jsonData: param,
            scope: me,
            success: function() {
                this.drawPanel.getSurface().add(this.drawWire([
                    {
                        left: {id: leftPinId}, right: {id: rightPinId}
                    }
                ]));
                this.drawPanel.renderFrame();
                NOC.msg.complete(__("Objects was successfully connected"));
            },
            failure: function(response) {
                NOC.error(__("Failed to connect objects : ") + response.responseText);
            }
        });
    },
    showMenu: function(event) {
        var canvas = Ext.ComponentQuery.query("#canvas")[0];

        if(canvas.selectedSprite) {
            canvas.isMenuOpen = true;
            event.preventDefault();
            canvas.up().menu.showAt(event.pageX, event.pageY);
        }
    },
    deleteInternalConnection: function() {
        var drawPanel = Ext.ComponentQuery.query("#canvas")[0],
            sprite = drawPanel.selectedSprite;
        console.log("deleteInternalConnection", sprite.fromPortId, sprite.toPortId, this);
        drawPanel.selectedSprite.setAttributes(drawPanel.selectedWire);
        drawPanel.renderFrame();
        Ext.Msg.confirm(__("Confirm"), __("Are you sure you want to delete this connection") + " " + sprite.fromPort + "=>" + sprite.toPort, function(btn) {
            if(btn === "yes") {
                sprite.remove();
                drawPanel.renderFrame();
            }
        });
    },
    onMouseMove: function(event) {
        var me = this;
        if(me.getViewModel().get("rightSelectedPinId") || me.getViewModel().get("leftSelectedPinId")) {
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
        this.getViewModel().set("leftSelectedPin", null);
        this.getViewModel().set("leftSelectedPinId", null);
        this.getViewModel().set("leftIsInternalConnection", null);
        this.getViewModel().set("rightSelectedPin", null);
        this.getViewModel().set("rightSelectedPinId", null);
        this.getViewModel().set("rightIsInternalConnection", null);
    },
    isConnectionExist: function(labelAlign, prevPinId, currPinId) {
        var me = this;
        console.log(me);
    },
    cancelDrawConnection: function() {
        var canvas = Ext.ComponentQuery.query("#canvas")[0],
            pointer = canvas.getSurface().get("pointer");

        if(pointer) {
            pointer.remove();
            canvas.getSurface().renderFrame();
        }
    }
});
