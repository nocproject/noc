function show_result(data) {
    var tb=$("#alarms_table TBODY");
    tb.empty();
    $.each(data["alarms"],function(i,r){
        var $tr=$(document.createElement("tr"));
        $tr.addClass(r[0]);
        tb.append($tr);
        $.each(r, function(j,d) {
            if(j>0) {
                var $td=$(document.createElement("td"));
                $tr.append($td);
                if(j==1) {
                    alarm_id=d;
                    $td.html("<A HREF='"+d+"/'>"+d+"</A>"); // Link to alarm
                } else if (j==5) {
                    status=d;
                    $td.text({A:"Active", C:"Cleared"}[status]);
                } else
                    $td.text(d);
            }
        });
        var $td=$(document.createElement("td"));
        $tr.append($td);
        var td_link="";
        $td.html(td_link);
    });
    // Set up pager
    $("#pager").pager({pagenumber:data["page"]+1,pagecount:data["pages"],buttonClickCallback: pager_click});
    $("#alarms_count").text(data["count"]);
    $("#cover").hide();
    // Enable row hover
    $("#alarms_table TR").hover(
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

function change_status(obj,alarm_id,status) {
    show_cover();
    $(obj).closest('tr').find('td').andSelf().fadeTo('normal', 0);
    $.ajax({
        url     : "/fm/alarm/"+alarm_id+"/"+status+"/",
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
    var t=$("#alarms_table");
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

