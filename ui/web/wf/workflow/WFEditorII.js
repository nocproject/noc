//---------------------------------------------------------------------
// Workflow editor, JointJS version
//---------------------------------------------------------------------
// Copyright (C) 2007-2018 The NOC Project
// See LICENSE for details
//---------------------------------------------------------------------
console.debug("Defining NOC.wf.workflow.WFEditorII");

Ext.define("NOC.wf.workflow.WFEditorII", {
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
                type: 'hbox',
                align: 'stretch'
            },
            items: [
                {
                    xtype: "container",
                    itemId: "container",
                    flex: 4
                },
                {
                    xtype: "form",
                    itemId: "inspector",
                    flex: 1,
                    scrollable: "vertical",
                    bodyPadding: '10',
                    defaults: {
                        labelAlign: "top",
                        width: "100%"
                    },
                    blur: me.onSubmitInspector,
                    listeners: {
                        scope: me,
                        // deactivate: me.onSubmitInspector,
                        statesave: me.onSubmitInspector
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
        me.workflow = {type: "workflow", name: "", description: ""};
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
        if(Ext.isFunction(me.graph.clear)) {
            me.graph.clear();
        }
        me.draw(me.data());
        me.callParent(arguments);
        // Ext.Ajax.request({
        //     url: "/wf/workflow/" + record.get("id") + "/config/",
        //     method: "GET",
        //     scope: me,
        //     success: function(response) {
        //         var data = Ext.decode(response.responseText);
        //         console.log(data);
        //     },
        //     failure: function() {
        //         NOC.error(__("Failed to get data"));
        //     }
        // });
    },
    //
    draw: function(data) {
        var me = this, x = 200, y = 40,
            inspector = me.getComponent("inspector");
        var stateByName = function(name) {
            return me.graph.getElements().filter(function(element) {
                return element.attr("label/text") === name;
            })
        };

        me.workflow = Ext.merge(me.workflow, {name: data.name, description: data.description});
        data.states.forEach(function(state) {
            var rect = new joint.shapes.standard.Rectangle();
            rect.set("position", {x: x, y: y});
            rect.resize(me.stateWidth, me.stateHeight);
            rect.attr("label/text", state.name);
            // .attr("rect/magnet", true);
            // .attr("text/pointer-events", "none");
            rect.prop({
                data: {
                    type: "state",
                    is_default: state.is_default,
                    update_last_seen: state.update_last_seen,
                    is_productive: state.is_productive,
                    name: state.name,
                    ttl: state.ttl,
                    on_enter_handlers: state.on_enter_handlers,
                    job_handler: state.job_handler,
                    on_leave_handlers: state.on_leave_handlers,
                    update_expired: state.update_expired,
                    description: state.description
                }
            });
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
                    link.prop({
                        data: {
                            type: "transition",
                            from_state: transition.from_state,
                            to_state: transition.to_state,
                            enable_manual: transition.enable_manual,
                            description: transition.description,
                            handlers: transition.handlers,
                            is_active: transition.is_active,
                            event: transition.event,
                            label: transition.label
                        }
                    });
                    link.addTo(me.graph);
                });
            });
        });
        joint.layout.DirectedGraph.layout(me.graph, {
            marginX: 50,
            marginY: 50,
            nodeSep: 100,
            edgeSep: 80,
            rankDir: "TB"
        });
        me.showWorkflowInspector(inspector, me.workflow);
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
        var me = this,
            inspector = me.getComponent("inspector"),
            data = me.workflow;

        me.unhighlight();
        if(view.model) {
            data = view.model.get("data");
            me.currentHighlight = view;
            view.highlight();
        }
        switch(data.type) {
            case "state": {
                this.addElementTools(view);
                me.showStateInspector(inspector, data);
                break;
            }
            case "transition": {
                this.addLinkTools(view);
                me.showTransitionInspector(inspector, data);
                break;
            }
            case "workflow": {
                me.showWorkflowInspector(inspector, data);
                break;
            }
        }
    },
    //
    clearInspector: function(inspector) {
        inspector.removeAll();
    },
    //
    showInspector: function(record, data, inspector, fields, title) {
        var me = this;

        record.set(data);
        me.clearInspector(inspector);
        inspector.add(fields);
        inspector.loadRecord(record);
        inspector.setTitle(title);
    },
    //
    showWorkflowInspector: function(inspector, data) {
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
            ],
            record = Ext.create("NOC.wf.workflow.Model");

        me.showInspector(record, data, inspector, fields, __("Workflow Inspector"));
    },
    //
    showStateInspector: function(inspector, data) {
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
            ],
            record = Ext.create("NOC.wf.state.Model");

        me.showInspector(record, data, inspector, fields, __("State Inspector"));
    },
    //
    showTransitionInspector: function(inspector, data) {
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
            ],
            record = Ext.create("NOC.wf.transition.Model");

        me.showInspector(record, data, inspector, fields, __("Transition Inspector"));
    },
    //
    onSubmitInspector: function() {
        var me = this,
            data,
            form = me.getComponent("inspector"),
            record = form.getRecord();

        if(form.isValid()) {
            form.updateRecord(record);
            data = record.getData();
            if(me.currentHighlight && me.currentHighlight.model) {
                me.currentHighlight.model.prop({data: data});
                switch(me.currentHighlight.model.get('data').type) {
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
                me.workflow = Ext.merge(me.workflow, data);
            }
        }
    },
    //
    onSaveClick: function() {
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
            delete element.data['type'];
            delete element.data['id'];
            return element.data;
        });
        states = states.map(function(element) {
            delete element.data['type'];
            delete element.data['id'];
            element.data.position = element.position;
            return element.data;
        });
        var ret = Ext.merge(Ext.clone(me.workflow), {states: states, transitions: transitions});
        delete ret['type'];
        delete ret['id'];
        // console.log(ret);
        console.log(JSON.stringify(ret));
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
            inspector = me.getComponent("inspector"),
            rect = new joint.shapes.standard.Rectangle(),
            data = {
                type: "state",
                name: stateName
                // is_default: state.is_default,
                // update_last_seen: state.update_last_seen,
                // is_productive: state.is_productive,
                // ttl: state.ttl,
                // on_enter_handlers: state.on_enter_handlers,
                // job_handler: state.job_handler,
                // on_leave_handlers: state.on_leave_handlers,
                // update_expired: state.update_expired,
                // description: state.description
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
        me.showStateInspector(inspector, data);
    },
    //
    onRemoveCell: function() {
        var me = this,
            inspector = me.getComponent("inspector"),
            data = me.workflow;

        me.showWorkflowInspector(inspector, data);
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
                    on_enter_handlers: [],
                    job_handler: null,
                    on_leave_handlers: [],
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
                    label: "Approve"
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
            description: "Default resource workflow with external provisioning"
        }
    }
});