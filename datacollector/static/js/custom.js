/* Global variables */
var support_html5 = true;
var timer_rig = false;
var timer_rig_max = null;
var page_start_time = false;
var website_id = 'talk2me';
var default_dialog_width = 450;

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
                    setUnsavedChanges();
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
    
    // Make sure that any changes made to any form elements will trigger an "unsaved changes" dialog on page exit.
    // If the form elements are cleared (made blank), then reset the unsaved changes flag.
    // "keyup" ensures that changes are captured on input fields and textareas *before* they lose focus (e.g., type into
    // a textarea, then it gets disabled, and then click backspace without clicking away from textarea), while "change"
    // captures changes on radio, select, and checkbox fields.
    $(".form-field").keyup(function() { detectFieldChanges(this); })
                    .change(function() { detectFieldChanges(this); });
    
    // If the user is currently loading a session page, scroll to top to prevent
    // the browser from scrolling down when the next task is displayed on the same page.
    var session_task_id = $("#session_task_id").val();
    if (session_task_id !== undefined) {
        $(window).scrollTop(0);
        
        // If there are multiple audio recording buttons on the session page, disable all but the first.
        // (At any point in time there should only be one active audio recording button to prevent user 
        // from clicking all of them at the same time).
        var id_audio_buttons = "btn_recording_";
        if ($("[id^='" + id_audio_buttons + "']").length > 1) {
            var audio_buttons = $("[id^='" + id_audio_buttons + "']");
            for (i = 0; i < audio_buttons.length; i++) {
                if (i > 0) {
                    $(audio_buttons[i]).attr("disabled", "disabled");
                }
            }
        }
    }
    
    // Make all clickable table rows links
    $(".clickable-row").click(function() {
        window.document.location = $(this).data("href");
    });
    
    // Notifications
    $(".dropdown-toggle").click(function() {
        var toggle = $(this);
        // Send AJAX request to server to mark all notifications as 'dismissed' (viewed).
        $.ajax({
            async: true,
            type: 'POST',
            url: '/' + website_id + '/notify/dismiss/',
            data: {'target_notif': '' },
            dataType: 'json',
            error: function(jqXHR, textStatus, errorThrown) { 
                console.log('Unable to dismiss notifications: ' + textStatus + ", " + errorThrown);
            },
            success: function(data, textStatus, jqXHR) {
                // Update the UI to remove the red notification (the number of 'new' notifications).
                // Visibility: hidden preserves the space taken up by the label.
                $(toggle).siblings(".dropdown-label-new").css('visibility','hidden');
            }
        });
    });
    
    // If we're on the admin page, load the Google Charts API
    if ($("#chart_div").length > 0) {
        // Load the Visualization API and the piechart package.
        google.load('visualization', '1.0', {'packages':['corechart'],
                                             'callback': function() { drawChart(); } });
    }
    
    // Measure time spent on page
    page_start_time = new Date().getTime();
});

// Callback that creates and populates a data table,
// instantiates the pie chart, passes in the data and
// draws it.
function drawChart() {

    // Create the data table.
    var data = new google.visualization.DataTable();
    data.addColumn('string', 'Topping');
    data.addColumn('number', 'Slices');
    data.addRows([
      ['Mushrooms', 3],
      ['Onions', 1],
      ['Olives', 1],
      ['Zucchini', 1],
      ['Pepperoni', 2]
    ]);

    // Set chart options
    var options = {'title':'How Much Pizza I Ate Last Night',
                   'width':400,
                   'height':300};

    // Instantiate and draw our chart, passing in some options.
    var chart = new google.visualization.PieChart(document.getElementById('chart_div'));
    chart.draw(data, options);
}

/* Check for unsaved work before navigation away from page */
window.onbeforeunload = function (e) {
    var e = e || window.event;
    var msg = 'You have unsaved data that will be lost if you leave this page.';
    
    // If the user is currently on a session page and has entered in some unsaved data, 
    // ask them to confirm leaving the page.
    var session_task_id = $("#session_task_id").val();
    if (session_task_id !== undefined) {
        var unsaved_changes_id = "unsaved_changes";
        if ($("#" + unsaved_changes_id).length > 0) {
            if ($("#" + unsaved_changes_id).val() == "yes") {
                
                // For IE6-8 and Firefox prior to version 4
                if (e) {
                    e.returnValue = msg;
                }
                // For Chrome, Firefox, Safari, Opera (modern versions)
                return msg;
            }
        }
    }
};

/*
 * Run when window is closed/left
 */
$(window).unload(function() {
    
    // If the user is currently on a session page, record the time they spent on it
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


$.preload = function(array, fn_when_done) {
	var length = array.length,
	    document = window.document,
	    body = document.body,
	    isIE = 'fileSize' in document,
	    object;
	while (length--) {
		if (isIE) {
			new Image().src = array[length];
			continue;
		}
		object = document.createElement('object');
		object.data = array[length];
		object.width = object.height = 0;
		body.appendChild(object);
	}
    fn_when_done();
};

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

function formSubmit(submit_btn, ajax_msg) {
    preventResubmission(submit_btn, ajax_msg);
    $(submit_btn).closest("form").submit();
}

function formSubmitAjax(submit_btn, ajax_msg, success_fn) {
    
    // As soon as the submit button is pressed, (1) disable the button to prevent resubmits,
    // (2) show an ajax indicator to the user to indicate that their data is being sent to 
    // the server, and (3) clear the errors display div.
    $(submit_btn).prop("disabled", true);
    $(submit_btn).siblings(".ajax_loader").removeClass("invisible");
    $(submit_btn).siblings(".ajax_loader").children(".ajax_loader_msg").html(ajax_msg);
    $("#form_errors").addClass("invisible");
    $("#save_msg_container").addClass("invisible");
    
    var post_params = "";
    var the_form = $(submit_btn).closest("form");
    $(the_form).find(".form-field").each(function() {
        // If the form element is a radio element, then only add it to params if it is the selected one
        if ($(this).is("input[type='checkbox']")) {
            if ($(this).is(":checked") == true) {
                if (post_params) {
                    post_params += "&";
                }
                post_params += $(this).attr('name') + "=on";
            }
        }
        else if (!($(this).is("input[type='radio']")) || $(this).is(":checked") == true) {
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
            $(submit_btn).siblings(".ajax_loader").addClass("invisible");
            
            // (3) Display error message
            $("#form_errors").html("<strong>The form could not be submitted.</strong> Error 601: " + textStatus + " - " + errorThrown + ". Please contact the website administrators to report this error.").removeClass("invisible");
            $("body").scrollTop(0);
        },
        success: function(data, textStatus, jqXHR) {
            // (1) Re-enable submit button, (2) hide the ajax indicator
            $(submit_btn).prop("disabled", false);
            $(submit_btn).siblings(".ajax_loader").addClass("invisible");
            
            response_text = jqXHR.responseText;
            page_response = JSON && JSON.parse(response_text) || $.parseJSON(response_text);
            if (page_response['status'] == 'success') {
                // Now that the data have been saved on the server, reset the "unsaved changes" flag (if it exists)
                resetUnsavedChanges();
                
                success_fn(page_response);
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

/* Functions used as success functions after AJAX form submission 
 * "params" - the page response dictionary (returned from corresponding view)
 */
 
// Used on the Session page to refresh and display the next task
function reloadPage(params) {
    window.location.reload();
}

// Used on Account Settings page: display success message up top, and clear any password fields
function displayConfirmMsg(params) {
    $("#save_msg_container").html(params['save_msg']).removeClass("invisible");
    $("body").scrollTop(0);
    $(".pwd-field").val("");
    if (params['email_change'] == 'true') {
        $("#email_validation").html(params['email_confirm_display']);
    }
}

// Used on Account Settings page: after Withdrawal, the user is logged out - redirect to main page
function redirectToHome(params) {
    window.location.href = params['website_root'];
}
/* END FUNCTIONS USED AS SUCCESS FUNCTIONS AFTER AJAX FORM SUBMISSION */

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
    // (3) enable the response field, and bring focus to it
    $("#submit_btn").prop("disabled", true);
    $(start_btn).prop('disabled', true);
    $(start_btn).parent().find("[name=response]").each(function() {
        $(this).prop('readonly', false).removeClass("input-disabled").focus();
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

/*
 * If there is still no user input at the end of the timer, 
 * re-enable the timer button and keep submission disabled.
 */
function updateTimerDisplay(start_btn, instance_id) {
    var current_value = parseInt($("#timer_val_" + instance_id).val());
    if (timer_rig_max == null) {
        timer_rig_max = current_value;
    }
    var new_value = current_value - 1;
    $("#timer_val_" + instance_id).val(new_value);
    var display_min = Math.floor(new_value / 60);
    var display_sec = new_value - display_min * 60;
    
    $("#timer_display_" + instance_id).html(pad(display_min,2,'0') + ":" + pad(display_sec,2,'0'));
    
    if (new_value <= 0) {
        stopTimerRig();
        
        // (1) disable the response field
        $(start_btn).parent().find("[name=response]").each(function() {
            $(this).prop('readonly', true).addClass("input-disabled");
        });
        
        var unsaved_changes = $("#unsaved_changes").val();
        if (unsaved_changes != "") {
            // If the user provided a response, then:
            // (2) enable the submit button 
            $("#submit_btn").prop("disabled", false);
        } else {
            // Otherwise:
            // (3) re-enable the timer Start button to allow user to repeat the task
            // and reset the timer max
            $(start_btn).prop("disabled", false).text("Start");
            $("#timer_val_" + instance_id).val(timer_rig_max);
        }
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

// Used on Demographics page, to auto-select a language for which a fluency has been selected
// The radio button of the selected fluency is passed as argument "rb".
function selectCorrespondingLanguage(rb) {
    if ($(rb).is(":checked")) {
        $(rb).closest("tr").find("input[type=checkbox]").attr("checked", true);
    }
}

// This function creates a jQuery UI dialog widget, assuming the existence of 
// a #dialog-message div on the current page
function createDialog(title, body, width) {
    var dialog_id = "dialog-message";
    if ($("#" + dialog_id).length > 0) {
        $("#" + dialog_id).attr("title", title).html(body).dialog({
            modal: true,
            buttons: {
                OK: function() { closeDialog(this); }
            },
            width: width
        });
    }
}

function createDialogRedirect(title, body, width, redirectBtnTitle, redirectFn) {
    var dialog_id = "dialog-message";
    if ($("#" + dialog_id).length > 0) {
        
        $("#" + dialog_id).attr("title", title).html(body).dialog({
            closeOnEscape: false,
            modal: true,
            width: width,
            open: function(event, ui) { $(".ui-dialog-titlebar-close", ui.dialog | ui).hide() }
        });
        
        // Need to create the buttons as an object because otherwise the button name cannot 
        // be specified dynamically (jquery interprets the variable name as the button name even 
        // when it's not in quotes). Additionally, this button object has to be created *after*
        // the dialog is initialized, because the dynamic redirectFn needs a reference to the 
        // existing dialog object.
        var dialog_obj = $("#" + dialog_id);
        var dialog_buttons = {};
        dialog_buttons[redirectBtnTitle] = function() { redirectFn(dialog_obj); };
        $(dialog_obj).dialog("option", "buttons", dialog_buttons);
    }
}

function goToIndex(d) {
    closeDialog(d);
    window.location.href = '/' + website_id;
}

function closeDialog(d) {
    $(d).dialog("close");
}

// Account Settings page: resend user confirmation email
function resendConfirmationEmail(btn) {
    $(btn).attr("disabled", "disabled");
    $.ajax({
        async: true,
        type: 'GET',
        url: '/' + website_id + '/account',
        data: {'resend-email': 'true' },
        dataType: 'json',
        error: function(jqXHR, textStatus, errorThrown) { 
            $(btn).removeAttr("disabled");
            createDialog("Failed", 
                        "<p>The confirmation email could not be resent due to the following error: " + errorThrown + "</p>", 
                        default_dialog_width);
        },
        success: function(data, textStatus, jqXHR) {
            $(btn).removeAttr("disabled");
            response_text = jqXHR.responseText;
            page_response = JSON && JSON.parse(response_text) || $.parseJSON(response_text);
            if (page_response['status'] == 'success') {
                // Notify user 
                createDialog("Success", 
                        "<p>The confirmation email has been resent successfully. Please check your email client in a few minutes.</p>", 
                        default_dialog_width);
            } else {
                var error_msg = page_response['error'];
                createDialog("Failed", 
                        "<p>" + error_msg + "</p>", 
                        default_dialog_width);
            }
        }
    });
}

function preventResubmission(link, notification) {
    if ($(link).is("button")) {
        $(link).attr("disabled", "disabled");
    } else {
        $(link).addClass("not-active");
    }
    $(link).siblings(".ajax_loader").removeClass("invisible");
    $(link).siblings(".ajax_loader").children(".ajax_loader_msg").html(notification);
}



// Session page: if any changes made to any of the form fields, update the unsaved changes boolean flag
function setUnsavedChanges() {
    var unsaved_changes_id = "unsaved_changes";
    if ($("#" + unsaved_changes_id).length > 0) {
        $("#" + unsaved_changes_id).val("yes");
    }
}

function resetUnsavedChanges() {
    var unsaved_changes_id = "unsaved_changes";
    if ($("#" + unsaved_changes_id).length > 0) {
        $("#" + unsaved_changes_id).val("");
    }
}

function detectFieldChanges(field) { 
    if ($(field).val() != "") {
        setUnsavedChanges();
    } else {
        resetUnsavedChanges();
    }
}

function ajaxToPhoneAPI() {
    $.ajax({
        async: true,
        type: 'POST',
        url: '/' + website_id + '/phone/session',
        crossDomain: true,
        data: {'auth_name': 'system', 
               'auth_pass': '14a90af63c607ba3c1ff3906f9f5150b61eae1cc56654ef2595b7491c633619f156a8b08f1ae3798413e1bff17bf6a01f0cf1ae9417f8bfab2bce120e0fac5ba',
               'user_passcode': 1,
               'user_birthyear': 1990,
               'user_birthmonth': 9,
               'user_birthday': 25},
        dataType: 'json',
        error: function(jqXHR, textStatus, errorThrown) { 
            console.log('AJAX request error from /phone/session: ' + textStatus + ", " + errorThrown);
        },
        success: function(data, textStatus, jqXHR) {
            console.log('Sent AJAX request to /phone/session!');
            
        }
    });
}

function stroopTaskBegin(btn) {
    // Start recording audio
    toggleRecordingSilent(btn, stroopTaskNextItemHelper, null);
    
    // Display the first item
    $(btn).closest("div.stroop-slide").addClass("invisible");
    $(btn).closest("div.stroop-slide").next("div.stroop-slide").removeClass("invisible");
}

function stroopTaskNextItemHelper(audioRecordingInstance) {
    // This function executes on success of the audio recording for the previous Stroop item
    // "btn" is the initiating DOM element that was clicked to start the audio recording.
    var btn = audioRecordingInstance.initiatingElement; // this is the element that initiated the recording that just finished
    var btn_current = $(btn).closest("div.stroop-slide").next("div.stroop-slide").children("button")[0];
    
    // Display the next item, if there is one
    if ($(btn_current).closest("div.stroop-slide").next("div.stroop-slide").length > 0) {
        
        // Start recording audio for the next instance, and display the next instance
        toggleRecordingSilent(btn_current, stroopTaskNextItemHelper, null);
        
        $(btn_current).closest("div.stroop-slide").addClass("invisible");
        $(btn_current).closest("div.stroop-slide").next("div.stroop-slide").removeClass("invisible");
    } else {
        // End of task - move on to next task (submit the form)
        $("#submit_btn").click();
    }
    
}

function stroopTaskNextItem(btn) {
    // Stop recording audio for the previous instance
    toggleRecordingSilent(btn, stroopTaskNextItemHelper, null);
}