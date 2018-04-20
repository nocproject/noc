/*
 * jQuery plugin to Rotate text
 * Copyright (C) 2007-2009 The NOC Project
 * See LICENSE for details
 */
(function($){
    $.fn.rotate_text = function(settings) {
        var config={"fontHeight":12,"fontWidth":8,"textPadding":2};
        
        if(settings) $.extend(config,settings);
        
        var baseline=0;
        var TP=config["textPadding"];
        var FH=config["fontHeight"];
        var FW=config["fontWidth"];
        var x0=config["fontHeight"]+config["textPadding"];
        // Calculate baseline
        this.each(function() {
            var tl=$(this).html().length;
            var bl=tl*FW+TP;
            if(bl>baseline) {
                baseline=bl;
            }
        });
        // Rotate text
        this.each(function(){
            var $t=$(this);
            var $text=$t.html();
            $t.html("");
            $t.width(FH+2*TP);
            $t.height(baseline+TP);
            $t.svg(function(svg){
                var g=svg.group(
                        svg.group(svg.group({fontFamily: 'Verdana',fontSize:FH}),
                            {transform:'translate('+x0+','+baseline+')'}),
                                {transform:'rotate(-90)'});
                svg.text(g,0,0,$text);
            });
        });
    }
})(jQuery);
