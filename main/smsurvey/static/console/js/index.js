$(document).ready(function(){

   if (typeof Cookies.get('session_id') === 'undefined' || typeof Cookies.get('username') === 'undefined') {
       window.location.href="http://project-smsurvey-lb-1432717712.us-east-1.elb.amazonaws.com/console/login.html"
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
           error: function(jqxhr) {
               alert(jqxhr["responseJSON"]["reason"]);
               window.location.href="http://project-smsurvey-lb-1432717712.us-east-1.elb.amazonaws.com/console/login.html"
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
           success: function(data, status){
               $.each(plugins, function(index, plugin){
                   var onclick = '$("#page-wrapper-plugin").attr("src", "' + plugin["url"] + '/config"); ' +
                       '$("#page-wrapper-home").hide(); ' +
                       '$("#page-wrapper-plugin").show(); ' +
                       '$("#a_home").html("Console -> ' + plugin["name"] + '");';
                   var html = '<li><a href="#" onclick="' + onclick + '"><i class="fa ' + plugin["icon"] +
                       ' fa-fw></i> ' + plugin["name"] + '"</a></li>';

                   $('#side-menu').prepend(html);
               });
            },
           error: function(jqxhr) {
               alert(jqxhr["responseJSON"]["reason"]);
           }
       });
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

       $.ajax({
           url: "http://project-smsurvey-lb-1432717712.us-east-1.elb.amazonaws.com/console/logout",
           type: "POST",
           data: JSON.stringify(to_send),
           contentType: "application/json; charset=utf-8"
       });

       window.location.href="http://project-smsurvey-lb-1432717712.us-east-1.elb.amazonaws.com/login.html"

   });
});