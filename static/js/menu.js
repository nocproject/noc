/*
 * Navigation menu
 * Copyright (C) 2007-2009 The NOC Project
 * See LICENSE for details
 */
function app_click(e) {
    e.data.toggleClass("active_ul");
    e.data.toggleClass("collapsed_ul");
}
/*
 * Build Menu from JSON response
 */
function build_menu(menu_data) {
    // Extract application name
    var app=document.location.pathname;
    if(app.substring(0,7)=="/admin/") {
        app=app.slice(6);
    }
    if(app.substring(0,13)=="/main/report/") {
        app=app.slice(13);
        var idx=app.search("\\.");
        if(idx!=-1) {
            app=app.slice(0,idx)
        }
    } else {
        app=app.slice(1);
        var idx=app.search("/");
        if(idx!=-1) {
            app=app.slice(0,idx);
        }
    }
    // Build menu
    var $menu=$("#menu");
    jQuery.each(menu_data,function(i,r){
        var $app_div=$(document.createElement("div"));
        $menu.append($app_div);
        $app_div.addClass("app");
        var $app_title=$(document.createElement("div"));
        $app_div.append($app_title);
        $app_title.html(r["title"]);
        $app_title.addClass("app_title");
        var $app_list=$(document.createElement("ul"));
        $app_div.append($app_list);
        $app_list.addClass("collapsed_ul");
        $app_title.bind("click",$app_list,app_click);
        /* Create menu items */
        jQuery.each(r["items"], function(i,x){
            var $li=$(document.createElement("li"));
            $app_list.append($li);
            var $a=$(document.createElement("a"));
            $li.append($a);
            $a.html(x[0]);
            if(typeof(x[1])=="string") {
                $a.attr("href",x[1]);
            } else {
                var $n_ul=$(document.createElement("ul"));
                $li.append($n_ul);
                /* Create nested menu items */
                jQuery.each(x[1]["items"], function(j,y){
                    var $n_li=$(document.createElement("li"));
                    $n_ul.append($n_li);
                    var $n_a=$(document.createElement("a"));
                    $n_li.append($n_a);
                    $n_a.html(y[0]);
                    $n_a.attr("href",y[1]);
                });
            }
        });
        // Expand current application
        if(app==r["app"]) {
            $app_list.toggleClass("active_ul");
            $app_list.toggleClass("collapsed_ul");
        }
    });
}
/*
 * Request for menu
 */
function menu() {
    jQuery.getJSON("/main/menu/",build_menu)
}
