$(document).ready(function() {

    $("#btn_login").click(function(){
        var to_send = {
            "username": $("#username").val(),
            "password": $("#password").val()
        };

       $.ajax({
           url: "http://project-smsurvey-lb-1432717712.us-east-1.elb.amazonaws.com/console/login",
           type: "POST",
           data: JSON.stringify(to_send),
           contentType: "application/json; charset=utf-8",
           dataType: "json",
           success: function(data, status){
               if (status === 'success') {
                   Cookies.set('session_id', data['session_id'], {expires: 7});
                   Cookies.set('username', data['username'], {expires: 7});
                   window.location.href="http://project-smsurvey-lb-1432717712.us-east-1.elb.amazonaws.com/"
               } else {
                   alert(data['message']);
               }
            },
           error: function(jqxhr) {
               alert(jqxhr["responseJSON"]["reason"]);
           }
       });
    });

});