$(document).ready(function(){

   if (typeof Cookies.get('session_id') === 'undefined' || typeof Cookies.get('username') === 'undefined') {
       window.location.href="http://project-smsurvey-lb-1432717712.us-east-1.elb.amazonaws.com/console/login"
   } else {
       var to_send = {
            "session_id": Cookies.get('session_id'),
            "username": Cookies.get('username')
        };

       $.post(
           "http://project-smsurvey-lb-1432717712.us-east-1.elb.amazonaws.com/console/check_login",
           to_send,
           function(data, status) {
               if (status !== 'success') {
                   window.location.href="http://project-smsurvey-lb-1432717712.us-east-1.elb.amazonaws.com/console/login"
               }
           },
           "json"
       );
   }


   if (typeof Cookies.get('session_id') !== 'undefined') {
        $.getJSON(
            "http://project-smsurvey-lb-1432717712.us-east-1.elb.amazonaws.com/console/plugins?session_id=" + Cookies.get("session_id"),
            function(plugins, status) {
                if (status === 'success') {
                    $.each(plugins, function(index, plugin){
                        var onclick = '$("#page-wrapper-plugin").attr("src", "' + plugin["url"] + '/config"); ' +
                            '$("#page-wrapper-home").hide(); ' +
                            '$("#page-wrapper-plugin").show(); ' +
                            '$("#a_home").html("Console -> ' + plugin["name"] + '");';
                        var html = '<li><a href="#" onclick="' + onclick + '"><i class="fa ' + plugin["icon"] +
                            ' fa-fw></i> ' + plugin["name"] + '"</a></li>';

                        $('#side-menu').prepend(html);
                       });
                }
            }
       );
   }

   $('#a_home').click(function() {
       $("#page-wrapper-plugin").hide();
       $("page-wrapper-home").show();

       $("#a_home").html("Console")
   });

   $('#a_logout').click(function() {
       var to_send = {
            "session_id": Cookies.get('session_id')
        };

       $.post(
           "http://project-smsurvey-lb-1432717712.us-east-1.elb.amazonaws.com/console/logout",
           to_send
       );

       window.location.href="http://project-smsurvey-lb-1432717712.us-east-1.elb.amazonaws.com/console/login"

   });
});