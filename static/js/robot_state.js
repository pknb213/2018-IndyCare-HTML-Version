function update_robot_state(sn){
    $.ajax({
        type: "GET",
        url: "/robot/state/" + sn,
        dataType: 'json',
        success: (json)=>{
            //console.log(json);
            json = eval("("+ json + ")");
            $("#busy_li").empty();
            $("#ready_li").empty();
            $("#collision_li").empty();
            $("#error_li").empty();
            $("#program_state_li").empty();
            $("#emergency_li").empty();
            $("#report_connected_li").empty();
            $("#server_connected_li").empty();

            if (json['busy'] === 1)
                $("#busy_li").append("<img src='/static/img/active/icon_busy.svg' alt='icon_busy' /><span>BUSY</span>");
            else
                $("#busy_li").append("<img src='/static/img/inactive/icon_busy.svg' alt='icon_busy' /><span>BUSY</span>");
            if (json['ready'] === 1)
                $("#ready_li").append("<img src='/static/img/active/icon_ready.svg' alt='icon_busy' /><span>READY</span>");
            else
                $("#ready_li").append("<img src='/static/img/inactive/icon_ready.svg' alt='icon_busy' /><span>READY</span>");
            if (json['collision'] === 1)
                $("#collision_li").append("<img src='/static/img/active/icon_collision.svg' alt='icon_busy' /><span>COLLISION</span>");
            else
                $("#collision_li").append("<img src='/static/img/inactive/icon_collision.svg' alt='icon_busy' /><span>COLLISION</span>");
            if (json['error'] === 1)
                $("#error_li").append("<img src='/static/img/active/icon_error.svg' alt='icon_busy' /><span>ERROR</span>");
            else
                $("#error_li").append("<img src='/static/img/inactive/icon_error.svg' alt='icon_busy' /><span>ERROR</span>");
            if (json['program_state'] === 1)
                $("#program_state_li").append("<img src='/static/img/active/icon_state_play.svg' alt='icon_busy' /><span>PROGRAM STATE</span>");
            else if (json['program_state'] === 2)
                $("#program_state_li").append("<img src='/static/img/active/icon_state_pause.svg' alt='icon_busy' /><span>PROGRAM STATE</span>");
            else
                $("#program_state_li").append("<img src='/static/img/active/icon_state_stop.svg' alt='icon_busy' /><span>PROGRAM STATE</span>");
            if (json['emergency'] === 1)
                $("#emergency_li").append("<img src='/static/img/active/icon_energency.svg' alt='icon_busy' /><span>EMERGENCY</span>");
            else
                $("#emergency_li").append("<img src='/static/img/inactive/icon_energency.svg' alt='icon_busy' /><span>EMERGENCY</span>");
            if (json['is_server_connected'] === 1)
                $("#report_connected_li").append("<img src='/static/img/active/icon_server_connected.svg' alt='icon_busy' /><span>SERVER CONNECTED</span>");
            else
                $("#report_connected_li").append("<img src='/static/img/inactive/icon_server_connected.svg' alt='icon_busy' /><span>SERVER CONNECTED</span>");
            if (json['is_reporter_running'] === 1)
                $("#server_connected_li").append("<img src='/static/img/active/icon_report_connected.svg' alt='icon_busy' /><span>ROBOT CONNECTED</span>");
            else
                $("#server_connected_li").append("<img src='/static/img/inactive/icon_report_connected.svg' alt='icon_busy' /><span>ROBOT CONNECTED</span>");
        }
    });
}