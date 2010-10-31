/**
 * Really Simple Color Picker in jQuery
 * 
 * Copyright (c) 2008 Lakshan Perera (www.laktek.com)
 * Licensed under the MIT (MIT-LICENSE.txt)  licenses.
 * 
 */

(function($){
  $.fn.colorPicker = function(){    
    if(this.length > 0) buildSelector();
    return this.each(function(i) { 
      buildPicker(this)}); 
  };
  
  var selectorOwner;
  var selectorShowing = false;
  
  buildPicker = function(element){
    //build color picker
    control = $("<div class='color_picker'>&nbsp;</div>")
    control.css('background-color', $(element).val());
    
    //bind click event to color picker
    control.bind("click", toggleSelector);
    
    //add the color picker section
    $(element).after(control);

    //add even listener to input box
    $(element).bind("change", function() {
      selectedValue = toHex($(element).val());
      $(element).next(".color_picker").css("background-color", selectedValue);
    });
    
    //hide the input box
    $(element).hide();

  };
  
  buildSelector = function(){
    selector = $("<div id='color_selector'></div>");

     //add color pallete
     $.each($.fn.colorPicker.defaultColors, function(i){
      swatch = $("<div class='color_swatch'>&nbsp;</div>")
      swatch.css("background-color", "#" + this);
      swatch.bind("click", function(e){ changeColor($(this).css("background-color")) });
      swatch.bind("mouseover", function(e){ 
        $(this).css("border-color", "#598FEF"); 
        $("input#color_value").val(toHex($(this).css("background-color")));    
        }); 
      swatch.bind("mouseout", function(e){ 
        $(this).css("border-color", "#000");
        $("input#color_value").val(toHex($(selectorOwner).css("background-color")));
        });
      
     swatch.appendTo(selector);
     });
  
     //add HEX value field
     hex_field = $("<label for='color_value'>Hex</label><input type='text' size='8' id='color_value'/>");
     hex_field.bind("keydown", function(event){
      if(event.keyCode == 13) {changeColor($(this).val());}
      if(event.keyCode == 27) {toggleSelector()}
     });
     
     $("<div id='color_custom'></div>").append(hex_field).appendTo(selector);

     $("body").append(selector); 
     selector.hide();
  };
  
  checkMouse = function(event){
    //check the click was on selector itself or on selectorOwner
    var selector = "div#color_selector";
    var selectorParent = $(event.target).parents(selector).length;
    if(event.target == $(selector)[0] || event.target == selectorOwner || selectorParent > 0) return
    
    hideSelector();   
  }
  
  hideSelector = function(){
    var selector = $("div#color_selector");
    
    $(document).unbind("mousedown", checkMouse);
    selector.hide();
    selectorShowing = false
  }
  
  showSelector = function(){
    var selector = $("div#color_selector");
    
    //alert($(selectorOwner).offset().top);
    
    selector.css({
      top: $(selectorOwner).offset().top + ($(selectorOwner).outerHeight()),
      left: $(selectorOwner).offset().left
    }); 
    hexColor = $(selectorOwner).prev("input").val();
    $("input#color_value").val(hexColor);
    selector.show();
    
    //bind close event handler
    $(document).bind("mousedown", checkMouse);
    selectorShowing = true 
   }
  
  toggleSelector = function(event){
    selectorOwner = this; 
    selectorShowing ? hideSelector() : showSelector();
  }
  
  changeColor = function(value){
    if(selectedValue = toHex(value)){
      $(selectorOwner).css("background-color", selectedValue);
      $(selectorOwner).prev("input").val(selectedValue).change();
    
      //close the selector
      hideSelector();    
    }
  };
  
  //converts RGB string to HEX - inspired by http://code.google.com/p/jquery-color-utils
  toHex = function(color){
    //valid HEX code is entered
    if(color.match(/[0-9a-fA-F]{3}$/) || color.match(/[0-9a-fA-F]{6}$/)){
      color = (color.charAt(0) == "#") ? color : ("#" + color);
    }
    //rgb color value is entered (by selecting a swatch)
    else if(color.match(/^rgb\(([0-9]|[1-9][0-9]|[1][0-9]{2}|[2][0-4][0-9]|[2][5][0-5]),[ ]{0,1}([0-9]|[1-9][0-9]|[1][0-9]{2}|[2][0-4][0-9]|[2][5][0-5]),[ ]{0,1}([0-9]|[1-9][0-9]|[1][0-9]{2}|[2][0-4][0-9]|[2][5][0-5])\)$/)){
      var c = ([parseInt(RegExp.$1),parseInt(RegExp.$2),parseInt(RegExp.$3)]);
      
      var pad = function(str){
            if(str.length < 2){
              for(var i = 0,len = 2 - str.length ; i<len ; i++){
                str = '0'+str;
              }
            }
            return str;
      }

      if(c.length == 3){
        var r = pad(c[0].toString(16)),g = pad(c[1].toString(16)),b= pad(c[2].toString(16));
        color = '#' + r + g + b;
      }
    }
    else color = false;
    
    return color
  }

  
  //public methods
  $.fn.colorPicker.addColors = function(colorArray){
    $.fn.colorPicker.defaultColors = $.fn.colorPicker.defaultColors.concat(colorArray);
  };
  
  $.fn.colorPicker.defaultColors = 
    ['000000', '000033', '000066', '000099', '0000CC', '0000FF', '003300', '003333', '003366', '003399', '0033CC', '0033FF',
    '006600', '006633', '006666', '006699', '0066CC', '0066FF', '009900', '009933', '009966', '009999', '0099CC', '0099FF',
    '00CC00', '00CC33', '00CC66', '00CC99', '00CCCC', '00CCFF', '00FF00', '00FF33', '00FF66', '00FF99', '00FFCC', '00FFFF',
    '330000', '330033', '330066', '330099', '3300CC', '3300FF', '333300', '333333', '333366', '333399', '3333CC', '3333FF',
    '336600', '336633', '336666', '336699', '3366CC', '3366FF', '339900', '339933', '339966', '339999', '3399CC', '3399FF',
    '33CC00', '33CC33', '33CC66', '33CC99', '33CCCC', '33CCFF', '33FF00', '33FF33', '33FF66', '33FF99', '33FFCC', '33FFFF',
    '660000', '660033', '660066', '660099', '6600CC', '6600FF', '663300', '663333', '663366', '663399', '6633CC', '6633FF',
    '666600', '666633', '666666', '666699', '6666CC', '6666FF', '669900', '669933', '669966', '669999', '6699CC', '6699FF',
    '66CC00', '66CC33', '66CC66', '66CC99', '66CCCC', '66CCFF', '66FF00', '66FF33', '66FF66', '66FF99', '66FFCC', '66FFFF',
    '990000', '990033', '990066', '990099', '9900CC', '9900FF', '993300', '993333', '993366', '993399', '9933CC', '9933FF',
    '996600', '996633', '996666', '996699', '9966CC', '9966FF', '999900', '999933', '999966', '999999', '9999CC', '9999FF',
    '99CC00', '99CC33', '99CC66', '99CC99', '99CCCC', '99CCFF', '99FF00', '99FF33', '99FF66', '99FF99', '99FFCC', '99FFFF',
    'CC0000', 'CC0033', 'CC0066', 'CC0099', 'CC00CC', 'CC00FF', 'CC3300', 'CC3333', 'CC3366', 'CC3399', 'CC33CC', 'CC33FF',
    'CC6600', 'CC6633', 'CC6666', 'CC6699', 'CC66CC', 'CC66FF', 'CC9900', 'CC9933', 'CC9966', 'CC9999', 'CC99CC', 'CC99FF',
    'CCCC00', 'CCCC33', 'CCCC66', 'CCCC99', 'CCCCCC', 'CCCCFF', 'CCFF00', 'CCFF33', 'CCFF66', 'CCFF99', 'CCFFCC', 'CCFFFF',
    'FF0000', 'FF0033', 'FF0066', 'FF0099', 'FF00CC', 'FF00FF', 'FF3300', 'FF3333', 'FF3366', 'FF3399', 'FF33CC', 'FF33FF',
    'FF6600', 'FF6633', 'FF6666', 'FF6699', 'FF66CC', 'FF66FF', 'FF9900', 'FF9933', 'FF9966', 'FF9999', 'FF99CC', 'FF99FF',
    'FFCC00', 'FFCC33', 'FFCC66', 'FFCC99', 'FFCCCC', 'FFCCFF', 'FFFF00', 'FFFF33', 'FFFF66', 'FFFF99', 'FFFFCC', 'FFFFFF'];
  
})(jQuery);

