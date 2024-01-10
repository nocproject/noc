//---------------------------------------------------------------------
// inv.inv CreateConnection form
//---------------------------------------------------------------------
// Copyright (C) 2007-2020 The NOC Project
// See LICENSE for details
//---------------------------------------------------------------------
console.debug("Defining NOC.inv.inv.CreateConnectionForm");

Ext.define("NOC.inv.inv.CreateConnectionForm", {
    extend: "Ext.panel.Panel",
    region: "center",
    layout: "fit",
    border: false,
    scrollable: true,
    app: null,
    AVAILABLE_COLOR: "#2c3e50",
    OCCUPIED_COLOR: "lightgray",
    INVALID_COLOR: "lightcoral",
    WIRE_COLOR: "#1F6D91",
    SELECTED_WIRE_COLOR: "#f5d63c",
    requires: [
        "NOC.core.Pin",
        "NOC.core.PinInternal",
        "NOC.core.ComboBox"
    ],
    viewModel: {
        data: {
            leftObject: null,
            rightObject: null,
            leftSelectedPin: null,
            leftSelectedPinId: null,
            rightSelectedPin: null,
            rightSelectedPinId: null,
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
            region: "center",
            scrollable: false,
            sprites: [],
            listeners: {
                spritemouseover: me.onSpriteMouseOver,
                spritemouseout: me.onSpriteMouseOut,
                spriteclick: me.onSpriteClick,
                scope: me,
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
                me.drawPanel,
                me.legendPanel
            ],
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
                var data = Ext.decode(response.responseText),
                    maxPins = Math.max(data.left.connections.length, data.right.connections.length),
                    isValid = function(pins, name) {
                        return Ext.each(pins, function(pin) {
                            if(pin.name === name) {
                                return pin.valid;
                            }
                        });
                    };

                mainPanel.unmask();
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
                mainPanel.drawPanel.getSurface().add(
                    mainPanel.drawObject(data.left.connections,
                        mainPanel.getWidth() / 2 - 100,
                        "left",
                        maxPins));
                if(rightObject) {
                    mainPanel.drawPanel.getSurface().add(
                        mainPanel.drawObject(data.right.connections,
                            mainPanel.getWidth() / 2 + 100,
                            "right", maxPins));
                    mainPanel.drawPanel.getSurface().add(mainPanel.drawWire(data.wires));
                }
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
    drawObject: function(ports, xOffset, labelAlign, maxPins) {
        var me = this,
            selectedPin = me.getViewModel().get(labelAlign + "SelectedPin"),
            containerHeight = me.drawPanel.getHeight() - 20, // 20 is legend height
            boxWidth = 20,
            boxHeight = 20,
            gap = 7.5,
            surfaceHeight = maxPins * (boxHeight + gap) + gap,
            scale = 1,
            sprites = [];

        if(surfaceHeight > containerHeight) {
            scale = containerHeight / surfaceHeight;
            boxHeight *= scale;
            boxWidth *= scale;
            gap *= scale;
        }
        Ext.each(ports, function(port, index) {
            var color = me.AVAILABLE_COLOR,
                name = port.name,
                remoteId = "none",
                remoteName = "none"
            enabled = true;

            if(!port.free) {
                color = me.OCCUPIED_COLOR;
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
                color = me.INVALID_COLOR;
                enabled = false;
            }
            sprites.push({
                type: "pin",
                id: port.id,
                boxWidth: boxWidth,
                boxHeight: boxHeight,
                fontSize: 12,
                pinName: name,
                pinColor: color,
                isSelected: port.name === selectedPin,
                remoteId: remoteId,
                remoteName: remoteName,
                enabled: enabled,
                labelAlign: labelAlign,
                x: xOffset,
                y: index * (boxHeight + gap) + gap,
                zIndex: 5
            });
            if(port.allow_internal) {
                sprites.push({
                    type: "pininternal",
                    boxWidth: boxWidth,
                    boxHeight: boxHeight,
                    fontSize: 12,
                    x: xOffset - boxWidth - 5,
                    y: index * (boxHeight + gap) + gap + boxHeight / 2,
                    zIndex: 5
                });
            }
        }, me);
        // add legend
        sprites = sprites.concat(me.legend(__("Free and valid slot"), me.AVAILABLE_COLOR, 2.5, containerHeight));
        sprites = sprites.concat(me.legend(__("Occupied slot"), me.OCCUPIED_COLOR, 250, containerHeight));
        sprites = sprites.concat(me.legend(__("Invalid slot"), me.INVALID_COLOR, 500, containerHeight));
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
                type: 'line',
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
    selectPin: function(pinName, value) {
        var me = this;

        Ext.each(me.drawPanel.getSurface().getItems(), function(sprite) {
            if(sprite.attr.pinName === pinName) {
                sprite.setAttributes({
                    isSelected: value
                })
            }
        });
    },
    deSelectPin: function(pin, selectedPin, side) {
        if(selectedPin && pin.sprite.labelAlign === side && selectedPin !== pin.sprite.attr.pinName) {
            this.selectPin(selectedPin, false); // deselect by name
        }
        if(pin.sprite.attr.isSelected) {
            return null;
        }
        return pin.sprite.attr.pinName;
    },
    beforeDestroy: function() {
        var me = this,
            target = me.formPanelDropTarget;
        if(target) {
            target.unreg();
            me.formPanelDropTarget = null;
        }
        this.callParent();
    },
    onSpriteMouseOver: function(pin, event, args) {
        var me = this;

        if(pin.sprite.type === "pin") {
            pin.sprite.setAttributes({
                scale: 1.02,
                labelBold: true,
            });
            Ext.each(me.drawPanel.getSurface().getItems(), function(sprite) {
                if(sprite.config.leftPortId === pin.sprite.id || sprite.config.rightPortId === pin.sprite.id) {
                    sprite.setAttributes({
                        strokeStyle: me.SELECTED_WIRE_COLOR,
                        lineWidth: 4,
                        zIndex: 100,
                    });
                    me.drawPanel.getSurface().renderFrame();
                    return false;
                }
            });
        }
    },
    onSpriteMouseOut: function(pin, event, args) {
        var me = this;

        if(pin.sprite.type === "pin") {
            pin.sprite.setAttributes({
                scale: 1,
                labelBold: false,
            });
            Ext.each(me.drawPanel.getSurface().getItems(), function(sprite) {
                if(sprite.config.leftPortId === pin.sprite.id || sprite.config.rightPortId === pin.sprite.id) {
                    sprite.setAttributes({
                        strokeStyle: me.WIRE_COLOR,
                        lineWidth: 2,
                        zIndex: 10,
                    });
                    me.drawPanel.getSurface().renderFrame();
                }
            });
        }
    },
    onSpriteClick: function(pin, event) {
        var mainPanel = this;

        if(pin.sprite.remoteId !== "none") {
            var leftObject, rightObject;
            if(pin.sprite.config.labelAlign === "left") {
                leftObject = mainPanel.getViewModel().get("leftObject");
                rightObject = Ext.create("Ext.data.Model", {id: pin.sprite.remoteId, name: pin.sprite.remoteName});
            } else {
                rightObject = mainPanel.getViewModel().get("rightObject");
                leftObject = Ext.create("Ext.data.Model", {id: pin.sprite.remoteId, name: pin.sprite.remoteName});
            }
            mainPanel.getViewModel().set("leftObject", rightObject);
            mainPanel.getViewModel().set("rightObject", leftObject);
            mainPanel.getViewModel().set("leftSelectedPin", null);
            mainPanel.getViewModel().set("rightSelectedPin", null);
            mainPanel.load();
            return;
        }
        if(!pin.sprite.enabled) {
            return;
        }
        if(pin.sprite.labelAlign === "left") {
            mainPanel.getViewModel().set("leftSelectedPin", mainPanel.deSelectPin(pin, mainPanel.getViewModel().get("leftSelectedPin"), "left"));
            mainPanel.getViewModel().set("leftSelectedPinId", pin.sprite.id);
        }
        if(pin.sprite.labelAlign === "right") {
            mainPanel.getViewModel().set("rightSelectedPin", mainPanel.deSelectPin(pin, mainPanel.getViewModel().get("rightSelectedPin"), "right"));
            mainPanel.getViewModel().set("rightSelectedPinId", pin.sprite.id);
        }
        pin.sprite.setAttributes({
            isSelected: !pin.sprite.attr.isSelected
        });
        mainPanel.load();
    },
    onCleanClick: function() {
        var me = this;

        me.setTitle(__("Object connections"));
        me.getViewModel().set("leftObject", null);
        me.getViewModel().set("rightObject", null);
        me.getViewModel().set("leftSelectedPin", null);
        me.getViewModel().set("leftSelectedPinId", null);
        me.getViewModel().set("rightSelectedPin", null);
        me.getViewModel().set("rightSelectedPinId", null);
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
    }
});
