/* Global variables */
var support_html5 = true;

/* 
 * Run on page load
 */
$(function () {
    
    // Add date picker to date fields
    //$(".datefield").each(function() {
    //    $(this).datetimepicker();
    //});
    
    // Check browser for HTML5 support of:
    // (1) getUserMedia() API for capturing raw audio
    // (2) FormData used to send raw audio stream back to server
    support_getUserMedia = navigator.getUserMedia !== undefined || 
                           navigator.webkitGetUserMedia !== undefined || 
                           navigator.mozGetUserMedia !== undefined;
    support_FormData = window.FormData !== undefined;
    if (!support_getUserMedia || !support_FormData) {
        // Notify the user to switch browsers
        support_html5 = false;
        $(".support_html5").each(function() {
            $(this).removeClass("invisible");
        });
    }
});

$(document).ajaxSend(function(event, xhr, settings) {
    function getCookie(name) {
        var cookieValue = null;
        if (document.cookie && document.cookie != '') {
            var cookies = document.cookie.split(';');
            for (var i = 0; i < cookies.length; i++) {
                var cookie = jQuery.trim(cookies[i]);
                // Does this cookie string begin with the name we want?
                if (cookie.substring(0, name.length + 1) == (name + '=')) {
                    cookieValue = decodeURIComponent(cookie.substring(name.length + 1));
                    break;
                }
            }
        }
        return cookieValue;
    }
    function sameOrigin(url) {
        // url could be relative or scheme relative or absolute
        var host = document.location.host; // host + port
        var protocol = document.location.protocol;
        var sr_origin = '//' + host;
        var origin = protocol + sr_origin;
        // Allow absolute or scheme relative URLs to same origin
        return (url == origin || url.slice(0, origin.length + 1) == origin + '/') ||
            (url == sr_origin || url.slice(0, sr_origin.length + 1) == sr_origin + '/') ||
            // or any other URL that isn't scheme relative or absolute i.e relative.
            !(/^(\/\/|http:|https:).*/.test(url));
    }
    function safeMethod(method) {
        return (/^(GET|HEAD|OPTIONS|TRACE)$/.test(method));
    }

    if (!safeMethod(settings.type) && sameOrigin(settings.url)) {
        xhr.setRequestHeader("X-CSRFToken", getCookie('csrftoken'));
    }
});


/* Use in tasks where the task instance has to be hidden while the user 
 * is responding (e.g., hiding the story while the user attempts to 
 * re-tell it in their own words) 
 */
function hideDisplay(btn) {
    record_btn = $(btn).closest("li").find("#record-btn");
    $(btn).closest("li").html("Click the \"Start recording\" button below to begin recording. Tell the story in your own words, as you remember it. Try to speak for at least a minute. When done, click the \"Stop recording\" button.<p>" + record_btn.html() + "</p>");
}
