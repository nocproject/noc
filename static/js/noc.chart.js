//
// jQuery AJAX Chart extension
// Copyright (C) 2009, nocproject.org
//

// Create closure
(function($){
    // Convert each element to chart
    $.fn.nocchart = function(options) {
        // Extend provided options with default ones
        var opts = $.extend({},$.fn.nocchart.defaults,options);
        // Iterate and draw all matched elements
        this.each(function(){
            $(this).svg({onLoad:function($svg){
                (new Chart($svg,opts)).load(0,0);
            }});
        });
    };
    
    // Chart class
    function Chart($svg, options) {
        this.svg=$svg;
        this.options=new Object(options);
        this.width=this.svg._width();
        this.height=this.svg._height();
        this.drag_x0=null;
        this.offset=($.browser.msie ? 0 : this.svg._svg.offsetLeft);
        this.outline=null;
    };
    // Chart.load
    Chart.prototype.load = function(t0,t1) {
        var url=this.options.ajaxURL;
        if(t0&&t1) {
            url+="?"+this.options.t0Name+"="+t0+"&"+this.options.t1Name+"="+t1;
        }
        chart=this;
        $.ajax({
            dataType: "json",
            url     : url,
            success : function(data) {chart.draw(data);}
        });
    }
    // Chart.clear -- clear chart area
    Chart.prototype.clear = function() {
        this.svg.clear();
    }
    //
    Chart.prototype.plotColor = function(i) {
        return this.options.colors[i];
    }
    // Set data
    Chart.prototype.setData = function(data) {
        this.time_series=data["time_series"];
        this.min_v=data["min_v"];
        this.max_v=data["max_v"];
        this.min_ts=data["min_ts"];
        this.max_ts=data["max_ts"];
        this.points=data["points"];
    }
    // Chart.draw
    Chart.prototype.draw = function(data) {
        this.clear();
        this.setData(data);
        this.drawLegend();
        this.setScales();
        // this.drawDebugGrid();
        this.drawMainField();
        this.drawXLabels();
        this.drawYLabels();
        this.drawPlots();
        this.addControls();
    };
    //
    Chart.prototype.drawDebugGrid = function() {
        // Bounding box
        this.svg.rect(0,0,this.width,this.height,{fill:"white",stroke:'red',strokeWidth:1});
        // Vertical
        var g_step=10;
        var style={stroke:'red',strokeWidth:1};
        for(x=g_step;x<this.width;x+=g_step) {
            this.svg.line(x,0,x,this.height,style);
        }
        // Horizontal
        for(y=g_step;y<this.height;y+=g_step) {
            this.svg.line(0,y,this.width,y,style);
        };
    }
    // Chart.legendColumnWidths
    Chart.prototype.legendColumnWidths = function() {
        var N=this.time_series.length;
        for(var lines=1;lines<=N;lines++) {
            var columns=Math.ceil(N/lines);
            var widths=[];
            var total_width=0;
            for(var j=0;j<columns;j++) {
                var w=0;
                for(k=j;k<N;k+=columns) {
                    var w1=this.time_series[k].length*this.options.fontWidth+3*this.options.textPadding+this.options.fontHeight;
                    if(w1>w) {
                        w=w1;
                    }
                }
                widths[j]=w;
                total_width+=w;
                if(total_width>this.width) {
                    break;
                }
            }
            if(total_width<widths) {
                break;
            }
        }
        return widths;
    };
    // Chart.drawLegend
    Chart.prototype.drawLegend = function() {
        var x=0;
        var widths=this.legendColumnWidths();
        var columns=widths.length;
        var N=this.time_series.length;
        var rows=Math.ceil(N/columns);
        for(col=0;col<columns;col++) {
            for(row=0;row<rows;row++) {
                var i=row*columns+col;
                if(i>=N)
                    continue;
                var y=row*(2*this.options.textPadding+this.options.fontHeight)+this.options.textPadding+this.options.fontHeight;
                this.svg.rect(x+this.options.textPadding,y-this.options.fontHeight,
                    this.options.fontHeight,this.options.fontHeight,
                    {fill:this.plotColor(i),stroke:"black",strokeWidth:1});
                this.svg.text(x+2*this.options.textPadding+this.options.fontHeight,y,
                    this.time_series[i],{fontFamily: this.options.fontFamily, fontSize: this.options.fontSize});
            }
            x+=widths[col];
        }
        this.legend_height=rows*(2*this.options.textPadding+this.options.fontHeight);
    };
    //
    Chart.prototype.setScales = function() {
        this.labels_height=8*this.options.fontWidth+2*this.options.textPadding; // 8 chars
        this.x0=this.options.textPadding+1;
        this.y0=this.height-this.labels_height-2*this.options.textPadding-1;
        this.x1=this.width-2-2*this.options.textPadding-8*this.options.fontWidth;
        this.y1=this.legend_height+2*this.options.textPadding+1;
        this.x_scale=(this.x1-this.x0)/(this.max_ts-this.min_ts);
        this.y_scale=(this.y1-this.y0)/(this.max_v-this.min_v);
    }
    //
    Chart.prototype.drawMainField = function() {
        this.main_field=$(this.svg.rect(this.x0,this.y1,this.x1-this.x0,this.y0-this.y1,
            {'fill':"#c0c0c0",stroke:'black',strokeWidth:1}));
    };
    //
    Chart.prototype.drawXLabels = function() {
        var delta=(this.options.fontHeight+2*this.options.textPadding)/this.x_scale;
        var ltw=delta;
        var d=new Date();
        // Find appropriative step
        for(i=0;i<this.options.labelScales.length;i++) {
            if(ltw<=this.options.labelScales[i]) {
                label_delta=this.options.labelScales[i];
                break;
            }
        }
        //
        var lg=this.svg.group({fontFamily: this.options.fontFamily,fontSize:this.options.fontSize});
        var baseline=this.height-this.options.textPadding;
        
        for(lt=Math.floor(this.max_ts/delta)*delta;lt>this.min_ts;lt-=label_delta) {
            var x=this.get_x(lt);
            d.setTime(lt*1000);
            var l1=this.pad2(d.getDate())+"."+this.pad2(d.getMonth()+1)+"."+this.pad2(d.getFullYear());
            var l2=this.pad2(d.getHours())+":"+this.pad2(d.getMinutes())+":00";
            var lg=this.svg.group({fontFamily: this.options.fontFamily, fontSize: this.options.fontSize});
            this.svg.line(x,this.y1,x,this.y0,{stroke:'#d0d0d0'});
            // day label
            var g=this.svg.group(this.svg.group(lg,
                {transform:'translate('+x+','+baseline+')'}),
                    {transform:'rotate(-90)'});
            this.svg.text(g,0,0,l1);
            // time label
            var g=this.svg.group(this.svg.group(lg,
                {transform:'translate('+(x+this.options.fontHeight)+','+baseline+')'}),
                    {transform:'rotate(-90)'});
            this.svg.text(g,0,0,l2);
        }
    };
    // Draw Y-labels
    Chart.prototype.drawYLabels = function() {
        // Draw y-labels
        var baseline=this.x1+this.options.textPadding;
        var zy=this.get_y(0);
        var lg=this.svg.group({fontFamily: this.options.fontFamily, fontSize: this.options.fontSize});
        var f_offset=this.options.fontHeight/2;
        // Draw zero line
        this.svg.line(this.x0, zy, this.x1, zy, {stroke:'#f0f0f0'});
        this.svg.text(lg,baseline,zy+f_offset,"0");
        // Lower bound label
        if(this.y0-zy>this.options.fontHeight+this.options.textPadding) {
            this.svg.text(lg,baseline,this.y0+f_offset,this.formatValue(this.min_v));
        }
        // Upper bound label
        if(zy-this.y1>this.options.fontHeight+this.options.textPadding) {
            this.svg.text(lg,baseline,this.y1+f_offset,this.formatValue(this.max_v));
        }
    };
    //
    Chart.prototype.drawPlots = function() {
        for(i=0;i<this.points.length;i++) {
            var p=[];
            for(j=0;j<this.points[i].length;j++) {
                var z=this.points[i][j];
                var t=z[0];
                var v=z[1];
                p[j]=[this.get_x(t),this.get_y(v)];
            }
            this.svg.polyline(p,{fill:"none", stroke:this.plotColor(i), strokeWidth: 1});
        }
    };
    //
    Chart.prototype.get_x = function(t) {
        return this.x0+this.x_scale*(t-this.min_ts);
    }
    //
    Chart.prototype.get_y = function(v) {
        return this.y0+this.y_scale*(v-this.min_v);
    }
    
    Chart.prototype.get_t = function(x) {
        return Math.floor((x-this.x0)/this.x_scale+this.min_ts);
    };    
    //
    Chart.prototype.pad2 = function(n) {
        if(n>=100) {
            n=n%100;
        }
        if(n<10) {
            return "0"+String(n);
        } else {
            return String(n);
        }
    };
    // Fit value to 7 symbols
    Chart.prototype.formatValue = function(v) {
        if(v==0) {
            return "0";
        }
        var sign="";
        if(v<0){
            sign="-";
            v=-v;
        }
        if(v<1000.0) {
            return sign+String(v).substring(0,5);
        }
        if(v<1000000.0) {
            return sign+String(v/1000.0).substring(0,5)+"k";
        }
        if(v<1000000000.0) {
            return sign+String(v/1000000.0).substring(0,5)+"M";
        }
        if(v<1000000000000.0) {
            return sign+String(v/1000000000.0).substring(0,5)+"G";
        }
        if(v<1000000000000000.0) {
            return sign+String(v/1000000000000.0).substring(0,5)+"T";
        }
        return sign+String(v/1000000000000000.0).substring(0,5)+"P";
    };
    //
    Chart.prototype.eventClosure = function(obj,methodName) {
        return (function(e) {
            return obj[methodName](e,this);
        });
    };
    //
    Chart.prototype.addControls = function() {
        // Initialize scripts
        this.svg.script('function scroll_left(evt) {evt.target.chart.scrollLeft();}');
        this.svg.script('function scroll_right(evt) {evt.target.chart.scrollRight();}');
        this.svg.script('function zoom_up(evt) {evt.target.chart.zoomUp();}');
        this.svg.script('function zoom_down(evt) {evt.target.chart.zoomDown();}');
        
        // Draw controls
        var cg=this.svg.group({stroke:'black',strokeWidth: 2,fill:'yellow',opacity:"0.25"});
        var y_baseline=(this.y0+this.y1)/2;
        var a_s=this.options.fontWidth*2;
        // Left Arrow
        var x_baseline=this.x0+this.options.textPadding;
        var obj=this.svg.polyline(cg,[[x_baseline,y_baseline],[x_baseline+a_s,y_baseline-a_s],
            [x_baseline+a_s,y_baseline+a_s],[x_baseline,y_baseline]],{onclick:'scroll_left(evt)'});
        obj.chart=this;
        // Right Arrow
        var x_baseline=this.x1-this.options.textPadding;
        obj=this.svg.polyline(cg,[[x_baseline,y_baseline],[x_baseline-a_s,y_baseline-a_s],
            [x_baseline-a_s,y_baseline+a_s],[x_baseline,y_baseline]],{onclick:'scroll_right(evt)'});
        obj.chart=this;
        // Scale
        var c_x=this.x0+a_s/2+this.options.textPadding;
        var c_y=this.y0-a_s/2-this.options.textPadding;
        
        // Zoom down
        obj=this.svg.circle(cg,c_x,c_y,a_s/2,{onclick:'zoom_down(evt)'}); 
        obj.chart=this;
        obj=this.svg.line(cg,c_x-a_s/4,c_y,c_x+a_s/4,c_y,{onclick:'zoom_down(evt)'});
        obj.chart=this;
        obj=this.svg.line(cg,c_x,c_y-a_s/4,c_x,c_y+a_s/4,{onclick:'zoom_down(evt)'});
        obj.chart=this;
        
        c_y-=a_s+this.options.textPadding;
        // Zoom up
        obj=this.svg.circle(cg,c_x,c_y,a_s/2,{onclick:'zoom_up(evt)'});
        obj.chart=this;
        obj=this.svg.line(cg,c_x-a_s/4,c_y,c_x+a_s/4,c_y,{onclick:'zoom_up(evt)'});
        obj.chart=this;
        // Dragging
        this.main_field.mousedown(this.eventClosure(this,"startDrag")).mouseup(this.eventClosure(this,"stopDrag")).mousemove(this.eventClosure(this,"dragging"));
    };
    //
    Chart.prototype.scrollLeft = function() {
        var delta=(this.max_ts-this.min_ts)/2;
        this.load(this.min_ts-delta,this.max_ts-delta);
    };
    //
    Chart.prototype.scrollRight = function() {
        var delta=(this.max_ts-this.min_ts)/2;
        this.load(this.min_ts+delta,this.max_ts+delta);
    };
    //
    Chart.prototype.zoomUp = function() {
        var center=Math.round((this.min_ts+this.max_ts)/2);
        var leg=Math.round((this.max_ts-this.min_ts)*1.618/2);
        this.load(center-leg,center+leg);
    };
    //
    Chart.prototype.zoomDown = function() {
        var center=Math.round((this.min_ts+this.max_ts)/2);
        var leg=Math.round((this.max_ts-this.min_ts)/1.618/2);
        this.load(center-leg,center+leg);
    };
    //
    Chart.prototype.startDrag = function(event) {
        this.drag_x0=event.clientX-this.offset;
    };
    //
    Chart.prototype.stopDrag = function(event) {
        if(!this.outline) {
            return;
        }
        $(this.outline).remove();
        this.outline=null;
        var drag_x1=event.clientX-this.offset;
        var t0,t1;
        if(drag_x1>this.drag_x0) {
            t0=this.get_t(this.drag_x0);
            t1=this.get_t(drag_x1);
        } else {
            t0=this.get_t(drag_x1);
            t1=this.get_t(this.drag_x0);
        }
        this.drag_x0=null;
        this.load(t0,t1);
    };
    //
    Chart.prototype.dragging = function(event) {
        if(!this.drag_x0) {
            return
        };
        var drag_x1=event.clientX-this.offset;
        var width,x;
        if(drag_x1>this.drag_x0) {
            x=this.drag_x0;
            width=drag_x1-this.drag_x0;
        } else {
            x=drag_x1;
            width=this.drag_x0-drag_x1;
        }
        var height=this.y0-this.y1;
        if(!this.outline) {
            this.outline=this.svg.rect(0,0,0,0,{fill: '#d0d0d0', stroke: '#e0e0e0', strokeWidth: 1, strokeDashArray: '2,2',opacity:"0.5"});
            $(this.outline).mouseup(this.eventClosure(this,"stopDrag"));
        }
        this.svg.change(this.outline,{x:x,y:this.y0-height,width:width,height:height});
    };
    // Default Values
    $.fn.nocchart.defaults = {
        fontFamily  : "Verdana",
        fontHeight  : 10,
        fontWidth   : 8,
        textPadding : 2,
        ajaxURL     : "",
        t0Name      : "t0",
        t1Name      : "t1",
        colors      : ["#0000FF","#7D00FF","#FF00FF","#FF007D","#FF0000","#FF7D00","#FFFF00","#7DFF00","#00FF00","#00FF7D","#00FFFF","#007DFF"],
        labelScales : [60,3600,86400,2592000]
    };
    // End of closure
})(jQuery);
