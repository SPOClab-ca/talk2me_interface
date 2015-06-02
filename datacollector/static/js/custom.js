/* Global variables */
var support_html5 = true;
var timer_rig = false;
var page_start_time = false;
var website_id = 'talk2me';

/* 
 * Run on page load
 */
$(document).ready(function () {
    
    // Add date picker to date fields. The subject has to be at least 18 years old.
    $(".datefield").each(function() {
        $(this).datepicker({ 
            dateFormat: "yy-mm-dd",
            changeMonth: true,
            changeYear: true,
            minDate: "-150Y",
            maxDate: "-18Y",
            yearRange: "-150:-18"
        });
    });
    
    // Add "scale" slider (jquery UI element for selecting a value on a scale)
    $("[class^='scale_']").each(function() {
        var regex_scale = /scale[_]([0-9]+)[_]([0-9]+)/i;
        var matches = regex_scale.exec($(this).attr("class"));
        if (matches && matches.length >= 3) {
            var slider_min = parseInt(matches[1]);
            var slider_max = parseInt(matches[2]);
            
            var default_val = median(range(slider_min, slider_max));
            // Math.round((slider_max-slider_min+1)/2);
            $(this).slider({
                min: slider_min,
                max: slider_max,
                value: default_val,
                range: "min",
                step: 0.5,
                slide: function(event, ui) {
                    $(this).siblings(".scale_display").html(ui.value);
                    $(this).siblings("[name=response]").val(ui.value);
                }
            });
            
            // Update the label with the default value for the slider
            $(this).siblings(".scale_display").html(default_val);
            $(this).siblings("[name=response]").val(default_val);
        }
    });
    
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
    
    // Measure time spent on page
    page_start_time = new Date().getTime();
});


/*
 * Run when window is closed/left
 */
$(window).unload(function() {
    
    var session_task_id = $("#session_task_id").val();
    if (session_task_id !== undefined) {
        // By default, store the time elapsed in seconds in db
        var page_time_elapsed = Math.round((new Date().getTime() - page_start_time) / 1000);
        
        $.ajax({
            async: false,
            type: 'POST',
            url: '/' + website_id + '/pagetime',
            data: {'timeelapsed': page_time_elapsed, 'sessiontaskid': session_task_id },
            dataType: 'json',
            error: function(jqXHR, textStatus, errorThrown) { 
                console.log('Page time error: ' + textStatus + ", " + errorThrown);
            },
            success: function(data, textStatus, jqXHR) {
                console.log('Sent page time!');
            }
        });
    }
    
});

function range(start, end) {
    var foo = [];
    for (var i = start; i <= end; i++) {
        foo.push(i);
    }
    return foo;
}

function median(values) {
    values.sort( function(a,b) {return a - b;} );
 
    var half = Math.floor(values.length/2);
 
    if(values.length % 2)
        return values[half];
    else
        return (values[half-1] + values[half]) / 2.0;
}

function formSubmit(submit_btn) {
    $(submit_btn).closest("form").submit();
}

function formSubmitAjax(submit_btn) {
    
    // As soon as the submit button is pressed, (1) disable the button to prevent resubmits,
    // (2) show an ajax indicator to the user to indicate that their data is being sent to 
    // the server, and (3) clear the errors display div.
    $(submit_btn).prop("disabled", true);
    $("#ajax_loader_msg").html("Submitting data, please wait...");
    $("#ajax_loader").removeClass("invisible");
    $("#form_errors").addClass("invisible");
    
    var post_params = "";
    var the_form = $(submit_btn).closest("form");
    $(the_form).find(".form-field").each(function() {
        // If the form element is a radio element, then only add it to params if it is the selected one
        if (!($(this).is("input[type='radio']")) || $(this).is(":checked") == true) {
            if (post_params) {
                post_params += "&";
            }
            post_params += $(this).attr('name') + "=" + encodeURIComponent($(this).val());
        }
    });
    
    $.ajax({
        async: true,
        type: 'POST',
        url: $(the_form).attr("action"),
        data: post_params,
        dataType: 'json',
        error: function(jqXHR, textStatus, errorThrown) { 
            // (1) Re-enable submit button, (2) hide the ajax indicator
            $(submit_btn).prop("disabled", false);
            $("#ajax_loader").addClass("invisible");
            
            // (3) Display error message
            $("#form_errors").html("<strong>The form could not be submitted.</strong> Error 601: " + textStatus + " - " + errorThrown + ". Please contact the website administrators to report this error.").removeClass("invisible");
            $("body").scrollTop(0);
        },
        success: function(data, textStatus, jqXHR) {
            // (1) Re-enable submit button, (2) hide the ajax indicator
            $(submit_btn).prop("disabled", false);
            $("#ajax_loader").addClass("invisible");
            
            response_text = jqXHR.responseText;
            page_response = JSON && JSON.parse(response_text) || $.parseJSON(response_text);
            if (page_response['status'] == 'success') {
                window.location.reload();
            } else {
                var errors = page_response['error'];
                if (errors.length > 0) {
                    var display_errors = "<strong>The form could not be submitted. Please correct the following error" + (errors.length > 1 ? "s" : "") + ":</strong><ul>";
                    for (i = 0; i < errors.length; i++) {
                        display_errors += "<li>" + errors[i].msg + "</li>";
                    }
                    display_errors += "</ul>";
                    
                    // (3) Display error message
                    $("#form_errors").html(display_errors).removeClass("invisible");
                    $("body").scrollTop(0);
                }
            }
        }
    });
}

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
    var container = $(btn).closest("li");
    if ($(btn).closest("li").length == 0) {
        container = $(btn).closest("div");
    }
    var instance_id = $(container).find("[name=instanceid]").val();
    var record_btn = $(container).find("#record-btn_" + instance_id);
    $(container).html("Click the \"Start recording\" button below to begin recording. Tell the story in your own words, as you remember it. Try to speak for at least a minute. When done, click the \"Stop recording\" button.<p class='space-top-small space-bottom-small'>" + record_btn.html() + "</p>");
}


/* Use to update timer in timed tasks.
 * Update display every second.
 */
function startTimerRig(start_btn, instance_id) {
    timer_rig = setInterval(function(){ 
        updateTimerDisplay(start_btn, instance_id); 
    }, 1000);
    
    // (1) disable the Submit button, 
    // (2) disable the Start button, 
    // (3) enable the response field
    $("#submit_btn").prop("disabled", true);
    $(start_btn).prop('disabled', true);
    $(start_btn).parent().find("[name=response]").each(function() {
        $(this).prop('readonly', false).removeClass("input-disabled");
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
        
        // (1) disable the response field
        // (2) enable the submit button
        // NB: DO NOT re-enable the Start button, since only one response will be accepted
        $(start_btn).parent().find("[name=response]").each(function() {
            $(this).prop('readonly', true).addClass("input-disabled");
        });
        $("#submit_btn").prop("disabled", false);
    }
}

function stopTimerRig() {
    if (timer_rig) {
        window.clearInterval(timer_rig);
    }
}

/* When a consent checkbox has additional details (e.g., email address prompt), only show them when the checkbox is selected */
function showCbDetails(cb) {
    var cb_id = $(cb).attr("id");
    var patt = /cb_([a-zA-Z_]+)/;
    if (patt.test(cb_id)) {
        var cb_details_id = "detail_" + patt.exec(cb_id)[1];
        if ($(cb).is(":checked")) {
            $("#" + cb_details_id).removeClass("invisible");
        } else {
            $("#" + cb_details_id).addClass("invisible");
        }
    }
}

function demographicsAddLanguage(link) {
    if ($("#language_selection").length > 0) {
        var tbl = $("#language_selection")[0];
        
        // Clone last row, and update all IDs and field names, reset select
        var tr_last = $(tbl).find("tr:last");
        var tr_clone = $(tr_last).clone();
        $(tr_clone).find("input[type=radio]").each(function() {
            $(this).prop("checked",false);
            var radio_name = $(this).attr("name");
            var patt_name = /(other_fluency_)([0-9]+)/;
            if (patt_name.test(radio_name)) {
                var prev_name = patt_name.exec(radio_name)[1];
                var prev_id = patt_name.exec(radio_name)[2];
                var new_id = parseInt(prev_id) + 1;
                $(this).attr("name", prev_name + new_id.toString());
            }
        });
        $(tr_clone).find("select").prop("selectedIndex",0);
        
        // Insert the cloned row last in the table
        $(tr_last).after($(tr_clone));
    }
}
