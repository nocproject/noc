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
  layout: "absolute",
  border: false,
  scrollable: true,
  app: null,
  itemId: "invConnectionForm",
  AVAILABLE_COLOR: NOC.colors.yes,
  OCCUPIED_COLOR: NOC.colors.carrot,
  INVALID_COLOR: NOC.colors.clouds,
  UNMASKED_LABEL_COLOR: NOC.colors.black,
  MASKED_LABEL_COLOR: NOC.colors.asbestos,
  legendHeight: 20,
  firstTrace: 3,
  requires: [
    "NOC.inv.inv.sprites.Body",
    "NOC.core.ComboBox",
    "NOC.inv.inv.sprites.Connection",
    "NOC.inv.inv.sprites.External",
    "NOC.inv.inv.sprites.Pin",
    "NOC.inv.inv.sprites.Pointer",
    "NOC.core.ConnectionGraph",
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
      connectButtonDisabled: true,
    },
  },
  initValues: function(){
    var me = this;
    me.boxWidth = 10;
    me.boxHeight = 10;
    me.schemaPadding = 30; // boxHeight * 3,
    me.gap = 6.75;
    me.scale = 0.5;
    me.discriminatorWidth = {
      left: -75.5, right: 75.5,
    };
    me.arrowLength = me.boxWidth * 5;
    me.drawPanelSize = {
      w: 0,
      h: 0,
    };
    me.betweenSpace = 450;
    me.toolTipOffset = 40;
  },
  initComponent: function(){
    var me = this;
    me.flag = 0;
    me.initValues();
    me.drawPanel = Ext.create({
      xtype: "draw",
      itemId: "canvas",
      region: "center",
      scrollable: false,
      isModalOpen: false, // event mouseOut is fired when modal window is open
      sprites: [],
      listeners: {
        spritemouseover: me.onSpriteMouseOver,
        spritemouseout: me.onSpriteMouseOut,
        spriteclick: me.onSpriteClick,
        scope: me,
        boxready: me.drawEmptyText,
        afterrender: function(container){
          container.getEl().on("keydown", me.cancelDrawConnection);
          container.getEl().set({
            tabIndex: 0,
            focusable: true,
          });
          container.getEl().focus();
        },
      },
      plugins: ["spriteevents"],
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
          cls: "x-form-clear-trigger",
          hidden: true,
          weight: -1,
          handler: function(field){
            field.setValue(null);
            field.fireEvent("select", field);
          },
        },
      },
      store: {
        fields: ["name", "available"],
        data: [],
      },
      bind: {
        disabled: "{!leftObject}",
        value: "{cable}",
      },
      listeners: {
        scope: me,
        change: Ext.Function.bind(me.reloadStatuses, me, [true], false),
      },
    });
    Ext.apply(me, {
      title: __("Object connections"),
      titleAlign: "center",
      items: [
        me.drawPanel,
      ],
      listeners: {
        element: "el",
        scope: me,
        mousemove: this.onMouseMove,
      },
      tbar: [
        {
          text: __("Save"),
          scope: me,
          glyph: NOC.glyph.save,
          bind: {
            disabled: "{!isDirty}",
          },
          handler: me.onSaveClick,
        },
        {
          text: __("Close"),
          itemId: "closeBtn",
          scope: me,
          glyph: NOC.glyph.arrow_left,
          handler: me.onCloseClick,
        },
        {
          glyph: NOC.glyph.eraser,
          scope: me,
          handler: me.onCleanClick,
          tooltip: __("Clear objects"),
          bind: {
            disabled: "{!leftObject}",
          },
        },
        {
          glyph: NOC.glyph.refresh,
          scope: me,
          handler: me.onReload,
          tooltip: __("Repaint"),
          bind: {
            disabled: "{!leftObject}",
          },
        },
        me.cableCombo,
        {
          glyph: NOC.glyph.arrows_h,
          scope: me,
          handler: me.connectPort,
          tooltip: __("Connect ports"),
          bind: {
            disabled: "{connectButtonDisabled}",
          },
        },
      ],
    });
    me.callParent();
  },
  addConnectionSprite: function(button, fromSprite, toSprite, side){
    var hasDiscriminator, internalConnectionQty, calculatedWidth,
      me = this,
      internalConnectionSurface = me.drawPanel.getSurface(side + "_internal_conn"),
      mainSurface = me.drawPanel.getSurface(),
      connections = me.getInternalConnections(internalConnectionSurface),
      body = mainSurface.get(side + "Body"),
      win = button.up("window"),
      gainDb = win.down("[name=gainDb]").getValue(),
      fromDiscriminator = win.down("[name=fromDiscriminator]").getValue() || undefined,
      toDiscriminator = win.down("[name=toDiscriminator]").getValue() || undefined,
      pinDisabled = {internalColor: me.OCCUPIED_COLOR, internalEnabled: false, isSelected: false},
      from = {
        discriminator: fromDiscriminator,
        has_arrow: false,
        id: fromSprite.id,
        name: fromSprite.attr.pinName,
      },
      to = {
        discriminator: toDiscriminator,
        has_arrow: true,
        id: toSprite.id,
        name: toSprite.pinName,
      },
      connection = {
        gain_db: gainDb,
        is_delete: true,
        to: to,
        from: from,
        isNew: true,
      };

    fromSprite.setAttributes(pinDisabled);
    toSprite.setAttributes(pinDisabled);
    internalConnectionQty = connections.internal_connections.push(connection);
    hasDiscriminator = me.hasDiscriminator(connections.internal_connections);
    me.switchInternalLabel(body, hasDiscriminator);
    calculatedWidth = (internalConnectionQty + me.firstTrace) * me.gap + (hasDiscriminator ? Math.abs(me.discriminatorWidth[side]) : 0);
    if(body.width <= calculatedWidth){
      var increment = (side === "left" ? calculatedWidth - body.attr.width : 0);
      body.setAttributes({
        width: calculatedWidth,
        x: body.attr.x - increment,
      });
    }
    me.drawInternalConnections(connections, internalConnectionSurface, side);
  },
  beforeDestroy: function(){
    var me = this,
      target = me.formPanelDropTarget;
    if(target){
      target.unreg();
      me.formPanelDropTarget = null;
    }
    me.getEl().un("keydown", me.cancelDrawConnection);
    this.callParent();
  },
  cancelDrawConnection: function(){
    var canvas = Ext.ComponentQuery.query("#canvas")[0],
      viewModel = canvas.up().getViewModel(),
      surface = canvas.getSurface(),
      id = viewModel.get("selectedPinId"),
      pointer = surface.get("pointer");

    Ext.Array.each(surface.getItems(), function(element){
      if(element.attr.isSelected) element.setAttributes({isSelected: false, pinOver: false});
    });
    if(id){
      canvas.up().reloadStatuses(false);
    }
    viewModel.set("selectedPin", null);
    viewModel.set("selectedPinId", null);
    viewModel.set("isSelectedPinInternal", null);
    if(pointer){
      pointer.remove();
    }
    canvas.getSurface().renderFrame();
  },
  checkAvailabilityConnection: function(){
    var vm = this.getViewModel();
    vm.set("connectButtonDisabled", true);
    if(Ext.isEmpty(vm.get("cable"))) return;
    if(Ext.isEmpty(vm.get("rightObject"))) return;
    var enabledPorts = Ext.Array.filter(this.drawPanel.getSurface().getItems(), function(sprite){
        return sprite.type === "pin" && sprite.enabled;
      }),
      rxTxPorts = Ext.Array.filter(enabledPorts, function(sprite){
        return sprite.pinName === "rx" || sprite.pinName === "tx";
      });
    if(rxTxPorts.length !== 4) return;
    vm.set("connectButtonDisabled", false);
  },
  cleanForm: function(){
    var me = this;
    me.initValues();
    me.setTitle(__("Object connections"));
    me.cleanViewModel();
    me.drawPanel.setHeight(me.body.getHeight()); // parent panel height
    me.drawPanel.setWidth(me.body.getWidth());
    me.drawPanel.removeAll(true);
    me.drawPanel.renderFrame();
    me.drawEmptyText(me.drawPanel);
  },
  cleanViewModel: function(){
    var vm = this.getViewModel();
    vm.set("leftObject", null);
    vm.set("rightObject", null);
    vm.set("selectedPin", null);
    vm.set("selectedPinId", null);
    vm.set("isSelectedPinInternal", null);
    vm.set("cable", null);
    vm.set("isDirty", false);
    vm.set("connectButtonDisabled", true);
  },
  createInternalConnectionMsg: function(fromSprite, toSprite, side){
    var me = this,
      mainSurface = me.drawPanel.getSurface(),
      fromDiscriminators = fromSprite.allowDiscriminators,
      toDiscriminators = toSprite.allowDiscriminators;

    me.drawPanel.isModalOpen = true;
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
      items: me.itemsForConnectionParamsForm(fromDiscriminators, toDiscriminators, "createBtn"),
      buttons: [
        {
          text: __("Create"),
          reference: "createBtn",
          handler: function(button){
            me.addConnectionSprite(button, fromSprite, toSprite, side);
            me.getViewModel().set("isDirty", true);
            mainSurface.renderFrame();
            button.up("window").close();
          },
        },
        {
          text: __("Cancel"),
          handler: function(){
            this.up("window").close();
          },
        },
      ],
      listeners: {
        close: function(){
          me.reloadStatuses(true);
          me.drawPanel.isModalOpen = false;
        },
      },
    });
  },
  connectPort: function(){
    var leftRx, leftTx, rightRx, rightTx,
      enabledPorts = Ext.Array.filter(this.drawPanel.getSurface().getItems(), function(sprite){
        return sprite.type === "pin" && sprite.enabled;
      }),
      rxTxPorts = Ext.Array.filter(enabledPorts, function(sprite){
        return sprite.pinName === "rx" || sprite.pinName === "tx";
      });
    for(var i = 0; i < rxTxPorts.length; i++){
      if(rxTxPorts[i].side === "left"){
        if(rxTxPorts[i].pinName === "rx"){
          leftRx = rxTxPorts[i];
        } else{
          leftTx = rxTxPorts[i];
        }
      } else{
        if(rxTxPorts[i].pinName === "rx"){
          rightRx = rxTxPorts[i];
        } else{
          rightTx = rxTxPorts[i];
        }
      }
    }
    this.createWire(leftTx, rightRx);
    this.createWire(rightTx, leftRx);
    this.getViewModel().set("connectButtonDisabled", true);
  },
  createWire: function(prevPinSprite, pinSprite){
    var me = this,
      cable = me.cableCombo.getValue(),
      mainSurface = me.drawPanel.getSurface(),
      wires = me.getWires(mainSurface),
      fromName = prevPinSprite.pinName,
      toName = pinSprite.pinName,
      wire = [
        {id: pinSprite.id, side: pinSprite.side, isNew: true, cable: cable},
        {id: prevPinSprite.id, side: prevPinSprite.side, isNew: true, cable: cable},
      ];
    prevPinSprite.setAttributes({
      pinColor: me.OCCUPIED_COLOR,
      enabled: false,
      isSelected: false,
      pinOver: false,
      pinName: fromName,
    });
    pinSprite.setAttributes({
      pinColor: me.OCCUPIED_COLOR,
      enabled: false,
      isSelected: false,
      pinOver: false,
      pinName: toName,
    });
    wires.push(wire);
    me.drawWires(wires, mainSurface);
    me.getViewModel().set("isDirty", true);

  },
  disconnectConnection: function(params, callBack){
    Ext.Ajax.request({
      url: "/inv/inv/disconnect/",
      method: "POST",
      jsonData: params,
      scope: this,
      success: function(){
        this.fireEvent("reloadInvNav");
        callBack();
      },
      failure: function(response){
        NOC.error(__("Failed to disconnect objects : ") + response.responseText);
      },
    });
  },
  drawEmptyText: function(container){
    var text = __("Drag other object from left tree"),
      minLeftWidth = 230, // min width = Ext.draw.TextMeasurer.measureText(text, font).width
      fontSize = 16,
      offset = this.schemaPadding * 0.5,
      color = window.getComputedStyle(container.up("panel").down("button[itemId=closeBtn]").btnIconEl.dom).color,
      parent = container.up("panel").body,
      width = parent.getWidth(),
      height = parent.getHeight(),
      font = Ext.String.format("normal {0}px arial", fontSize),
      squareSprite = {
        type: "rect",
        x: offset,
        y: offset,
        width: width - offset * 2,
        height: height - offset * 2,
        fillStyle: "none",
        strokeStyle: color,
        lineWidth: 3,
        lineDash: [10, 10],
        radius: 20,
      },
      textSprite = {
        type: "text",
        text: text,
        x: width / 2,
        y: height / 2 - fontSize,
        fillStyle: color,
        textAlign: "center",
        font: font,
      };
    if(Ext.isEmpty(this.getViewModel().get("leftObject"))){
      container.getSurface().removeAll(true);
    } else if(Ext.isEmpty(this.getViewModel().get("rightObject"))){
      this.drawPanelSize.w = parent.dom.clientWidth;  
      var remoteLength = this.getWiresOffset("left", "right", true),
        x = this.bodiesWidth.left + remoteLength[0] + this.arrowLength,
        squareWidth = this.drawPanelSize.w - x - offset * 2;

      if(squareWidth < minLeftWidth){
        this.drawPanelSize.w += minLeftWidth - squareWidth;
        squareWidth = minLeftWidth;
      }
      offset = this.schemaPadding * 0.5;
      squareSprite.x = x;
      squareSprite.y = offset;
      squareSprite.width = squareWidth;
      textSprite.x = squareSprite.x + squareSprite.width / 2;
      textSprite.y = squareSprite.height * 0.5;
    }
    container.getSurface().add(squareSprite, textSprite);
    container.getSurface().renderFrame();
  },
  drawInternalConnections: function(data, surface, side){
    var me = this;
    // surface => (left|right) + _internal_conn
    surface.removeAll(true);
    surface.add(me.makeInternalConnections(data.internal_connections, side));
    surface.renderFrame();
  },
  drawLegend: function(surface, height){
    surface.add(this.makeLegend(__("Free slot"), this.AVAILABLE_COLOR, 10, height));
    surface.add(this.makeLegend(__("Occupied slot"), this.OCCUPIED_COLOR, 115, height));
  },
  drawObject: function(pins, surface, side, hasDiscriminator){
    var me = this;

    surface.add(me.makePins(pins, side, hasDiscriminator));
    surface.add(me.makeExternalConnection(pins, side));
    surface.add(me.makeBody(pins, side));
  },
  drawWires: function(wires, surface){
    var me = this,
      wiresToRemove = Ext.Array.filter(surface.getItems(), function(sprite){
        return sprite.type === "connection";
      });

    Ext.Array.each(wiresToRemove, function(sprite){
      sprite.remove();
    });
    surface.add(me.makeWires(wires));
    surface.renderFrame();
  },
  flattenArray: function(array){
    var me = this,
      result = [];

    array.forEach(function(item){
      if(Ext.isArray(item)){
        result = result.concat(me.flattenArray(item));
      } else{
        result.push(item);
      }
    });

    return result;
  },
  getBodyWidth: function(me, pins, side){
    return (this.internalPinQty(pins) + 1) * me.gap + Math.abs(me.discriminatorWidth[side]);
  },
  getConnectionById: function(sprite){
    var surface,
      me = this;
    if(sprite.connectionType === "internal"){
      surface = me.drawPanel.getSurface(sprite.fromSide + "_internal_conn");
    }
    if(Ext.Array.contains(["wire", "loopback"], sprite.connectionType)){
      surface = me.drawPanel.getSurface();
    }
    return surface.get(sprite.fromPortId + "_" + sprite.toPortId);
  },
  getInternalConnections: function(surface){
    return {
      internal_connections: Ext.Array.map(surface.getItems(), function(sprite){
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
          is_delete: sprite.attr.isDeleted,
        }
      }),
    }
  },
  getWires: function(surface){
    return Ext.Array.map(
      Ext.Array.filter(surface.getItems(), function(sprite){return sprite.type === "connection"}),
      function(wire){
        return [
          {id: wire.fromPortId, side: wire.fromSide, cable: wire.cable, isNew: wire.isNew},
          {id: wire.toPortId, side: wire.toSide, cable: wire.cable, isNew: wire.isNew},
        ]
      });
  },
  getWiresOffset: function(firstSide, secondSide, isLabel){
    var me = this,
      mainSurface = me.drawPanel.getSurface(),
      sprites = mainSurface.getItems(),
      firstPins = Ext.Array.filter(sprites, function(sprite){return sprite.type === "pin" && sprite.side === firstSide}),
      secondPins = secondSide ? Ext.Array.filter(sprites, function(sprite){return sprite.type === "pin" && sprite.side === secondSide}) : [{pinNameWidth: 0}],
      firstNameWidthMax = Ext.Array.max(Ext.Array.map(firstPins, function(pin){return pin.pinNameWidth})) + me.boxWidth,
      secondNameWidthMax = (Ext.Array.max(Ext.Array.map(secondPins, function(pin){return pin.pinNameWidth})) || 0) + me.boxWidth;

    if(isLabel){
      firstNameWidthMax += Ext.Array.max(Ext.Array.map(firstPins, function(pin){return pin.remoteSlotWidth + me.boxWidth}));
      secondNameWidthMax += (Ext.Array.max(Ext.Array.map(secondPins, function(pin){return pin.remoteSlotWidth + me.boxWidth})) || 0);
    }
    return [firstNameWidthMax, secondNameWidthMax];
  },
  goToObject: function(leftId, leftName, side){
    var me = this,
      viewModel = me.getViewModel(),
      object = viewModel.get(side + "Object");
    
    if(side === "left"){
      viewModel.set("leftObject", Ext.data.Model.create({
        id: leftId,
        name: leftName,
      }));
      viewModel.set("rightObject", Ext.data.Model.create({
        id: object.id,
        name: object.get("name"),
      }));
    } else{
      viewModel.set("leftObject", Ext.data.Model.create({
        id: object.id,
        name: object.get("name"),
      }));
      viewModel.set("rightObject", Ext.data.Model.create({
        id: leftId,
        name: leftName,
      }));
    }
    me.load();

  },
  hasDiscriminator: function(connections){
    var hasDiscriminator = false;
    Ext.each(connections, function(connection){
      if(!Ext.isEmpty(connection.from.discriminator) || !Ext.isEmpty(connection.to.discriminator)){
        hasDiscriminator = true;
        return false;
      }
    });
    return hasDiscriminator;
  },
  internalPinQty: function(pins){
    return Ext.Array.filter(pins, (function(pin){return pin.internal;})).length || 1;
  },
  isPinAvailableForSelect: function(sprite){
    // check is mouse over pin available to make connection
    var me = this,
      viewModel = me.getViewModel(),
      firstSelectedPinId = viewModel.get("selectedPinId"),
      firstIsSelectedPinInternal = viewModel.get("isSelectedPinInternal"),
      firstSide = viewModel.get("side"),
      isSelectedPinInternal = sprite.attr.cursorOn === "internal";

    if(!firstSelectedPinId){ // no pin selected
      return false;
    }
    if(isSelectedPinInternal && firstSide !== sprite.side){
      return false;
    }
    if(isSelectedPinInternal === !firstIsSelectedPinInternal){
      return false;
    }
    if(!isSelectedPinInternal && !sprite.enabled){
      return false;
    }
    if(isSelectedPinInternal && !sprite.internalEnabled){
      return false;
    }
    return true;
  },
  itemsForConnectionParamsForm: function(fromDiscriminators, toDiscriminators, validateBtn, values){
    var fromDiscriminator = values ? values.fromDiscriminator : '',
      toDiscriminator = values ? values.toDiscriminator : '',
      gainDb = values ? values.gainDb : 0,
      setTriggers = function(value){
        return {
          clear: {
            cls: 'x-form-clear-trigger',
            hidden: Ext.isEmpty(value),
            weight: -1,
            handler: function(field){
              field.setValue(null);
              field.fireEvent("select", field);
            },
          },
        }
      },
      listeners = {
        change: function(field, value){
          if(value){
            field.getTrigger("clear").show();
          } else{
            field.getTrigger("clear").hide();
          }
        },
      },
      items = [
        {
          xtype: "combobox",
          fieldLabel: __("Discriminator From"),
          store: fromDiscriminators,
          editable: false,
          disabled: !fromDiscriminators.length,
          queryMode: "local",
          name: "fromDiscriminator",
          triggers: setTriggers(fromDiscriminator),
          listeners: listeners,
          value: fromDiscriminator,
        },
        {
          xtype: "combobox",
          fieldLabel: __("Discriminator To"),
          store: toDiscriminators,
          editable: false,
          disabled: !toDiscriminators.length,
          queryMode: "local",
          name: "toDiscriminator",
          triggers: setTriggers(toDiscriminator),
          listeners: listeners,
          value: toDiscriminator,
        },
        {
          xtype: "numberfield",
          fieldLabel: __("Gain DB"),
          step: 0.1,
          minValue: 0,
          maxValue: 100,
          name: "gainDb",
          value: gainDb,
          listeners: {
            validitychange: function(field, isValid){
              field.up("window").lookupReference(validateBtn).setDisabled(!isValid);
            },
          },
        },
      ];
    return items;
  },
  load: function(){
    var me = this,
      action = function(){
        var params, title,
          cable = me.cableCombo.getValue(),
          leftObject = me.getViewModel().get("leftObject"),
          rightObject = me.getViewModel().get("rightObject"),
          leftObjectId = leftObject.get("id"),
          rightObjectId = rightObject ? rightObject.get("id") : undefined;

        if(leftObjectId === rightObjectId){
          return;
        }
        title = (leftObject ? leftObject.get("name") : __("none"))
          + "<i class='fa fa-arrows-h' style='padding: 0 5px 0 5px;'></i>"
          + (rightObject ? rightObject.get("name") : __("none"));
        me.setTitle(title);
        params = "o1=" + leftObjectId + (rightObjectId ? "&o2=" + rightObjectId : "");
        params += cable ? "&cable_filter=" + cable : "";
        me.mask(__("Loading..."));
        Ext.Ajax.request({
          url: "/inv/inv/crossing_proposals/?" + params,
          method: "GET",
          scope: me,
          success: function(response){
            var schemeHeight, bodiesWidth = {left: 0, right: 0},
              parentPanel = me.body,
              mainSurface = me.drawPanel.getSurface(),
              data = Ext.decode(response.responseText);

            me.drawPanelSize = {
              w: parentPanel.getWidth(),
              h: parentPanel.getHeight(),
            };
            me.maxPins = Math.max(data.left.connections.length, data.right.connections.length);
            schemeHeight = me.maxPins * (me.boxHeight + me.gap) + me.gap + me.schemaPadding * 2 + me.legendHeight;
            if(schemeHeight > me.drawPanelSize.h){
              me.drawPanelSize.h = schemeHeight;
            }
            me.drawPanel.setHeight(me.drawPanelSize.h);
            me.unmask();
            NOC.msg.complete(__("The data was successfully loaded"));
            mainSurface.removeAll(true);
            me.getViewModel().set("isDirty", false);
            me.cableCombo.getStore().loadData(data.cable);
            // me.scaleCalculate();
            Ext.Array.each(["left", "right"], function(side){
              if(data[side].connections && data[side].connections.length){
                var hasDiscriminator = me.hasDiscriminator(data[side].internal_connections);

                bodiesWidth[side] = me.getBodyWidth(me, data[side].connections, side);
                me.drawObject(data[side].connections, mainSurface, side, hasDiscriminator, me.maxPins);
                me.drawInternalConnections(data[side], me.drawPanel.getSurface(side + "_internal_conn"), side, hasDiscriminator);
              }
            });
            me.bodiesWidth = bodiesWidth;
            me.drawWires(data.wires, mainSurface);
            me.drawLegend(mainSurface, me.drawPanelSize.h - me.legendHeight);
            if(Ext.isEmpty(rightObjectId)){
              me.drawEmptyText(me.drawPanel);
            }
            me.drawPanel.getEl().dom.style.width = `${me.drawPanelSize.w}px`;
            me.drawPanel.getSurface().setRect([0, 0, me.drawPanelSize.w, me.drawPanelSize.h]);
            me.drawPanel.getSurface("left_internal_conn").setRect([0, 0, me.drawPanelSize.w, me.drawPanelSize.h]);
            me.drawPanel.getSurface("right_internal_conn").setRect([0, 0, me.drawPanelSize.w, me.drawPanelSize.h]);
            if(!Ext.isEmpty(rightObjectId)){
              me.checkAvailabilityConnection();
            }
            mainSurface.renderFrame();
          },
          failure: function(){
            me.unmask();
            NOC.msg.failed(__("Error loading data"));
          },
        });
      };

    if(me.getViewModel().get("isDirty")){
      Ext.Msg.confirm(__("Confirm"), __("There is unsaved data, do you really want to load the object?"), function(btn){
        if(btn === "yes"){
          action();
        }
      });
    } else{
      action();
    }
  },
  makeBody: function(pins, side){
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
      gap: me.gap,
    };
  },
  makeConnection: function(from, to, side, type, attr){
    var me = this;

    if(from.internal && to.internal){
      var f = from.internal.getBBoxCenter(),
        t = to.internal.getBBoxCenter();

      return {
        id: from.id + "_" + to.id,
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
        length: Math.abs(f[1] - t[1]),
        isNew: attr.isNew ? true : false,
        zIndex: 50,
      };
    }
  },
  makeExternalConnection: function(pins, side){
    var x = this.xOffset(side, pins),
      labelsLength = this.getWiresOffset("left", "right", true); // true doesn't include width name remote slot

    return Ext.Array.filter(Ext.Array.map(pins, function(pin, index){
      if(pin.remote_device){
        var length = labelsLength[side === "left" ? 0 : 1],
          remoteName = pin.remote_device.name || "",
          remoteSlot = pin.remote_device.slot || "",
          y = index * (this.boxHeight + this.gap) + this.gap + this.schemaPadding;

        return {
          type: "external",
          fromXY: [x, y],
          length: length,
          box: [this.boxWidth, this.boxHeight],
          side: side,
          actualScale: this.scale,
          pinColor: this.OCCUPIED_COLOR,
          remoteName: remoteName,
          remoteSlot: remoteSlot,
          remoteId: pin.remote_device.id,
          zIndex: 50,
        }
      }
      return null;
    }, this), function(item){
      return item !== null;
    });
  },
  makeInternalConnections: function(connections, side){
    var ports, me = this,
      surface = me.drawPanel.getSurface(),
      sprites = [];
      
    NOC.core.ConnectionGraph.buildGraphFromConnections(connections);
    ports = NOC.core.ConnectionGraph.getPortsWithManyLabel();
    Ext.each(ports, function(port){
      Ext.each(connections, function(connection){
        if(connection.from.id === port.id){
          connection.to.discriminator = connection.from.discriminator;
          connection.from.discriminator = "";
        }
        if(connection.to.id === port.id){
          connection.from.discriminator = connection.to.discriminator;
          connection.to.discriminator = "";
        }
      });
    });
    Ext.each(connections, function(connection){
      var conn,
        fromPin = surface.get(connection.from.id),
        toPin = surface.get(connection.to.id);

      fromPin.has_arrow = connection.from.has_arrow;
      toPin.has_arrow = connection.to.has_arrow;
      if((conn = me.makeConnection(fromPin, toPin, side, "internal", connection)) != undefined) sprites.push(conn);
    });
    return Ext.Array.map(
      Ext.Array.sort(sprites, function(a, b){
        return a.length - b.length;
      }), function(sprite, index){
        var f = sprite.fromXY,
          t = sprite.toXY,
          betweenLine = sprite.fromSide === "left" ? -1 : 1;

        sprite.trace = index + me.firstTrace;
        sprite.path = Ext.String.format("M{0},{1} L{2},{3} L{4},{5} L{6},{7}",
                                        f[0], f[1], f[0] + betweenLine * me.gap * sprite.trace, f[1], f[0] + betweenLine * me.gap * sprite.trace, t[1], t[0], t[1]);
        return sprite;
      },
    );
  },
  makeLegend: function(text, color, x, h){
    return [
      {
        type: "rect",
        width: 15,
        height: 15,
        fillStyle: color,
        stroke: "black",
        lineWidth: 2,
        x: x,
        y: h - 2.5,
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
        y: h + 5,

      },
    ]
  },
  makePins: function(pins, side, hasDiscriminator){
    var me = this,
      xOffset = me.xOffset(side, pins),
      selectedPin = me.getViewModel().get("selectedPin"),
      labelAlign = side === "left" ? "right" : "left";

    return Ext.Array.map(pins, function(port, index){
      var {
        pinColor,
        internalColor,
        name,
        remoteId,
        remoteName,
        remoteSlot,
        internalEnabled,
        enabled,
        masked,
      } = me.pinStatus(port, side);

      return {
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
        remoteSlot: remoteSlot,
        enabled: enabled,
        masked: masked,
        internalEnabled: internalEnabled,
        hasInternalLabel: hasDiscriminator,
        allowDiscriminators: port.internal ? port.internal.allow_discriminators : [],
        side: side,
        labelAlign: labelAlign,
        allowInternal: !Ext.isEmpty(port.internal),
        internalLabelWidth: me.discriminatorWidth[side],
        x: xOffset,
        y: index * (me.boxHeight + me.gap) + me.gap + me.schemaPadding,
        zIndex: 75,
      };
    }, me);
  },
  makeWire: function(firstPort, secondPort, firstSide, secondSide, firstOffset, secondOffset, isNew, cable){
    return {
      id: firstPort.id + "_" + secondPort.id,
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
      isDeleted: true,
      offset: [firstOffset, secondOffset],
      cable: cable,
      zIndex: 50,
    };
  },
  makeWires: function(wires){
    var me = this,
      mainSurface = me.drawPanel.getSurface(),
      offsetX = me.getWiresOffset("left", "right", true);

    return Ext.Array.map(wires, function(wire){
      wire = me.wireSort(wire);
      return me.makeWire(mainSurface.get(wire[0].id), mainSurface.get(wire[1].id), wire[0].side, wire[1].side, offsetX[0] + me.boxWidth * 2, offsetX[1] + me.boxWidth * 2, wire[0].isNew, wire[0].cable);
    });
  },
  onBoxReady: function(){
    this.callParent(arguments);
    var me = this,
      body = me.body;

    me.formPanelDropTarget = new Ext.dd.DropTarget(body, {
      ddGroup: "navi-tree-to-form",
      notifyEnter: function(){
        body.stopAnimation();
        body.highlight();
      },
      notifyDrop: Ext.bind(me.onDrop, me),
    });
  },
  onCleanClick: function(){
    var me = this;

    if(me.getViewModel().get("isDirty")){
      Ext.Msg.confirm(__("Confirm"), __("There is unsaved data, do you really want to clean?"), function(btn){
        if(btn === "yes"){
          me.cleanForm();
        }
      });
    } else{
      me.cleanForm();
    }
  },
  onCloseClick: function(){
    var me = this,
      action = function(){
        me.cleanForm();
        me.app.mainPanel.remove(me.app.connectionPanel, false);
        me.app.mainPanel.add(me.app.tabPanel);
      };

    me.fireEvent("reloadInvNav");
    if(me.getViewModel().get("isDirty")){
      Ext.Msg.confirm(__("Confirm"), __("There is unsaved data, do you really want to close the application?"), function(btn){
        if(btn === "yes"){
          action();
        }
      });
    } else{
      action();
    }
  },
  onDrop: function(ddSource){
    var me = this,
      selectedRecord = ddSource.dragData.records[0];

    if(me.getViewModel().get("leftObject")){
      me.getViewModel().set("rightObject", selectedRecord);
    }
    if(!me.getViewModel().get("leftObject")){
      me.getViewModel().set("leftObject", selectedRecord);
    }
    this.load();
    return true;
  },
  onMouseMove: function(event){
    var me = this;
    if(me.getViewModel().get("selectedPinId")){
      var surface = me.drawPanel.getSurface(),
        pointer = surface.get("pointer");
      if(pointer){
        var surfaceEl = surface.el.dom,
          surfaceXY = Ext.fly(surfaceEl).getXY();

        pointer.setAttributes({
          toX: event.pageX - surfaceXY[0],
          toY: event.pageY - surfaceXY[1],
        });
        me.drawPanel.getSurface().renderFrame();
      }
    }
  },
  onReload: function(){
    this.load();
  },
  onSaveClick: function(){
    var params, ObjectIds = {left: undefined, right: undefined},
      me = this,
      vm = me.getViewModel(),
      mainSurface = me.drawPanel.getSurface(),
      leftSurface = me.drawPanel.getSurface("left_internal_conn"),
      rightSurface = me.drawPanel.getSurface("right_internal_conn"),
      leftObject = vm.get("leftObject"),
      rightObject = vm.get("rightObject"),
      newWires = Ext.Array.filter(mainSurface.getItems(), function(sprite){return sprite.type === "connection" && sprite.isNew}),
      leftInternal = Ext.Array.filter(leftSurface.getItems(), function(sprite){return sprite.type === "connection" && sprite.isNew}),
      rightInternal = Ext.Array.filter(rightSurface.getItems(), function(sprite){return sprite.type === "connection" && sprite.isNew}),
      connections = leftInternal.concat(newWires).concat(rightInternal);

    ObjectIds.left = leftObject.get("id");
    if(rightObject){
      ObjectIds.right = rightObject.get("id");
    } else{
      ObjectIds.right = ObjectIds.left;
    }

    params = Ext.Array.map(connections, function(connection){
      var param = {
        name: connection.fromPort,
        remote_name: connection.toPort,
        is_internal: connection.connectionType === "internal",
        object: ObjectIds[connection.fromSide],
        remote_object: ObjectIds[connection.toSide],
      };

      if(connection.toDiscriminator || connection.fromDiscriminator){
        param.discriminator = {};
        if(connection.toDiscriminator){
          param.discriminator.output = connection.toDiscriminator;
        }
        if(connection.fromDiscriminator){
          param.discriminator.input = connection.fromDiscriminator;
        }
      }
      if(connection.gainDb != undefined){
        param.gain_db = connection.gainDb;
      }
      if(connection.cable != "null"){ // ExtJS converts values all properties to string
        param.cable = connection.cable;
      }
      if(param.object === param.remote_object){
        delete param.remote_object;
      }
      return param;
    });
    Ext.Ajax.request({
      url: "/inv/inv/connect/",
      method: "POST",
      jsonData: params,
      scope: me,
      success: function(response){
        var invalidConnections,
          data = Ext.decode(response.responseText);

        vm.set("isDirty", false);
        if(data && data.status){
          NOC.msg.complete(__("Objects was successfully connected"));
          this.fireEvent("reloadInvNav");
        } else{
          NOC.error(__("Failed to connect objects : ") + data.text);
          invalidConnections = data.invalid_connections;
          if(invalidConnections && invalidConnections.length){
            var title = __("Invalid Connections will be deleted") + ":<br/><br/>",
              msg = Ext.Array.map(invalidConnections, function(connection){
                return connection.error;
              });
            Ext.Msg.show({
              title: __("Invalid connections"),
              message: title + msg.join("<br/>") + "<br/><br/><br/>" + __("This message will automatically close in 5 seconds."),
              buttons: Ext.Msg.OK,
              icon: Ext.Msg.INFO,
            });

            Ext.Array.each(invalidConnections, function(invalid){
              Ext.Array.each(connections, function(connection){
                if(connection.fromPort === invalid.name && connection.toPort === invalid.remote_name){
                  me.removeConnection(me.getConnectionById(connection));
                  return false;
                }
              });
            });
            if(rightSurface){
              rightSurface.renderFrame();
            }
            Ext.defer(function(){
              Ext.Msg.hide();
            }, 5000);
          }
        }
        Ext.Array.each(connections, function(connection){
          if(!connection.destroyed){
            connection.setAttributes({isNew: false});
          }
        });
        mainSurface.renderFrame();
        leftSurface.renderFrame();
        rightSurface.renderFrame();
      },
      failure: function(response){
        NOC.error(__("Failed to connect objects : ") + response.responseText);
      },
    });
  },
  onSpriteClick: function(element){
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
      isWire = sprite.attr.cursorOn === "wire",
      clearViewModel = function(){
        viewModel.set("selectedPinId", null);
        viewModel.set("selectedPin", null);
        viewModel.set("isSelectedPinInternal", null);
        viewModel.set("side", null);
        surface.get("pointer").remove();
      };

    if(!sprite.enabled && isWire){
      return;
    }
    if(!sprite.internalEnabled && isInternal){
      return;
    }

    if(prevSprite && (prevSprite.id === sprite.id)){
      return;
    }

    if(sprite.type === "pin" && isInternal && sprite.attr.isSelected && prevSprite && prevSprite.attr.isSelected){
      me.createInternalConnectionMsg(prevSprite, sprite, side);
      clearViewModel();
      return;
    }

    if(sprite.type === "pin" && !isInternal && sprite.attr.isSelected && prevSprite && prevSprite.attr.isSelected){
      me.createWire(prevSprite, sprite, side);
      clearViewModel();
      return;
    }

    switch(sprite.type){
      case "pin": {
        me.selectPin(element, prevSelectPinId, isInternal, prevIsInternal);
        sprite.setAttributes({
          isInternalFixed: isInternal,
        });
        // add pointer
        if(isInternal){
          pointerX = sprite.internal.attr.translationX;
          pointerY = sprite.internal.attr.translationY;
          offset = (side === "left" ? -4 * me.boxWidth : 4 * me.boxWidth);
        }
        if(isWire){
          pointerX = sprite.box.attr.translationX + sprite.box.attr.width / 2;
          pointerY = sprite.box.attr.translationY + sprite.box.attr.height / 2;
          offset = (side === "left" ? 1 : -1) * me.getWiresOffset(side, undefined, true)[0];
          offset += 2 * me.boxWidth * (side === "left" ? 1 : -1); // add offset for external arrow connection
        }
        if(!pointer){
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
            zIndex: 100,
          });
        } else{
          pointer.setAttributes({
            fromX: pointerX,
            fromY: pointerY,
            toX: pointerX + offset,
            toY: pointerY,
            actualScale: me.scale,
          });
        }
        if(sprite.attr.isSelected){
          viewModel.set("selectedPinId", sprite.id);
          viewModel.set("selectedPin", sprite.pinName);
          viewModel.set("isSelectedPinInternal", isInternal);
          viewModel.set("side", side);
        } else{
          // self selected
          clearViewModel();
        }
        me.reloadStatuses(false, side + "_filter=" + sprite.pinName + "&internal=" + isInternal);
        break;
      }
      case "connection": {
        if(sprite.connectionType === "internal" && sprite.isDeleted){
          me.updateDeleteInternalConnectionMsg();
        }
        if(Ext.Array.contains(["wire", "loopback"], sprite.connectionType)){
          me.removeWireMsg(sprite);
        }
        break;
      }
      case "external": {
        me.goToObject(sprite.remoteId, sprite.remoteName, side);
        break;
      }
    }
    surface.renderFrame();
  },
  onSpriteMouseOut: function(element){
    var me = this,
      viewModel = me.getViewModel(),
      selectedPinId = viewModel.get("selectedPinId"),
      mainSurface = me.drawPanel.getSurface(),
      sprite = element.sprite;

    if(!me.drawPanel.isModalOpen){
      switch(sprite.type){
        case "pin": {
          if(selectedPinId !== sprite.id){
            var pointer = mainSurface.get("pointer");
            sprite.setAttributes({
              isSelected: false,
              pinOver: false,
            });
            if(pointer){
              pointer.setAttributes({
                lineType: "line",
                side: sprite.side,
              });
            }
          }
          if(sprite.enabled){
            sprite.setAttributes({
              actualScale: 1,
            });
          }
          // wire connections
          Ext.each(me.drawPanel.getSurface().getItems(), function(s){
            if(s.fromPortId === sprite.id || s.toPortId === sprite.id){
              s.setAttributes({isSelected: false});
            }
          });
          // internal connections
          Ext.each(me.drawPanel.getSurface(sprite.side + "_internal_conn").getItems(), function(s){
            if(s.fromPortId === sprite.id || s.toPortId === sprite.id){
              s.setAttributes({isSelected: false});
            }
          });
          break;
        }
        case "connection": {
          mainSurface.get(sprite.fromPortId).setAttributes({
            actualScale: 1,
            pinOver: false,
          });
          mainSurface.get(sprite.toPortId).setAttributes({
            actualScale: 1,
            pinOver: false,
          });
          if(sprite.connectionType === "internal"){
            me.drawPanel.selectedSprite = undefined;
            sprite.setAttributes({isSelected: false});
            if(sprite.toDiscriminatorTooltip && !sprite.toDiscriminatorTooltip.isHidden()){
              sprite.toDiscriminatorTooltip.hide();
            }
            if(sprite.fromDiscriminatorTooltip && !sprite.fromDiscriminatorTooltip.isHidden()){
              sprite.fromDiscriminatorTooltip.hide();
            }
          }
          if(Ext.Array.contains(["wire", "loopback"], sprite.connectionType)){
            sprite.setAttributes({isSelected: false});
          }
          break;
        }
        case "external": {
          if(!sprite.destroyed){
            sprite.setAttributes({isSelected: false});
            sprite.remoteNameTooltip.hide();
          }
          break;
        }
      }
    }
  },
  onSpriteMouseOver: function(element, event){
    var pointer, me = this,
      mainSurface = me.drawPanel.getSurface(),
      sprite = element.sprite;

    if(!me.drawPanel.isModalOpen){
      switch(sprite.type){
        case "pin": {
          if(sprite.enabled){
            sprite.setAttributes({
              actualScale: 1.2,
              pinOver: true,
            });
          }
          // illumination of ALL wire connections
          Ext.each(mainSurface.getItems(), function(s){
            if(s.fromPortId === sprite.id || s.toPortId === sprite.id){
              s.setAttributes({isSelected: true});
            }
          });
          // illumination of ALL internal connections
          Ext.each(me.drawPanel.getSurface(sprite.side + "_internal_conn").getItems(), function(s){
            if(s.fromPortId === sprite.id || s.toPortId === sprite.id){
              s.setAttributes({isSelected: true});
            }
          });
          if(me.isPinAvailableForSelect(sprite)){
            var viewModel = me.getViewModel(),
              firstSide = viewModel.get("side");
              
            pointer = mainSurface.get("pointer");
            sprite.setAttributes({
              isSelected: true,
              isInternalFixed: sprite.attr.cursorOn === "internal",
              pinOver: true,
            });
            pointer.setAttributes({
              lineType: firstSide === sprite.side && sprite.attr.cursorOn !== "internal" ? "loopback" : sprite.attr.cursorOn,
              side: sprite.side,
              xOffsets: Ext.Array.map(me.getWiresOffset(firstSide, sprite.side, true), function(w){return w + this.boxWidth * 2}, me),
            });
          }
          break;
        }
        case "connection": {
          pointer = mainSurface.get("pointer");
          mainSurface.get(sprite.fromPortId).setAttributes({
            actualScale: 1.2,
            pinOver: true,
          });
          mainSurface.get(sprite.toPortId).setAttributes({
            actualScale: 1.2,
            pinOver: true,
          });
          if(pointer){
            pointer.setAttributes({
              lineType: "line",
            });
          }
          if(sprite.connectionType === "internal"){
            me.drawPanel.selectedSprite = sprite;
            sprite.setAttributes({isSelected: true});
            if(sprite.toDiscriminatorTooltip && sprite.toDiscriminatorTooltip.isHidden()){
              sprite.toDiscriminatorTooltip.showAt([event.pageX + (sprite.side === "left" ? me.toolTipOffset : -1 * me.toolTipOffset), event.pageY + me.toolTipOffset]);
            }
            if(sprite.fromDiscriminatorTooltip && sprite.fromDiscriminatorTooltip.isHidden()){
              sprite.fromDiscriminatorTooltip.showAt([event.pageX + (sprite.side === "left" ? me.toolTipOffset : -1 * me.toolTipOffset), event.pageY - me.toolTipOffset]);
            }
          }
          if(Ext.Array.contains(["wire", "loopback"], sprite.connectionType)){
            sprite.setAttributes({isSelected: true});
            me.drawPanel.getSurface().renderFrame();
          }
          break;
        }
        case "external": {
          sprite.setAttributes({isSelected: true});
          sprite.remoteNameTooltip.showAt([event.pageX + (sprite.side === "left" ? me.toolTipOffset : -1 * me.toolTipOffset), event.pageY + me.toolTipOffset]);
          break;
        }
      }
    }
  },
  pinStatus: function(pin){
    var me = this,
      pinColor = me.AVAILABLE_COLOR,
      internalColor = me.AVAILABLE_COLOR,
      name = pin.name,
      remoteId = "none",
      remoteName = "none",
      remoteSlot = "none",
      internalEnabled = true,
      masked = false,
      enabled = true;

    if(!pin.free){
      pinColor = me.OCCUPIED_COLOR;
      enabled = false;
      if(pin.remote_device){
        remoteName = pin.remote_device.name || "";
        remoteSlot = pin.remote_device.slot || "";
        remoteId = pin.remote_device.id;
      }
    }
    if(!pin.valid){
      pinColor = me.INVALID_COLOR;
      enabled = false;
      masked = true;
    }
    if(pin.internal){
      if(!pin.internal.valid){
        internalColor = me.INVALID_COLOR;
        internalEnabled = false;
      }
      if(!pin.internal.free){
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
      remoteSlot: remoteSlot,
      internalEnabled: internalEnabled,
      enabled: enabled,
      masked: masked,
    };
  },
  reDrawLabelsStyle: function(surface){
    var me = this;
    Ext.Array.each(
      Ext.Array.filter(surface.getItems(), function(sprite){ return sprite.type === "pin" }),
      function(pin){
        pin.setAttributes({
          labelColor: pin.masked ? me.MASKED_LABEL_COLOR : me.UNMASKED_LABEL_COLOR,
        });
      });
  },
  reloadStatuses: function(fromCombo, filter){
    var params, me = this,
      vm = me.getViewModel(),
      leftObject = vm.get("leftObject"),
      rightObject = vm.get("rightObject"),
      cable = me.cableCombo.getValue(),
      leftObjectId = leftObject ? leftObject.id : undefined,
      rightObjectId = rightObject ? rightObject.id : undefined;

    if(!leftObjectId){
      return;
    }
    if(me.cableCombo.getValue()){
      me.cableCombo.getTrigger("clear").show();
    } else{
      me.cableCombo.getTrigger("clear").hide();
    }
    params = "o1=" + leftObjectId + (rightObjectId ? "&o2=" + rightObjectId : "");
    params += cable ? "&cable_filter=" + cable : "";
    params += filter ? "&" + filter : "";
    me.mask(__("Loading..."));
    Ext.Ajax.request({
      url: "/inv/inv/crossing_proposals/?" + params,
      method: "GET",
      success: function(response){
        var data = Ext.decode(response.responseText);

        Ext.Array.each(["left", "right"], function(side){
          if(data[side].connections && data[side].connections.length){
            me.updatePinsStatus(data[side].connections, side, fromCombo);
          }
        });
        me.unmask();
        me.checkAvailabilityConnection();
        NOC.msg.complete(__("The data was successfully updated"));
      },
      failure: function(){
        me.unmask();
        NOC.msg.failed(__("Error updating statuses"));
      },
    });
  },
  removeConnection: function(connection){
    if(connection.connectionType === "internal"){
      this.removeInternalConnection(connection);
    } else{
      this.removeWire(connection);
    }
  },
  removeInternalConnection: function(connectionSpire){
    var connections,
      me = this,
      drawPanel = me.drawPanel,
      side = connectionSpire.fromSide,
      mainSurface = drawPanel.getSurface(),
      body = mainSurface.get(side + "Body"),
      surface = drawPanel.getSurface(side + "_internal_conn"),
      pinEnabled = {internalColor: me.AVAILABLE_COLOR, internalEnabled: true};

    mainSurface.get(connectionSpire.fromPortId).setAttributes(pinEnabled);
    mainSurface.get(connectionSpire.toPortId).setAttributes(pinEnabled);
    connections = me.getInternalConnections(surface);
    if(!me.hasDiscriminator(connections.internal_connections)){
      me.switchInternalLabel(body, false);
    }
    me.reloadStatuses(false);
    me.drawInternalConnections(connections, surface, side);
    mainSurface.renderFrame();
  },
  removeWireMsg: function(wireSprite){
    var me = this,
      drawPanel = me.drawPanel;

    drawPanel.isModalOpen = true;
    Ext.Msg.confirm(__("Confirm"), __("Are you sure you want to delete this wire") + " " + wireSprite.fromPort + "=>" + wireSprite.toPort, function(btn){
      if(btn === "yes"){
        var vm = me.getViewModel(),
          leftObject = vm.get("leftObject"),
          rightObject = vm.get("rightObject"),
          params = {
            object: leftObject.id,
            name: wireSprite.fromPort,
            remote_object: rightObject ? rightObject.id : undefined,
            remote_name: wireSprite.toPort,
            is_internal: wireSprite.connectionType === "internal",
          };

        if(wireSprite.isNew){
          me.removeWire(wireSprite);
        } else{
          if(!params.remote_object){
            delete params.remote_object;
          }
          me.disconnectConnection(params, function(){
            me.removeWire(wireSprite);
            me.reloadStatuses(true);
            NOC.msg.complete(__("Wire was successfully disconnected"));
          });
        }
      }
      drawPanel.isModalOpen = false;
    });
  },
  removeWire: function(wireSprite){
    var connections,
      me = this,
      drawPanel = me.drawPanel,
      mainSurface = drawPanel.getSurface(),
      fromSprite = mainSurface.get(wireSprite.fromPortId),
      toSprite = mainSurface.get(wireSprite.toPortId);
    
    fromSprite.setAttributes({
      pinColor: me.AVAILABLE_COLOR,
      enabled: true,
      pinName: wireSprite.fromPort,
    });
    toSprite.setAttributes({
      pinColor: me.AVAILABLE_COLOR,
      enabled: true,
      pinName: wireSprite.toPort,
    });
    wireSprite.remove();
    connections = me.getWires(mainSurface);
    me.drawWires(connections, mainSurface);
    mainSurface.renderFrame();
  },
  scaleCalculate: function(){
    var surfaceHeight, containerHeight,
      me = this;
    
    me.initValues();
    surfaceHeight = me.maxPins * (me.boxHeight + me.gap) + me.gap + me.schemaPadding * 4,
    containerHeight = me.drawPanel.getHeight() - me.legendHeight;
    if(surfaceHeight > containerHeight){
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
  selectPin: function(element, prevSelectPinId, isInternal, preIsInternal){
    var sprite = element.sprite,
      isSelected = sprite.attr.isSelected;
    if((sprite.id !== prevSelectPinId) ||
            (sprite.id === prevSelectPinId && isInternal === preIsInternal)){
      isSelected = !isSelected;
    }
    sprite.setAttributes({
      isSelected: isSelected,
      isInternalFixed: isInternal,
    });
    if(sprite.id !== prevSelectPinId){
      // deselect previous selection
      var preSelectedSprite = this.drawPanel.getSurface().get(prevSelectPinId);
      if(preSelectedSprite){
        preSelectedSprite.setAttributes({isSelected: false});
      }
    }
  },
  switchInternalLabel: function(body, state){
    var me = this,
      mainSurface = me.drawPanel.getSurface(),
      internalPins = Ext.Array.filter(mainSurface.getItems(), function(sprite){return sprite.type === "pin" && sprite.side === body.side});

    Ext.Array.map(internalPins, function(pin){
      pin.setAttributes({
        hasInternalLabel: state,
      })
    });
  },
  updateDeleteInternalConnectionMsg: function(){
    var me = this,
      drawPanel = me.drawPanel,
      mainSurface = drawPanel.getSurface(),
      sprite = drawPanel.selectedSprite,
      fromSprite = mainSurface.get(sprite.fromPortId),
      toSprite = mainSurface.get(sprite.toPortId),
      side = sprite.fromSide,
      values = {
        gainDb: sprite.gainDb,
        fromDiscriminator: sprite.fromDiscriminator,
        toDiscriminator: sprite.toDiscriminator,
      };

    drawPanel.isModalOpen = true;

    Ext.create("Ext.window.Window", {
      autoShow: true,
      width: 400,
      reference: "updateRemoveConnFrm",
      modal: true,
      layout: "form",
      title: __("Update or modify internal connection from") + " " + sprite.fromPort + " " + __("to") + " " + sprite.toPort,
      referenceHolder: true,
      defaultFocus: "numberfield",
      defaultButton: "updateBtn",
      items: me.itemsForConnectionParamsForm(fromSprite.allowDiscriminators, toSprite.allowDiscriminators, "updateBtn", values),
      buttons: [
        {
          text: __("Update"),
          reference: "updateBtn",
          handler: function(button){
            sprite.remove();
            me.addConnectionSprite(button, fromSprite, toSprite, side);
            me.getViewModel().set("isDirty", true);
            mainSurface.renderFrame();
            button.up("window").close();
          },
        },
        {
          text: __("Delete"),
          handler: function(button){
            var vm = me.getViewModel(),
              fromObject = vm.get(sprite.fromSide + "Object"),
              params = {
                object: fromObject.id,
                name: sprite.fromPort,
                remote_name: sprite.toPort,
                is_internal: true,
              };

            if(sprite.isNew){
              me.removeInternalConnection(sprite);
            } else{
              me.disconnectConnection(params, function(){
                me.removeInternalConnection(sprite);
                NOC.msg.complete(__("Internal cross was successfully disconnected"));
              });
            }
            button.up("window").close();
          },
        },
        {
          text: __("Cancel"),
          handler: function(){
            this.up("window").close();
          },
        },
      ],
      listeners: {
        close: function(){
          me.reloadStatuses(true);
          drawPanel.isModalOpen = false;
        },
      },
    });
  },
  updatePinsStatus: function(pinObjList, side, clearPointer){
    var me = this,
      mainSurface = me.drawPanel.getSurface(),
      leftSurface = me.drawPanel.getSurface("left_internal_conn"),
      rightSurface = me.drawPanel.getSurface("right_internal_conn"),
      newWires = Ext.Array.filter(mainSurface.getItems(), function(sprite){return sprite.type === "connection" && sprite.isNew}),
      leftInternal = Ext.Array.filter(leftSurface.getItems(), function(sprite){return sprite.type === "connection" && sprite.isNew}),
      rightInternal = Ext.Array.filter(rightSurface.getItems(), function(sprite){return sprite.type === "connection" && sprite.isNew}),
      pinsWithNewConnections = me.flattenArray(Ext.Array.map(leftInternal.concat(newWires).concat(rightInternal), function(connection){
        var type = connection.connectionType === "internal" ? "internal" : "external";
        return [{
          pin: connection.fromPortId,
          type: type,
        },
                {
                  pin: connection.toPortId,
                  type: type,
                }];
      }));

    if(clearPointer){
      me.cancelDrawConnection();
    }
    Ext.Array.each(pinObjList, function(pinObj){
      var pinStripe = mainSurface.get(pinObj.id),
        allowDiscriminators = pinObj.internal ? pinObj.internal.allow_discriminators : undefined,
        pinHasNewInternalConnection = Ext.Array.filter(pinsWithNewConnections, function(item){return item.pin === pinObj.id && item.type === "internal"}).length > 0,
        pinHasNewExternalConnection = Ext.Array.filter(pinsWithNewConnections, function(item){return item.pin === pinObj.id && item.type === "external"}).length > 0,
        status = me.pinStatus(pinObj, side),
        pinColor = pinHasNewExternalConnection ? pinStripe.pinColor : status.pinColor,
        enabled = pinHasNewExternalConnection ? pinStripe.enabled : status.enabled,
        internalColor = pinHasNewInternalConnection ? pinStripe.internalColor : status.internalColor,
        internalEnabled = pinHasNewInternalConnection ? pinStripe.internalEnabled : status.internalEnabled;

      pinStripe.setAttributes({
        pinColor: pinColor,
        enabled: enabled,
        allowDiscriminators: allowDiscriminators,
        internalColor: internalColor,
        internalEnabled: internalEnabled,
      });
    });
    me.reDrawLabelsStyle(mainSurface);
  },
  wireSort: function(wire){
    return Ext.Array.sort(wire, function(a, b){
      return a.side === 'left' ? -1 : (b.side === 'left' ? 1 : 0);
    });
  },
  xOffset: function(side, pins){
    var internalPinQty = this.internalPinQty(pins);

    if(side === "left"){
      return internalPinQty * this.gap + 30 - this.discriminatorWidth[side];
    }
    var rightWidth = internalPinQty * this.gap + 30 + this.discriminatorWidth[side],
      remoteLength = this.getWiresOffset("left", "right", true),
      rightOffset = this.bodiesWidth.left + remoteLength[0] + this.arrowLength + this.betweenSpace;

    if(rightOffset + rightWidth > this.drawPanelSize.w){
      this.drawPanelSize.w = rightOffset + rightWidth;
    }
    return rightOffset;
  },
});
