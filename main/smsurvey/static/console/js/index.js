var permissions_lookup = [
    ["", "", "READ PARTICIPANT", "WRITE PARTICIPANT", "READ/WRITE PARTICIPANT"],
    ["", "", "READ ENROLLMENT", "WRITE ENROLLMENT", "READ/WRITE ENROLLMENT"],
    ["", "", "READ PROTOCOL", "WRITE PROTOCOL", "READ/WRITE PROTOCOL"],
    ["", "", "READ QUESTION", "WRITE QUESTION", "READ/WRITE QUESTION"],
    ["", "", "READ RESPONSE", "WRITE RESPONSE", "READ/WRITE RESPONSE"],
    ["", "", "READ NOTE", "WRITE NOTE", "READ/WRITE NOTE"],
    ["", "", "READ SURVEY", "WRITE SURVEY", "READ/WRITE SURVEY"],
    ["", "", "READ TASK", "WRITE TASK", "READ/WRITE TASK"],
    ["", "", "READ PLUGIN", "WRITE PLUGIN", "READ/WRITE PLUGIN"],
    ["", "", "READ OWNER", "WRITE OWNER", "READ/WRITE OWNER"]
];

$(document).ready(function () {

    if (typeof Cookies.get('session_id') === 'undefined' || typeof Cookies.get('username') === 'undefined') {
        window.location.href = "http://project-smsurvey-lb-1432717712.us-east-1.elb.amazonaws.com/login.html"
    } else {
        var to_send = {
            "session_id": Cookies.get('session_id'),
            "username": Cookies.get('username')
        };

        $.ajax({
            url: "http://project-smsurvey-lb-1432717712.us-east-1.elb.amazonaws.com/console/check_login",
            type: "POST",
            data: JSON.stringify(to_send),
            contentType: "application/json; charset=utf-8",
            dataType: "json",
            error: function (jqxhr) {
                alert(jqxhr["responseJSON"]["reason"]);
                Cookies.remove("session_id");
                Cookies.remove("username");
                window.location.href = "http://project-smsurvey-lb-1432717712.us-east-1.elb.amazonaws.com/login.html"
            }
        });
    }


    if (typeof Cookies.get('session_id') !== 'undefined') {

        to_send = {
            "session_id": Cookies.get("session_id")
        };

        $.ajax({
            url: "http://project-smsurvey-lb-1432717712.us-east-1.elb.amazonaws.com/console/plugins",
            type: "GET",
            data: to_send,
            dataType: "json",
            success: function (data) {

                var plugins = data["plugins"];

                $.each(plugins, function (index, plugin) {

                    var html = "<li><a href='#' onclick='plugin_onclick(" + JSON.stringify(plugin) + ")'><i class='fa " + plugin["icon"] +
                        " fa-fw'></i> " + plugin["name"] + "</a></li>";

                    $('#side-menu').prepend(html);
                });
            },
            error: function (jqxhr) {
                alert(jqxhr["responseJSON"]["reason"]);
            }
        });
    }

    $('#a_home').click(function () {
        $("#page-wrapper-plugin").hide();
        $("#page-wrapper-manage-plugins").hide();
        $("#page-wrapper-add-plugin").hide();
        $("#page-wrapper-home").show();

        $("#a_home").html("<i class=\"fa fa-desktop fa-fw \"></i> Console")
    });

    $('#a_logout').click(function () {
        var to_send = {
            "session_id": Cookies.get('session_id')
        };

        Cookies.remove("session_id");
        Cookies.remove("username");

        $.ajax({
            url: "http://project-smsurvey-lb-1432717712.us-east-1.elb.amazonaws.com/console/logout",
            type: "POST",
            data: JSON.stringify(to_send),
            contentType: "application/json; charset=utf-8"
        });

        window.location.href = "http://project-smsurvey-lb-1432717712.us-east-1.elb.amazonaws.com/login.html"

    });

    $('#a_manage_plugins').click(function () {
        $("#page-wrapper-home").hide();
        $("#page-wrapper-plugin").hide();
        $("#page-wrapper-add-plugin").hide();

        $("#a_home").html("<i class=\"fa fa-desktop fa-fw \"></i> Console -> <i class=\"fa fa-cubes fa-fw \"></i> Manage Plugins");

        var to_send = {
            "session_id": Cookies.get("session_id")
        };

        $.ajax({
            url: "http://project-smsurvey-lb-1432717712.us-east-1.elb.amazonaws.com/console/plugins",
            type: "GET",
            data: to_send,
            dataType: "json",
            success: function (data) {

                var plugins = data["plugins"];

                var html = "";

                $.each(plugins, function (index, plugin) {
                    html += "<tr><td>" + plugin['id'] + "</td>";
                    html += "<td>" + plugin['name'] + "</td>";
                    html += "<td><button class='btn btn-info btn-xs' onclick='get_permissions(true, " + JSON.stringify(plugin) + ", alert)'>View Permissions</button></td>";
                    html += "<td><button class='btn btn-danger btn-xs' onclick='remove_plugin(" + JSON.stringify(plugin) + ")'>Remove Plugin</button></td></tr>";
                });

                $("#tbody_plugins").html(html);
            },
            error: function (jqxhr) {
                alert(jqxhr["responseJSON"]["reason"]);
            }
        });

        $("#page-wrapper-manage-plugins").show();
    });

    $("#btn_new_plugin").click(function () {
        $("#page-wrapper-plugin").hide();
        $("#page-wrapper-manage-plugins").hide();
        $("#page-wrapper-home").hide();
        $("#page-wrapper-add-plugin").show();

        $("#a_home").html("<i class=\"fa fa-desktop fa-fw \"></i> Console -> <i class=\"fa fa-cubes fa-fw \"></i> Manage Plugins -> <i class=\"fa fa-cube fa-fw \"></i> Add New Plugin")
    });

    $("#btn_cancel_add").click(function () {
        $("#page-wrapper-home").hide();
        $("#page-wrapper-plugin").hide();
        $("#page-wrapper-add-plugin").hide();
        $("#page-wrapper-manage-plugins").show();
        $("#a_home").html("<i class=\"fa fa-desktop fa-fw \"></i> Console -> <i class=\"fa fa-cubes fa-fw \"></i> Manage Plugins");
    });

    $("#btn_add_plugin").click(function () {
        var plugin_url = $("#input_plugin_url").val();
        get_permissions(false, plugin_url, confirm_permissions)
    });
});

function remove_plugin(plugin) {
    if (confirm("Are you sure? Removing a plugin without properly disassociating everything can have unintended consequences")) {
        var to_send = {
            "session_id": Cookies.get("session_id"),
            "plugin_id": plugin["id"]
        };

        $.ajax({
            url: "http://project-smsurvey-lb-1432717712.us-east-1.elb.amazonaws.com/console/plugins",
            type: "DELETE",
            data: to_send,
            dataType: "json",
            success: function () {
                location.reload()
            },
            error: function (jqxhr) {
                alert(JSON.stringify(jqxhr));
            }
        });
    }
}

function plugin_onclick(plugin) {
    $("#page-wrapper-home").hide();
    $("#page-wrapper-manage-plugins").hide();
    $("#page-wrapper-plugin").attr("src", plugin["url"] + '/config').show();
    $("#page-wrapper-add-plugin").hide();
    $("#a_home").html("<i class=\"fa fa-desktop fa-fw \"></i> Console -> <i class=\"fa " + plugin["icon"] + " fa-fw \"></i>" + plugin["name"]);
}

function get_permissions(registered, plugin, callback) {

    if (registered) {
        plugin = plugin["id"]
    }

    $.ajax({
        url: "http://project-smsurvey-lb-1432717712.us-east-1.elb.amazonaws.com/console/plugins/" + plugin + "/permissions",
        type: "GET",
        dataType: "json",
        success: function (data) {
            var permissions = data["permissions"].split('').map(Number);

            var message = "";

            $.each(permissions, function (index, permission) {
                if (permission !== 1) {
                    message += index + " - " + permissions_lookup[index][permission] + "\n";
                }

            });

            return callback(message);
        },
        fail: function (message) {
            alert(JSON.stringify(message));
        }
    });
}

function confirm_permissions(message) {

    var plugin_url = $("#input_plugin_url").val();

    if (confirm(message)) {
        var to_send = {
                "session_id": Cookies.get('session_id'),
                "plugin_url": plugin_url
            };

            $.ajax({
                url: "http://project-smsurvey-lb-1432717712.us-east-1.elb.amazonaws.com/console/plugins",
                type: "POST",
                data: JSON.stringify(to_send),
                contentType: "application/json; charset=utf-8",
                dataType: "json",
                success: function() {
                    location.reload()
                },
                error: function (message) {
                    alert(JSON.stringify(message));
                }
            });
    }
}