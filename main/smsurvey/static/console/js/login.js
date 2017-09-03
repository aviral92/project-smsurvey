$(document).ready(function() {

    $("#btn_login").click(function(){
        var to_send = {
            "username": $("#username").value,
            "password": $("#password").value
        };

       $.post(
           "http://project-smsurvey-lb-1432717712.us-east-1.elb.amazonaws.com/console/login",
           to_send,
           function(data, status, xhr) {
               if (status === 'success') {
                   Cookies.set('session_id', data['session_id'], {expires: 7});
                   Cookies.set('username', $('#username').value, {expires: 7});
                   window.location.href="http://project-smsurvey-lb-1432717712.us-east-1.elb.amazonaws.com/console"
               } else {
                   alert(data['message']);
               }
           },
           "json"
       );
    });

});