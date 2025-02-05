//---------------------------------------------------------------------
// Workflow editor, JointJS version
//---------------------------------------------------------------------
// Copyright (C) 2007-2018 The NOC Project
// See LICENSE for details
//---------------------------------------------------------------------
console.debug("Defining NOC.wf.workflow.WFEditor");

Ext.define("NOC.wf.workflow.WFEditor", {
    extend: "NOC.core.ApplicationPanel",
    requires: [
        "Ext.ux.form.StringsField",
        "NOC.core.label.LabelField",
        "NOC.core.tagfield.Tagfield",
        "NOC.main.ref.modelid.LookupField"
    ],
    config: {
        scriptsLoaded: false
    },
    mixins: {
        observable: 'Ext.util.Observable'
    },
    constructor: function(config) {
        this.mixins.observable.constructor.call(this, config);
        this.callParent();
    },
    updateScriptsLoaded: function(newValue, oldValue) {
        var me = this;
        me.fireEvent("scriptsLoaded", newValue);
    },
    initComponent: function() {
        var me = this;

        me.blankMenu = Ext.create("Ext.menu.Menu", {
            items: [
                {
                    text: __("Add State"),
                    glyph: NOC.glyph.plus,
                    scope: me,
                    handler: me.onAddState
                }
            ]
        });
        me.menuPosition = {x: 0, y: 0};
        me.stateWidth = 100;
        me.stateHeight = 40;
        me.isIspectorDirty = false;
        me.inspector = {
            xtype: "form",
            itemId: "inspector",
            flex: 1,
            scrollable: "vertical",
            bodyPadding: "10",
            defaults: {
                labelAlign: "top",
                width: "100%"
            },
            listeners: {
                scope: me,
                dirtychange: me.inspectorDirty
            },
            buttons: [
                {
                    text: __("Submit"),
                    disabled: true,
                    formBind: true,
                    scope: me,
                    handler: me.onSubmitInspector
                }
            ]
        };
        Ext.apply(me, {
            tbar: [
                me.getCloseButton(),
                "-",
                {
                    xtype: "button",
                    tooltip: __("Delete Workflow"),
                    text: __("Delete"),
                    glyph: NOC.glyph.remove,
                    scope: me,
                    handler: me.onDeleteClick
                },
                "-",
                {
                    xtype: "button",
                    tooltip: __("Save Workflow"),
                    text: __("Save"),
                    glyph: NOC.glyph.save,
                    scope: me,
                    handler: me.onSaveClick
                }
            ],
            layout: {
                type: "hbox",
                align: "stretch"
            },
            items: [
                {
                    xtype: "container",
                    itemId: "container",
                    flex: 4
                }
            ]
        });
        me.callParent();
    },
    //
    afterRender: function() {
        var me = this;
        new_load_scripts([
            "/ui/pkg/lodash/lodash.min.js",
            "/ui/pkg/backbone/backbone.min.js",
            "/ui/pkg/dagre/dagre.min.js",
            "/ui/pkg/graphlib/graphlib.min.js",
            "/ui/pkg/joint/joint.min.js",
            "/ui/pkg/joint.layout.directedgraph/joint.layout.directedgraph.min.js",
            "/ui/web/wf/workflow/js/joint.element.Tools.js"
        ], me, me.initMap);
        me.callParent();
    },
    // Initialize JointJS Map
    initMap: function() {
        var me = this,
            dom = me.getComponent("container").el.dom;
        me.currentHighlight = null;
        me.workflow = {};
        me.graph = new joint.dia.Graph;
        me.paper = new joint.dia.Paper({
            el: dom,
            model: me.graph,
            gridSize: 10,
            gridWidth: 10,
            gridHeight: 10,
            drawGrid: true,
            linkPinning: false,
            preventContextMenu: false,
            defaultRouter: {
                name: "metro"
            },
            defaultConnector: {
                name: "rounded"
            },
            guard: function(evt) {
                return (evt.type === "mousedown" && evt.buttons === 2);
            }
        });
        me.paper.on("blank:pointerclick", Ext.bind(me.onSelect, me));
        me.paper.on("cell:pointerclick", Ext.bind(me.onSelect, me));
        me.paper.on("blank:contextmenu", Ext.bind(me.openBlankMenu, me));
        //
        me.graph.on("change:position", function(element) {
            var elementView = element.findView(me.paper);
            elementView.removeTools();
        });
        me.graph.on("remove", Ext.bind(me.onRemoveCell, me));
        me.setScriptsLoaded(true);
    },
    //
    preview: function(record, backItem) {
        var me = this;
        if(record) {
            me.configId = record.get("id");
            Ext.Ajax.request({
                url: "/wf/workflow/" + me.configId + "/config/",
                method: "GET",
                scope: me,
                success: function(response) {
                    me.draw(Ext.decode(response.responseText));
                },
                failure: function() {
                    NOC.error(__("Failed to get data"));
                }
            });
        } else {
            me.configId = "000000000000000000000000";
            me.draw({
                id: me.configId,
                name: "New Workflow",
                description: "New Workflow diagram",
                is_active: true,
                allowed_models: [],
                states: [],
                transitions: []
            });
        }
        if(me.graph && Ext.isFunction(me.graph.clear)) {
            me.graph.clear();
        }
        me.callParent(arguments);
    },
    //
    draw: function(data) {
        var me = this, x = 200, y = 40, makeLayout = true;
        var stateByName = function(name) {
            return me.graph.getElements().filter(function(element) {
                return element.attr("label/text") === name;
            })
        };

        me.workflow = me.loadData(data, "workflow");
        data.states.forEach(function(state) {
            var rect = new joint.shapes.standard.Rectangle();
            if(state.x && state.y) {
                rect.set("position", {x: state.x, y: state.y});
                makeLayout = false;
            } else {
                rect.set("position", {x: x, y: y});
            }
            rect.resize(me.stateWidth, me.stateHeight);
            rect.attr("label/text", state.name);
            rect.prop({data: me.loadData(state, "state")});
            rect.addTo(me.graph);
            y += 100;
        });
        data.transitions.forEach(function(transition) {
            var fromStates = stateByName(transition.from_state);
            var toStates = stateByName(transition.to_state);

            fromStates.forEach(function(source) {
                toStates.forEach(function(target) {
                    var link = new joint.shapes.standard.Link();
                    link.source(source);
                    link.target(target);
                    link.appendLabel({
                        attrs: {
                            text: {
                                text: transition.label
                            }
                        }
                    });
                    link.prop({data: me.loadData(transition, "transition")});
                    if(transition.hasOwnProperty("vertices")) {
                        transition.vertices.forEach(function(vertex, index) {
                            link.insertVertex(index, vertex);
                        });
                    }
                    link.addTo(me.graph);
                });
            });
        });
        if(makeLayout) {
            joint.layout.DirectedGraph.layout(me.graph, {
                marginX: 50,
                marginY: 50,
                nodeSep: 100,
                edgeSep: 80,
                rankDir: "TB"
            });
        }
        me.showWorkflowInspector(me.workflow);
    },
    //
    unhighlight: function() {
        var me = this;
        if(me.currentHighlight) {
            me.currentHighlight.unhighlight();
            me.currentHighlight.removeTools();
            me.currentHighlight = null;
        }
    },
    //
    addElementTools: function(view) {
        var me = this,
            removeButton = new joint.elementTools.Remove({offset: -10, distance: -10}),
            linkButton = new joint.elementTools.AddLink({offset: me.stateHeight / 2, distance: me.stateWidth}),
            toolsView = new joint.dia.ToolsView({
                tools: [
                    removeButton,
                    linkButton
                ]
            });
        view.addTools(toolsView);
    },
    //
    addLinkTools: function(view) {
        var removeButton = new joint.linkTools.Remove(),
            verticesTool = new joint.linkTools.Vertices(),
            segmentsTool = new joint.linkTools.Segments();
        var toolsView = new joint.dia.ToolsView({
            tools: [
                verticesTool,
                segmentsTool,
                removeButton
            ]
        });
        view.addTools(toolsView);
    },
    //
    onSelect: function(view) {
        var me = this;
        me.dirtyCheck(me.select, view);
    },
    //
    select: function(view) {
        var me = this,
            data = me.workflow;
        me.unhighlight();
        if(view.model) {
            data = view.model.get("data");
            me.currentHighlight = view;
            view.highlight();
        }
        switch(data.type) {
            case "state": {
                me.addElementTools(view);
                me.showStateInspector(data);
                break;
            }
            case "transition": {
                me.addLinkTools(view);
                me.showTransitionInspector(data);
                break;
            }
            case "workflow": {
                me.showWorkflowInspector(data);
                break;
            }
        }
    },
    //
    clearInspector: function() {
        var me = this,
            inspector = me.getComponent("inspector");
        me.isIspectorDirty = false;
        if(inspector && Ext.isFunction(inspector.destroy)) {
            inspector.destroy();
        }
    },
    //
    showInspector: function(data, fields, title) {
        var me = this, inspector,
            record = Ext.create(me.getModelName(data.type));

        record.set(data);
        me.clearInspector();

        me.inspector.items = fields.map(function(field) {
            if(data.hasOwnProperty(field.name)) {
                field.value = data[field.name];
            }
            if(field.xtype === 'fieldset') {
                field.items = field.items.map(function(item) {
                    if(data.hasOwnProperty(item.name)) {
                        item.value = data[item.name];
                    }
                    return item;
                });
            }
            return field;
        });
        me.inspector.record = record;
        me.inspector.title = title;
        inspector = Ext.create(me.inspector);
        me.add(inspector);
    },
    //
    showWorkflowInspector: function(data) {
        var me = this,
            fields = [
                {
                    name: "name",
                    xtype: "textfield",
                    fieldLabel: __("Name"),
                    allowBlank: false
                },
                {
                    name: "is_active",
                    xtype: "checkbox",
                    boxLabel: __("Active")
                },
                {
                    name: "description",
                    xtype: "textarea",
                    fieldLabel: __("Description"),
                    allowBlank: true
                },
                {
                    name: "allowed_models",
                    xtype: "core.tagfield",
                    url: "/main/ref/modelid/lookup/",
                    fieldLabel: __("Allowed models"),
                    tooltip: __("Models allowed set workflow")
                },
                {
                    xtype: "fieldset",
                    layout: "vbox",
                    title: __("Integration"),
                    defaults: {
                        padding: 4,
                        labelAlign: "top",
                        disabled: true
                    },
                    items: [
                        {
                            name: "remote_system",
                            xtype: "main.remotesystem.LookupField",
                            fieldLabel: __("Remote System"),
                            allowBlank: true
                        },
                        {
                            name: "remote_id",
                            xtype: "textfield",
                            fieldLabel: __("Remote ID"),
                            allowBlank: true
                        },
                        {
                            name: "bi_id",
                            xtype: "displayfield",
                            fieldLabel: __("BI ID"),
                            allowBlank: true
                        }
                    ]
                }
            ];
        me.showInspector(data, fields, __("Workflow Inspector"));
    },
    //
    showStateInspector: function(data) {
        var me = this,
            fields = [
                {
                    name: "name",
                    xtype: "textfield",
                    fieldLabel: __("Name"),
                    allowBlank: false
                },
                {
                    name: "description",
                    xtype: "textarea",
                    fieldLabel: __("Description"),
                    allowBlank: true
                },
                {
                    name: "is_default",
                    xtype: "checkbox",
                    boxLabel: __("Default")
                },
                {
                    name: "is_productive",
                    xtype: "checkbox",
                    boxLabel: __("Productive")
                },
                {
                    name: "is_wiping",
                    xtype: "checkbox",
                    boxLabel: __("Wiping")
                },
                {
                    name: "update_last_seen",
                    xtype: "checkbox",
                    boxLabel: __("Update Last Seen")
                },
                {
                    name: "ttl",
                    xtype: "numberfield",
                    fieldLabel: __("TTL"),
                    allowBlank: true,
                    minValue: 0,
                    emptyText: __("Not Limited")
                },
                {
                    name: "update_expired",
                    xtype: "checkbox",
                    boxLabel: __("Update Expiration")
                },
                {
                    name: "labels",
                    xtype: "labelfield",
                    fieldLabel: __("Labels")
                },
                {
                    name: "job_handler",
                    xtype: "textfield",
                    fieldLabel: __("Job Handler")
                },
                {
                    xtype: "fieldset",
                    layout: "vbox",
                    title: __("Integration"),
                    defaults: {
                        padding: 4,
                        labelAlign: "top",
                        disabled: true
                    },
                    items: [
                        {
                            name: "remote_system",
                            xtype: "main.remotesystem.LookupField",
                            fieldLabel: __("Remote System"),
                            allowBlank: true
                        },
                        {
                            name: "remote_id",
                            xtype: "textfield",
                            fieldLabel: __("Remote ID"),
                            allowBlank: true
                        },
                        {
                            name: "bi_id",
                            xtype: "displayfield",
                            fieldLabel: __("BI ID"),
                            allowBlank: true
                        }
                    ]
                },
                {
                    name: "on_enter_handlers",
                    xtype: "stringsfield",
                    fieldLabel: __("On Enter Handlers"),
                    allowBlank: true
                },
                {
                    name: "on_leave_handlers",
                    xtype: "stringsfield",
                    fieldLabel: __("On Leave Handlers"),
                    allowBlank: true
                }
            ];
        me.stateNamePrev = data.name;
        me.showInspector(data, fields, __("State Inspector"));
    },
    //
    showTransitionInspector: function(data) {
        var me = this,
            fields = [
                {
                    name: "label",
                    xtype: "textfield",
                    fieldLabel: __("Label"),
                    allowBlank: false
                },
                {
                    name: "event",
                    xtype: "textfield",
                    fieldLabel: __("Event"),
                    allowBlank: true
                },
                {
                    name: "is_active",
                    xtype: "checkbox",
                    boxLabel: __("Active")
                },
                {
                    name: "enable_manual",
                    xtype: "checkbox",
                    boxLabel: __("Enable Manual")
                },
                {
                    name: "description",
                    xtype: "textarea",
                    fieldLabel: __("Description"),
                    allowBlank: true
                },
                {
                    xtype: "fieldset",
                    layout: "vbox",
                    title: __("Integration"),
                    defaults: {
                        padding: 4,
                        labelAlign: "top",
                        disabled: true
                    },
                    items: [
                        {
                            name: "remote_system",
                            xtype: "main.remotesystem.LookupField",
                            fieldLabel: __("Remote System"),
                            allowBlank: true
                        },
                        {
                            name: "remote_id",
                            xtype: "textfield",
                            fieldLabel: __("Remote ID"),
                            allowBlank: true
                        },
                        {
                            name: "bi_id",
                            xtype: "displayfield",
                            fieldLabel: __("BI ID"),
                            allowBlank: true
                        }
                    ]
                },
                {
                    name: "handlers",
                    xtype: "stringsfield",
                    fieldLabel: __("Handlers"),
                    allowBlank: true
                }
            ];
        me.showInspector(data, fields, __("Transition Inspector"));
    },
    //
    onSubmitInspector: function() {
        var me = this,
            data,
            form = me.getComponent("inspector");
        if(form.isValid()) {
            form.updateRecord(form.record);
            data = form.record.getData();
            if(data.type === "state" && data.name !== me.stateNamePrev) {
                me.changeStatenameInTransition(me.stateNamePrev, data.name);
            }
            me.isIspectorDirty = false;
            if(me.currentHighlight && me.currentHighlight.model) {
                me.currentHighlight.model.removeProp("data");
                me.currentHighlight.model.prop({data: data});
                switch(me.currentHighlight.model.get("data").type) {
                    case "state": {
                        me.currentHighlight.model.attr("label/text", data.name);
                        break;
                    }
                    case "transition": {
                        me.currentHighlight.model.label(0, {
                            attrs: {
                                text: {
                                    text: data.label
                                }
                            }
                        });
                        break;
                    }
                }
            } else { // workflow
                me.workflow = me.loadData(data, "workflow");
            }
            return true;
        }
        return false;
    },
    //
    onDeleteClick: function() {
        var me = this;
        Ext.Msg.show({
            title: __("Delete Workflow?"),
            msg: __("Do you wish to delete Workflow? This operation cannot be undone!"),
            buttons: Ext.Msg.YESNO,
            icon: Ext.window.MessageBox.QUESTION,
            modal: true,
            fn: function(button) {
                if(button === "yes") {
                    me.app.deleteRecord();
                    me.onClose();
                }
            }
        });
    },
    //
    onSaveClick: function() {
        var me = this;
        me.dirtyCheck(me.save);
    },
    //
    save: function() {
        var me = this,
            data = me.graph.toJSON(),
            findStateNameById = function(id) {
                for(var i = 0; i < states.length; i++) {
                    if(states[i].id === id) {
                        return states[i].data.name;
                    }
                }
                return "state not found";
            },
            states = data.cells.filter(function(cell) {
                return cell.data.type === "state"
            }),
            transitions = data.cells
                .filter(function(cell) {
                    return cell.data.type === "transition"
                })
                .map(function(element) {
                    element.from_state = findStateNameById(element.source.id);
                    element.to_state = findStateNameById(element.target.id);
                    element.data["vertices"] = [];
                    if(element.hasOwnProperty("vertices")) {
                        element.data["vertices"] = element.vertices;
                    }
                    if(element.data.hasOwnProperty("remote_system") && element.data["remote_system"].length === 0) {
                        delete element.data["remote_system"];
                    }
                    if(element.data.hasOwnProperty("remote_id") && element.data["remote_id"].length === 0) {
                        delete element.data["remote_id"];
                    }
                    delete element.data["bi_id"];
                    delete element.data["uuid"];
                    delete element.data["remote_system__label"];
                    delete element.data["workflow__label"];
                    delete element.data["from_state__label"];
                    delete element.data["to_state__label"];
                    delete element.data["type"];
                    return element.data;
                });
        if(!me.configId) {
            NOC.error(__("Create new diagram not implement"));
            return;
        }
        states = states.map(function(element) {
            element.data.x = element.position.x;
            element.data.y = element.position.y;
            if(element.data["job_handler"] != null && element.data["job_handler"].length === 0) {
                element.data["job_handler"] = null;
            }
            if(element.data.hasOwnProperty("remote_system") && element.data["remote_system"].length === 0) {
                delete element.data["remote_system"];
            }
            if(element.data.hasOwnProperty("remote_id") && element.data["remote_id"].length === 0) {
                delete element.data["remote_id"];
            }
            delete element.data["bi_id"];
            delete element.data["uuid"];
            delete element.data["position"];
            delete element.data["type"];
            delete element.data["update_ttl"];
            delete element.data["workflow"];
            delete element.data["workflow__label"];
            return element.data;
        });
        var ret = Ext.merge(Ext.clone(me.workflow), {states: states, transitions: transitions});
        delete ret["uuid"];
        delete ret["bi_id"];
        delete ret["type"];
        delete ret["id"];
        if(ret["allowed_models"] != null && ret["allowed_models"].length != 0) {
            var allowed_models = [];

            ret["allowed_models"].forEach(function(key) {
                    allowed_models.push(key);
            });
            ret["allowed_models"] = allowed_models;
        }
        Ext.Ajax.request({
            url: "/wf/workflow/" + me.configId + "/config/",
            method: "POST",
            jsonData: ret,
            scope: me,
            success: function() {
                me.onClose();
                NOC.info(__("Config saved"));
            },
            failure: function() {
                NOC.error(__("Failed save data"));
            }
        });
    },
    //
    openBlankMenu: function(evt) {
        var me = this;
        evt.preventDefault();
        me.menuPosition = {x: evt.originalEvent.layerX, y: evt.originalEvent.layerY};
        me.blankMenu.showAt(evt.clientX, evt.clientY);
        me.unhighlight();
    },
    //
    onAddState: function() {
        var stateName = "New State";
        var me = this, view,
            rect = new joint.shapes.standard.Rectangle(),
            data = {
                type: "state",
                name: stateName,
                on_enter_handlers: [],
                on_leave_handlers: [],
                job_handler: null,
                labels: [],
            };
        rect.prop({data: data});
        rect.set("position", me.menuPosition);
        rect.resize(me.stateWidth, me.stateHeight);
        rect.attr("label/text", stateName);
        rect.addTo(me.graph);
        view = rect.findView(me.paper);
        me.currentHighlight = view;
        view.highlight();
        me.addElementTools(view);
        me.showStateInspector(data);
    },
    //
    onRemoveCell: function() {
        var me = this,
            data = me.workflow;

        me.showWorkflowInspector(data);
    },
    //
    loadData: function(data, type) {
        var me = this,
            ret = {type: type},
            record = Ext.create(me.getModelName(type));
        Ext.Object.each(data, function(key, value) {
            if(["states", "transitions"].indexOf(key) === -1) {
                record.set(key, value);
                ret[key] = value;
            }
        });
        return ret;
    },
    //
    getModelName: function(type) {
        switch(type) {
            case "transition":
                return "NOC.wf.transition.Model";
            case "state":
                return "NOC.wf.state.Model";
            case "workflow":
                return "NOC.wf.workflow.Model"
        }
    },
    //
    inspectorDirty: function() {
        var me = this;
        me.isIspectorDirty = true;
    },
    //
    dirtyCheck: function(handler, args) {
        var me = this;
        if(me.isIspectorDirty) {
            Ext.Msg.show({
                title: __("Unsaved data"),
                msg: __("You have unsaved changes in inspector. Save or cancel the changes."),
                buttons: Ext.Msg.YESNOCANCEL,
                icon: Ext.MessageBox.WARNING,
                modal: true,
                scope: me,
                fn: function(button) {
                    var me = this;
                    if(button === "yes") {
                        if(me.onSubmitInspector()) {
                            handler.call(me, args);
                        }
                    }
                    if(button === "no") {
                        me.isIspectorDirty = false;
                        handler.call(me, args);
                    }
                }
            });
        } else {
            handler.call(me, args);
        }
    },
    //
    onClose: function() {
        var me = this;
        me.app.onClose();
    },
    //
    changeStatenameInTransition: function(prevName, newName) {
        var me = this, i, data, cloned,
            cells = me.graph.getCells(),
            len = cells.length,
            replaceProp = function(cell, data) {
                cell.removeProp("data");
                cell.prop({data: data});
            };
        for(i = 0; i < len; i++) {
            data = cells[i].get("data");
            if(data.type === "transition") {
                if(data.from_state === prevName) {
                    cloned = Ext.merge({}, Ext.clone(data), {from_state: newName});
                    replaceProp(cells[i], cloned);
                }
                if(data.to_state === prevName) {
                    cloned = Ext.Object.merge({}, Ext.clone(data), {to_state: newName});
                    replaceProp(cells[i], cloned);
                }
            }
        }
    }
});
