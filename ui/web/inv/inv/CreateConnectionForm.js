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
    requires: [
        "NOC.core.Pin",
        "NOC.core.ComboBox"
    ],
    viewModel: {
        data: {
            leftObject: null,
            rightObject: null,
            leftSelectedPin: null,
            rightSelectedPin: null,
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
                spriteclick: me.onSpriteClick
            },
            plugins: ["spriteevents"]
        });
        me.cableCombo = Ext.create({
            xtype: "core.combo",
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
            cabel = mainPanel.cableCombo.getValue(),
            leftSelected = mainPanel.getViewModel().get("leftSelectedPin"),
            rightSelected = mainPanel.getViewModel().get("rightSelectedPin"),
            leftObject = mainPanel.getViewModel().get("leftObject"),
            rightObject = mainPanel.getViewModel().get("rightObject");

        title = leftObject.get("name") + " <==> " + (rightObject ? rightObject.get("name") : __("none"));
        mainPanel.setTitle(title);
        params = "o1=" + leftObject.get("id") + (rightObject ? "&o2=" + rightObject.get("id") : "");
        params += leftSelected ? "&left_filter=" + leftSelected : "";
        params += rightSelected ? "&right_filter=" + rightSelected : "";
        params += cabel ? "&cable_filter=" + cabel : "";
        mainPanel.mask(__("Loading..."));
        Ext.Ajax.request({
            url: "/inv/inv/crossing_proposals/?" + params,
            method: "GET",
            success: function(response) {
                var data = Ext.decode(response.responseText),
                    maxPins = Math.max(data.left.connections.length, data.right.connections.length),
                    isValid = function(pins, name) {
                        return Ext.each(pins, function(pin) {
                            return pin.valid;
                        });
                    };

                mainPanel.unmask();
                NOC.msg.complete(__("The data was successfully loaded"));
                mainPanel.drawPanel.getSurface().removeAll();
                if(!isValid(data.right.connections, rightSelected)) {
                    mainPanel.getViewModel().set("rightSelectedPin", null);
                }
                if(!isValid(data.left.connections, leftSelected)) {
                    mainPanel.getViewModel().set("leftSelectedPin", null);
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
                enabled = true;

            if(!port.free) {
                color = me.OCCUPIED_COLOR;
            }
            if(!port.valid) {
                color = me.INVALID_COLOR;
                enabled = false;
            }
            sprites.push({
                type: "pin",
                boxWidth: boxWidth,
                boxHeight: boxHeight,
                fontSize: 12,
                pinName: port.name,
                pinColor: color,
                isSelected: port.name === selectedPin,
                enabled: enabled,
                labelAlign: labelAlign,
                x: xOffset,
                y: index * (boxHeight + gap) + gap
            });
        }, me);
        // add legend
        sprites = sprites.concat(me.legend(__("Free and valid slot"), me.AVAILABLE_COLOR, 2.5, containerHeight));
        sprites = sprites.concat(me.legend(__("Occupied slot"), me.OCCUPIED_COLOR, 250, containerHeight));
        sprites = sprites.concat(me.legend(__("Invalid slot"), me.INVALID_COLOR, 500, containerHeight));
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
        console.log("beforeDestroy");
        var me = this,
            target = me.formPanelDropTarget;
        if(target) {
            target.unreg();
            me.formPanelDropTarget = null;
        }
        this.callParent();
    },
    onSpriteMouseOver: function(pin, event, args) {
        if(pin.sprite.type === "pin" && pin.sprite.enabled) {
            pin.sprite.setAttributes({
                scale: 1.02
            });
        }
    },
    onSpriteMouseOut: function(pin, event, args) {
        if(pin.sprite.type === "pin") {
            pin.sprite.setAttributes({
                scale: 1
            });
        }
    },
    onSpriteClick: function(pin, event) {
        var mainPanel = this.up();

        if(!pin.sprite.enabled) {
            return;
        }
        if(pin.sprite.labelAlign === "left") {
            mainPanel.getViewModel().set("leftSelectedPin", mainPanel.deSelectPin(pin, mainPanel.getViewModel().get("leftSelectedPin"), "left"));
            console.log(mainPanel.getViewModel().get("leftSelectedPin"));
        }
        if(pin.sprite.labelAlign === "right") {
            mainPanel.getViewModel().set("rightSelectedPin", mainPanel.deSelectPin(pin, mainPanel.getViewModel().get("rightSelectedPin"), "right"));
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
        me.getViewModel().set("rightSelectedPin", null);
        me.drawPanel.getSurface().removeAll(true);
        me.drawPanel.getSurface().renderFrame();
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
            param = {
                object: leftObject,
                name: leftPin,
                remote_object: rightObject,
                remote_name: rightPin,
            };

        if(cable) {
            param.cable = cable;
        }
        console.log("connect :", param);
        Ext.Ajax.request({
            url: "/inv/inv/connect/",
            method: "POST",
            jsonData: param,
            scope: me,
            success: function(response) {
                var data = Ext.decode(response.responseText);
                console.log(data);
                NOC.msg.complete(__("Objects was successfully connected"));
            },
            failure: function(response) {
                NOC.error(__("Failed to connect objects : ") + response.responseText);
            }
        });

    }
});
