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
        "Ext.ux.form.StringsField"
    ],
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
            // trackResetOnLoad: true,
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
        me.callParent();
        new_load_scripts([
            "/ui/pkg/lodash/lodash.min.js",
            "/ui/pkg/backbone/backbone.min.js",
            "/ui/pkg/dagre/dagre.min.js",
            "/ui/pkg/graphlib/graphlib.min.js",
            "/ui/pkg/joint/joint.min.js",
            "/ui/pkg/joint.layout.directedgraph/joint.layout.directedgraph.min.js",
            "/ui/web/wf/workflow/js/joint.element.Tools.js"
        ], me, me.initMap);
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
            // interactive: Ext.bind(me.onInteractive, me)
        });
        me.paper.on("blank:pointerclick", Ext.bind(me.onSelect, me));
        me.paper.on("cell:pointerclick", Ext.bind(me.onSelect, me));
        me.paper.on("blank:contextmenu", Ext.bind(me.openBlankMenu, me));
        //
        me.graph.on("change:position", function(element, position) {
            var elementView = element.findView(me.paper);
            elementView.removeTools();
        });
        me.graph.on("remove", Ext.bind(me.onRemoveCell, me));
    },
    //
    preview: function(record, backItem) {
        var me = this;
        me.configId = record.get("id");
        if(Ext.isFunction(me.graph.clear)) {
            me.graph.clear();
        }
        me.callParent(arguments);
        // me.draw(me.data());
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
            // .attr("rect/magnet", true);
            // .attr("text/pointer-events", "none");
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
        // var sourceArrowheadTool = new joint.linkTools.SourceArrowhead();
        // var targetArrowheadTool = new joint.linkTools.TargetArrowhead();
        // var sourceAnchorTool = new joint.linkTools.SourceAnchor();
        // var targetAnchorTool = new joint.linkTools.TargetAnchor();
        // var boundaryTool = new joint.linkTools.Boundary();
        var toolsView = new joint.dia.ToolsView({
            tools: [
                verticesTool,
                segmentsTool,
                // sourceArrowheadTool,
                // targetArrowheadTool,
                // sourceAnchorTool,
                // targetAnchorTool,
                // boundaryTool,
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
            return field;
        });
        me.inspector.record = record;
        me.inspector.title = title;
        inspector = Ext.create(me.inspector);
        // inspector.getForm().getFields().each(function (field) {
        //     field.setValue(data[field.name]);
        // });
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
                    xtype: "fieldset",
                    layout: "vbox",
                    title: __("Integration"),
                    defaults: {
                        padding: 4,
                        labelAlign: "top"
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
                    xtype: "fieldset",
                    layout: "vbox",
                    title: __("Integration"),
                    defaults: {
                        padding: 4,
                        labelAlign: "top"
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
                        labelAlign: "top"
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
            me.isIspectorDirty = false;
            if(me.currentHighlight && me.currentHighlight.model) {
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
    onSaveClick: function() {
        var me = this;
        me.dirtyCheck(me.save);
    },
    //
    save: function() {
        var me = this,
            data = me.graph.toJSON();
        var states = data.cells.filter(function(cell) {
            return cell.data.type === "state"
        });
        var transitions = data.cells
        .filter(function(cell) {
            return cell.data.type === "transition"
        })
        .map(function(element) {
            element.from_state = states.filter(function(state) {
                return state.id === element.source.id;
            })[0].data.name;
            element.to_state = states.filter(function(state) {
                return state.id === element.target.id;
            })[0].data.name;
            if(element.hasOwnProperty("vertices")) {
                element.data["vertices"] = element.vertices;
            }
            delete element.data["type"];
            delete element.data["id"];
            return element.data;
        });
        states = states.map(function(element) {
            delete element.data["type"];
            delete element.data["id"];
            element.data.x = element.position.x;
            element.data.y = element.position.y;
            delete element["position"];
            return element.data;
        });
        var ret = Ext.merge(Ext.clone(me.workflow), {states: states, transitions: transitions});
        delete ret["type"];
        delete ret["id"];
        console.log(ret);
        // console.log(JSON.stringify(ret));
        Ext.Ajax.request({
            url: "/wf/workflow/" + me.configId + "/config/",
            method: "POST",
            jsonData: ret,
            scope: me,
            success: function(response) {
                console.log(response);
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
    onAddState: function(item, evt) {
        var stateName = "New State";
        var me = this, view,
            rect = new joint.shapes.standard.Rectangle(),
            data = {
                type: "state",
                name: stateName
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
                // if(record.get(key) !== undefined) {
                record.set(key, value);
                ret[key] = value;
                // }
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
        console.log("inspector changed");
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
    data: function() {
        return {
            states: [
                {
                    is_default: false,
                    update_last_seen: false,
                    is_productive: false,
                    name: "Approved",
                    ttl: 0,
                    on_enter_handlers: ["XXX"],
                    job_handler: null,
                    on_leave_handlers: ["YYY"],
                    update_expired: false,
                    description: "Resource reservation is approved. Resource will became ready when it will be discovered"
                },
                {
                    is_default: false,
                    update_last_seen: false,
                    is_productive: false,
                    name: "Cooldown",
                    ttl: 2592000,
                    on_enter_handlers: [],
                    job_handler: null,
                    on_leave_handlers: [],
                    update_expired: false,
                    description: "Cooldown stage for released resources to prevent reuse collisions"
                },
                {
                    is_default: true,
                    update_last_seen: false,
                    is_productive: false,
                    name: "Free",
                    ttl: 0,
                    on_enter_handlers: [],
                    job_handler: null,
                    on_leave_handlers: [],
                    update_expired: false,
                    description: "Resource is free and can be used"
                },
                {
                    is_default: false,
                    update_last_seen: false,
                    is_productive: true,
                    name: "Ready",
                    ttl: 604800,
                    on_enter_handlers: [],
                    job_handler: null,
                    on_leave_handlers: [],
                    update_expired: true,
                    description: "Resource is in productive usage"
                },
                {
                    is_default: false,
                    update_last_seen: false,
                    is_productive: false,
                    name: "Reserved",
                    ttl: 604800,
                    on_enter_handlers: [],
                    job_handler: null,
                    on_leave_handlers: [],
                    update_expired: false,
                    description: "Resource is temporary reserved/booked. It must be approved explicitly during TTL to became used"
                },
                {
                    is_default: false,
                    update_last_seen: false,
                    is_productive: false,
                    name: "Suspended",
                    ttl: 0,
                    on_enter_handlers: [],
                    job_handler: null,
                    on_leave_handlers: [],
                    update_expired: false,
                    description: "Resource is temporary suspended/blocked for organisational reasons"
                }
            ],
            transitions: [
                {
                    from_state: "Free",
                    to_state: "Ready",
                    enable_manual: true,
                    description: null,
                    handlers: [],
                    is_active: true,
                    event: "seen",
                    label: "Seen"
                },
                {
                    from_state: "Free",
                    to_state: "Reserved",
                    enable_manual: true,
                    description: null,
                    handlers: [],
                    is_active: true,
                    event: "reserve",
                    label: "Reserve"
                },
                {
                    from_state: "Reserved",
                    to_state: "Free",
                    enable_manual: true,
                    description: null,
                    handlers: [],
                    is_active: true,
                    event: "expired",
                    label: "Expired"
                },
                {
                    from_state: "Reserved",
                    to_state: "Approved",
                    enable_manual: true,
                    description: null,
                    handlers: [],
                    is_active: true,
                    event: "approve",
                    label: "Approve",
                    vertices: [{x: 650, y: 430}, {x: 680, y: 230}, {x: 610, y: 70}]
                },
                {
                    from_state: "Approved",
                    to_state: "Ready",
                    enable_manual: true,
                    description: null,
                    handlers: [],
                    is_active: true,
                    event: "seen",
                    label: "Seen"
                },
                {
                    from_state: "Ready",
                    to_state: "Suspended",
                    enable_manual: true,
                    description: null,
                    handlers: [],
                    is_active: true,
                    event: "suspend",
                    label: "Suspend"
                },
                {
                    from_state: "Suspended",
                    to_state: "Ready",
                    enable_manual: true,
                    description: null,
                    handlers: [],
                    is_active: true,
                    event: "resume",
                    label: "Resume"
                },
                {
                    from_state: "Ready",
                    to_state: "Cooldown",
                    enable_manual: true,
                    description: null,
                    handlers: [],
                    is_active: true,
                    event: "expired",
                    label: "Expired"
                },
                {
                    from_state: "Cooldown",
                    to_state: "Ready",
                    enable_manual: true,
                    description: null,
                    handlers: [],
                    is_active: true,
                    event: "seen",
                    label: "Seen"
                },
                {
                    from_state: "Cooldown",
                    to_state: "Free",
                    enable_manual: true,
                    description: null,
                    handlers: [],
                    is_active: true,
                    event: "expired",
                    label: "Expired"
                }
            ],
            name: "Default Resource",
            is_active: true,
            description: "Default resource workflow with external provisioning"
        }
    }
});