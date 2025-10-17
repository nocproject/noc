/* eslint-disable */
(function (joint, util, V, g) {

var ToolView = joint.dia.ToolView;

var Button = ToolView.extend({
  name: "button",
  events: {
    "mousedown": "onPointerDown",
    "touchstart": "onPointerDown",
  },
  options: {
    distance: 0,
    offset: 0,
    rotate: false,
  },
  update: function(){
    var position = {
      x: this.relatedView.model.attributes.position.x + this.options.distance,
      y: this.relatedView.model.attributes.position.y,
    };
    var matrix = V.createSVGMatrix()
            .translate(position.x, position.y)
            .translate(0, this.options.offset || 0);
    this.vel.transform(matrix, {absolute: true});
    return this;
  },
  onRender: function(){
    this.renderChildren(this.options.markup);
    this.update()
  },
  onPointerDown: function(evt){
    evt.stopPropagation();
    var actionFn = this.options.action;
    if(typeof actionFn === "function"){
      actionFn.call(this.relatedView, evt, this.relatedView);
    }
  },
});

var Remove = Button.extend({
  children: [{
    tagName: "circle",
    selector: "button",
    attributes: {
      "r": 7,
      "fill": "#FF1D00",
      "cursor": "pointer",
    },
  }, {
    tagName: "path",
    selector: "icon",
    attributes: {
      "d": "M -3 -3 3 3 M -3 3 3 -3",
      "fill": "none",
      "stroke": "#FFFFFF",
      "stroke-width": 2,
      "pointer-events": "none",
    },
  }],
  options: {
    distance: 0,
    offset: 0,
    action: function(){
      this.model.remove({ui: true, tool: this.cid});
    },
  },
});

var AddLink = Button.extend({
  children: [{
    tagName: "circle",
    selector: "button",
    attributes: {
      "r": 5,
      "stroke": "black",
      "stroke-width": 1,
      "fill": "white",
      "cursor": "pointer",
    },
  }],
  options: {
    distance: 0,
    offset: 0,
    action: function(evt){
      var link = new joint.shapes.standard.Link(),
        x = evt.originalEvent.layerX,
        y = evt.originalEvent.layerY,
        defaultName = "New Link";
      link.source(this.model);
      link.target({x: x + 50, y: y});
      link.appendLabel({
        attrs: {
          text: {
            text: defaultName,
          },
        },
      });
      link.addTo(this.paper.model);
      var linkView = link.findView(this.paper);
      linkView.startArrowheadMove("target");

      $(document).on({
        "mousemove.addLink": onDrag,
        "mouseup.addLink": onDragEnd,
      }, {
        // shared data between listeners
        view: linkView,
        paper: this.paper,
      });


      function onDrag(evt){
        // transform client to paper coordinates
        var p = evt.data.paper.snapToGrid({
          x: evt.clientX,
          y: evt.clientY,
        });
        // manually execute the linkView mousemove handler
        evt.data.view.pointermove(evt, p.x, p.y);
      }

      function onDragEnd(evt){
        var sourceId = evt.data.paper.model.getCell(evt.data.view.model.attributes.source.id),
          source = evt.data.paper.model.getCell(sourceId),
          targets = evt.data.paper.findViewsFromPoint({
            x: evt.originalEvent.layerX,
            y: evt.originalEvent.layerY,
          });

        if(targets.length && targets[0].model.id !== source.id){
          evt.data.view.model.target(targets[0]);
          evt.data.view.model.prop({
            data: {
              type: "transition",
              label: defaultName,
              enable_manual: false,
              handlers: [],
              event: null,
              from_state: source.get("data").name,
              to_state: targets[0].model.get("data").name,
            },
          });
        } else{
          evt.data.view.model.remove();
        }
        // manually execute the linkView mouseup handler
        evt.data.view.pointerup(evt);
        $(document).off(".addLink");
      }
    },
  },
});

// Export
joint.elementTools = {
  Remove: Remove,
  AddLink: AddLink,
};

})(joint, joint.util, V, g);