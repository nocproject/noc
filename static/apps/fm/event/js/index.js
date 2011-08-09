function show_result(data) {
    add_cell = function(row, html) {
        var $td = $(document.createElement("td"));
        $td.html(html);
        row.append($td);
        return $td;
    }
    
    add_cells = function(row, cells) {
        $.each(cells, function(i, d) {
            add_cell(row, d)
        });
    }
    
    var n = 0;
    var tb=$("#events_table TBODY");
    tb.empty();
    $.each(data["events"],function(i,r){
        var $tr=$(document.createElement("tr"));
        var rc = "row" + ((n % 2) + 1);
        $tr.addClass(rc);
        tb.append($tr);
        if (r.length == 4) {
            // Checkpoint <id, user, timestamp, comment>
            txt = r[2];
            if (r[1])
                txt += "[" + r[1] + "]";
            txt += ": " + r[3];
            var $cp = add_cell($tr, txt);
            $cp.attr("colspan", "6");
            $cp.addClass("checkpoint");
            $cp.corner();
        } else {
            // Event
            add_cells($tr, ["<A HREF='" + r[0] + "/'>" + r[0] + "</A>",
                            r[1], r[2],
                            {N:"New",A:"Active",S:"Archived",F:"Failed"}[r[3]],
                            r[4], r[5]]);
        }
        n += 1;
    });
    // Set up pager
    $("#pager").pager({pagenumber:data["page"]+1,pagecount:data["pages"],buttonClickCallback: pager_click});
    $("#events_count").text(data["count"]);
    $("#cover").hide();
    // Enable row hover
    $("#events_table TR").hover(
        function() {
            $(this).addClass("ui-state-highlight");
        },
        function() {
            $(this).removeClass("ui-state-highlight");
        }
    );    
}

var timeout_submit;

function update_data() {
    $("#form").submit();
    if(timeout_submit) {
        window.clearTimeout(timeout_submit);
    }
    timeout_submit=window.setTimeout(update_data,60000);
}

function change_status(obj,event_id,status) {
    show_cover();
    $(obj).closest('tr').find('td').andSelf().fadeTo('normal', 0);
    $.ajax({
        url     : "/fm/event/"+event_id+"/"+status+"/",
        success : update_data
    });
    return false;
}

function toggle_panel() {
    var fp=$("#form_panel");
    fp.toggle();
    if(fp.is(":hidden")) {
        $("#toggle_panel_link").text("Show Filter");
    } else {
        $("#toggle_panel_link").text("Hide Filter");
    }
    return false;
}

function show_cover() {
    var t=$("#events_table");
    if ($("#cover").is(':hidden')) {
        $("#cover").css({
            width: t.width(),
            height: t.height(),
            background: "#cccccc",
            position: "absolute",
            top: t.position().top,
            left: t.position().left,
            opacity: 0.5
        }).show();
    }
}

function pager_click(number) {
    $("#id_page").val(number);
    update_data();
}

