/* Global variables */
var support_html5 = true;
var timer_rig = false;

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
        $(".unsupported_html5").each(function() {
            $(this).addClass("invisible");
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


/* Use to update timer in timed tasks.
 * Update display every second.
 */
function startTimerRig(start_btn, instance_id) {
    timer_rig = setInterval(function(){ 
        updateTimerDisplay(start_btn, instance_id); 
    }, 1000);
    
    // Disable the Start button, and enable the response field
    $(start_btn).prop('disabled', true);
    $(start_btn).parent().find("[name=response]").each(function() {
        $(this).prop('disabled', false);
    });
    $(start_btn).text("Started timer...");
}

/* Pad a number 'n' with character 'z' to a given 'width'.
 * If character 'z' is empty, pad with '0'.
 */
function pad(n, width, z) {
    z = z || '0';
    n = n + '';
    return n.length >= width ? n : new Array(width - n.length + 1).join(z) + n;
}

function updateTimerDisplay(start_btn, instance_id) {
    var new_value = parseInt($("#timer_val_" + instance_id).val()) - 1;
    $("#timer_val_" + instance_id).val(new_value);
    var display_min = Math.floor(new_value / 60);
    var display_sec = new_value - display_min * 60;
    
    $("#timer_display_" + instance_id).html(pad(display_min,2,'0') + ":" + pad(display_sec,2,'0'));
    
    if (new_value <= 0) {
        stopTimerRig();
        
        // Disable the response field
        $(start_btn).parent().find("[name=response]").each(function() {
            $(this).prop('disabled', true);
        });
    }
}

function stopTimerRig() {
    if (timer_rig) {
        window.clearInterval(timer_rig);
    }
}