var number_of_runtimes = 1;
var number_of_dates = 1;

$(document).ready(function() {
    $("#btn_vt_back").click(function() {
        $("#config_view_times").hide();
        $("#config_home").show();
    });

    $("#btn_w_back").click(function() {
        $("#config_wizard").hide();
        $("#config_home").show();
    });

    $("#btn_save").click(function() {
       if (confirm("Are you sure you want to save?")) {
           var time_rule = get_time_rule_from_ui();

           var to_send = {
               "plugin_id": $("#plugin_id"),
               "name": $("#tb_name").val(),
               "protocol": $("#sel_protocol").find(":selected").val(),
               "time_rule": time_rule,
               "enable_notes": $("#cb_notes").is(":checked")
           };

           var timeout_val = $("#tb_timeout").val();
           if (timeout_val !== null && timeout_val.trim() !== "") {
               to_send["timeout"] = timeout_val;
               to_send["enable_warnings"] = $("#cb_warnings").is(":checked");
           }

           $.ajax(
               {
                   url: "/task/",
                   method: "POST",
                   data: to_send,
                   success: function() {
                       // noinspection SillyAssignmentJS
                       document.location.href = document.location.href;
                   },
                   fail: function() {
                       alert("Error occurred on saving of surveys");
                   }
               }
           );
       }
    });

    $("#cb_repeats").change(function(){
        if ($(this).is(":checked")) {
            $("#repeats").show();
            $("#sel_repeats").val('daily');
            $("#repeats_daily").show();
            $("#dp_until").show();
        } else {
            $("#repeats_daily").hide();
            $("#repeats_weekly").hide();
            $("#repeats_monthly_date").hide();
            $("#repeats_monthly_day").hide();
            $("#dp_until").hide();
        }
    });

    $("#sel_repeats").change(function() {
        var value = $("#sel_repeats").find(":selected").val();

        if (value === 'daily') {
            $("#repeats_daily").show();
            $("#repeats_weekly").hide();
            $("#repeats_monthly_date").hide();
            $("#repeats_monthly_day").hide();
        } else if (value === 'weekly') {
            $("#repeats_daily").hide();
            $("#repeats_weekly").show();
            $("#repeats_monthly_date").hide();
            $("#repeats_monthly_day").hide();
        } else if (value === 'monthly_date') {
            $("#repeats_daily").hide();
            $("#repeats_weekly").hide();
            $("#repeats_monthly_date").show();
            $("#repeats_monthly_day").hide();
        } else if (value === 'monthly_day') {
            $("#repeats_daily").hide();
            $("#repeats_weekly").hide();
            $("#repeats_monthly_date").hide();
            $("#repeats_monthly_day").show();
        }
    });

    $("#btn_new_task").click(function(){
        $("#config_home").hide();
        number_of_runtimes = 1;
        number_of_dates = 1;
        $("#config_wizard").show();
    });

    $("#btn_add_runtime").click(function() {
       number_of_runtimes += 1;
       var html = '<label for="tp_runtime' + number_of_runtimes + '">Runtime: </label><input id="tp_runtime' + number_of_runtimes + '" type="time" class="form-control">';
       $("#runtimes").append(html)
    });

    $("#btn_add_date").click(function() {
       number_of_dates += 1;
       var html = '<label for="tb_date' + number_of_dates + '">Date of month: </label><input id="tb_date' + number_of_dates + '" class="form-control" size="2">';
       $("#rundates").append(html)
    });
});

function get_time_rule_from_ui() {

    var time_rule = {};
    time_rule["run_date"] = $("#dp_run_date").val;
    time_rule["run_times"] = get_run_times();
    time_rule["until"] = $("#dp_until").val;

    if ($("#cb_repeats").is(":checked")) {
        var selected_rule = $('#sel_repeats').find(":selected").val();

        if (selected_rule === 'daily') {
            time_rule["type"] = 'daily';
            time_rule["params"] = get_daily_params();
        } else if (selected_rule === 'weekly') {
            time_rule["type"] = 'weekly';
            time_rule["params"] = get_weekly_params();
        } else if (selected_rule === 'monthly_date') {
            time_rule["type"] = 'monthly-date';
            time_rule["params"] = get_monthly_date_params();
        } else if (selected_rule === 'monthly-day') {
            time_rule["type"] = 'monthly_day';
            time_rule["params"] = get_monthly_day_params();
        }
    } else {
        time_rule["type"] = "no-repeat";
        time_rule["params"] = null
    }

    return time_rule;
}

function get_daily_params() {
    var params = {};
    params["every"] = $("#tb_every_daily").val();
    return params;
}

function get_weekly_params() {
    var params = {};
    params["every"] = $("#tb_every_weekly").val();

    var days = [];

    if ($("#cb_w_mon").is(":checked")) {
        days.append(0);
    }

    if ($("#cb_w_tue").is(":checked")) {
        days.append(1);
    }

    if ($("#cb_w_wed").is(":checked")) {
        days.append(2);
    }

    if ($("#cb_w_thu").is(":checked")) {
        days.append(3);
    }

    if ($("#cb_w_fri").is(":checked")) {
        days.append(4);
    }

    if ($("#cb_w_sat").is(":checked")) {
        days.append(5);
    }

    if ($("#cb_w_sun").is(":checked")) {
        days.append(6);
    }

    params["days"] = days;

    return params;
}

function get_monthly_date_params() {
    var params = {};
    params["every"] = $("#tb_every_monthly_date").val();

    var dates = [];

    for (var i = 1; i <= number_of_dates; i++) {
        dates.append(parseInt($("#tb_date" + i).val()));
    }

    params["dates"] = dates;

    return params;
}

function get_monthly_day_params() {
    var params = {};
    params["every"] = $("#tb_every_monthly_day").val();

    var param1 = $('#sel_monthly_day').find(":selected").val();

    var days = [];

    if ($("#cb_m_mon").is(":checked")) {
        days.append(0);
    }

    if ($("#cb_m_tue").is(":checked")) {
        days.append(1);
    }

    if ($("#cb_m_wed").is(":checked")) {
        days.append(2);
    }

    if ($("#cb_m_thu").is(":checked")) {
        days.append(3);
    }

    if ($("#cb_m_fri").is(":checked")) {
        days.append(4);
    }

    if ($("#cb_m_sat").is(":checked")) {
        days.append(5);
    }

    if ($("#cb_m_sun").is(":checked")) {
        days.append(6);
    }

    params["param1"] = param1;
    params["days"] = days;

    return params;
}

function get_run_times() {

    var runtimes = [];

    for (var i = 1; i <= number_of_runtimes; i++) {
        runtimes.append($("#tp_runtime" + i).val());
    }

    return runtimes;
}

function remove_task(task_id) {

    var to_send = {
        "plugin_id": $("#plugin_id").html(),
        "id": task_id
    };

    if (confirm("Removing task will mean it will not run again in the future")) {
        $.ajax({
            url: "/task",
            data: to_send,
            method: "DELETE",
            success: function() {
                // noinspection SillyAssignmentJS
                document.location.href = document.location.href;
            },
            fail: function() {
                alert("Error occurred on removal of task");
            }
        });
    }
}