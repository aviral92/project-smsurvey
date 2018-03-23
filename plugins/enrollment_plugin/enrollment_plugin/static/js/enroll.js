function addParticipant(enrollment_id) {
    var plugin_id = $("#sel_plugin").find(":selected").val();
    var plugin_scratch = $("#tb_scratch").val();
    var plugin_name = $("#tb_name").val();

    var to_send = {
        "enrollment_id": enrollment_id,
        "plugin_id": plugin_id,
        "plugin_name": plugin_name,
        "plugin_scratch": plugin_scratch
    };

    $.ajax(
        {
            url: "/enroller/",
            method: "POST",
            data: to_send,
            success: function () {
                alert("Participant saved");
                location.reload();
            },
            fail: function () {
                alert("Error occurred adding participant");
            }
        }
    );
}
