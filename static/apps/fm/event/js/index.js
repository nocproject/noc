function show_result(data) {
    var tb=$("#events_table TBODY");
    tb.empty();
    $.each(data["events"],function(i,r){
        var event_id,status;
        var $tr=$(document.createElement("tr"));
        $tr.addClass(r[0]);
        tb.append($tr);
        $.each(r, function(j,d) {
            if(j>0) {
                var $td=$(document.createElement("td"));
                $tr.append($td);
                if(j==1) {
                    event_id=d;
                    $td.html("<A HREF='"+d+"/'>"+d+"</A>"); // Link to event
                } else if (j==4) {
                    status=d;
                    $td.text({U:"Unclassified",A:"Active",C:"Closed"}[status]);
                } else {
                    $td.text(d);
                }
            }
        });
        var $td=$(document.createElement("td"));
        $tr.append($td);
        var td_link="";
        if(status=="C") {
            td_link+="<a href='#' onclick='change_status(this,"+event_id+",\"open\"); return false;'>[Open]</a>";
        } else if (status=="A") {
            td_link+="<a href='#' onclick='change_status(this,"+event_id+",\"close\"); return false;'>[Close]</a>";
        }
        if(td_link) {
            td_link+="<br/><a href='#' onclick='change_status(this,"+event_id+",\"reclassify\"); return false;'>[Reclassify]</a>";
        }
        $td.html(td_link);
    });
    // Set up pager
    $("#pager").pager({pagenumber:data["page"]+1,pagecount:data["pages"],buttonClickCallback: pager_click});
    $("#events_count").text(data["count"]);
    $("#cover").hide();
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

