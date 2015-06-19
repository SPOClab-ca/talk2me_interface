/*License (MIT)

Copyright Â© 2013 Matt Diamond

Permission is hereby granted, free of charge, to any person obtaining a copy of this software and associated 
documentation files (the "Software"), to deal in the Software without restriction, including without limitation 
the rights to use, copy, modify, merge, publish, distribute, sublicense, and/or sell copies of the Software, and 
to permit persons to whom the Software is furnished to do so, subject to the following conditions:

The above copyright notice and this permission notice shall be included in all copies or substantial portions of 
the Software.

THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR IMPLIED, INCLUDING BUT NOT LIMITED TO 
THE WARRANTIES OF MERCHANTABILITY, FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE 
AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER LIABILITY, WHETHER IN AN ACTION OF 
CONTRACT, TORT OR OTHERWISE, ARISING FROM, OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER 
DEALINGS IN THE SOFTWARE.
*/

(function(window){

  var Recorder = function(source, cfg){
    var config = cfg || {};
    var bufferLen = config.bufferLen || 4096;
    this.context = source.context;
    this.instanceid = null;
    if(!this.context.createScriptProcessor){
       this.node = this.context.createJavaScriptNode(bufferLen, 2, 2);
    } else {
       this.node = this.context.createScriptProcessor(bufferLen, 2, 2);
    }
   
    var worker = new Worker(config.workerPath || RECORDER_WORKER_PATH);
    worker.postMessage({
      command: 'init',
      config: {
        sampleRate: this.context.sampleRate
      }
    });
    var recording = false,
      currCallback;

    this.node.onaudioprocess = function(e){
      if (!recording) return;
      worker.postMessage({
        command: 'record',
        buffer: [
          e.inputBuffer.getChannelData(0),
          e.inputBuffer.getChannelData(1)
        ]
      });
    }

    this.configure = function(cfg){
      for (var prop in cfg){
        if (cfg.hasOwnProperty(prop)){
          config[prop] = cfg[prop];
        }
      }
    }

    this.record = function(){
      recording = true;
    }

    this.stop = function(){
      recording = false;
    }

    this.clear = function(){
      worker.postMessage({ command: 'clear' });
    }
    
    this.setInstanceId = function(instance_id) {
        this.instanceid = instance_id;
    }

    this.getBuffers = function(cb) {
      currCallback = cb || config.callback;
      worker.postMessage({ command: 'getBuffers' })
    }

    this.exportWAV = function(cb, type){
      currCallback = cb || config.callback;
      type = type || config.type || 'audio/wav';
      if (!currCallback) throw new Error('Callback not set');
      worker.postMessage({
        command: 'exportWAV',
        type: type
      });
    }

    this.exportMonoWAV = function(cb, type){
      currCallback = cb || config.callback;
      type = type || config.type || 'audio/wav';
      if (!currCallback) throw new Error('Callback not set');
      worker.postMessage({
        command: 'exportMonoWAV',
        type: type
      });
    }

    worker.onmessage = function(e){
      var blob = e.data;
      currCallback(blob);
    }

    source.connect(this.node);
    this.node.connect(this.context.destination);   // if the script node is not connected to an output the "onaudioprocess" event is not triggered in chrome.
  };

  Recorder.sendToServer = function(blob, instanceid) {
    
    $("#form_errors").addClass("invisible");
    $("#status_recording_" + instanceid).find("img").removeClass("invisible");
    $("#status_recording_" + instanceid + "_msg").html("Sending audio data to server, please be patient...");
    $("#status_recording_" + instanceid).removeClass("invisible");
    var fd = new FormData();
    fd.append('fname', 'test.wav');
    fd.append('data', blob);
    fd.append('instanceid', instanceid);
    $.ajax({
        type: 'POST',
        url: '/talk2me/audiotest',
        data: fd,
        processData: false,
        contentType: false,        
        dataType: 'json',
        error: function(jqXHR, textStatus, errorThrown) {
            $("#status_recording_" + instanceid).addClass("invisible");
            
            // Re-enable recording button
            $("#btn_recording_" + instanceid).prop("disabled", false);
            
            // Display error message
            $("#form_errors").html("<strong>The audio data could not be submitted.</strong> Error 701: " + textStatus + " - " + errorThrown + ". Please contact the website administrators to report this error.").removeClass("invisible");
            $("body").scrollTop(0);
        },
        success: function(data, textStatus, jqXHR) {
            // Mark the response field as completed, and mark the field as changed
            $("#response_audio_" + instanceid).val("yes");
            $("#unsaved_changes").val("yes");
            
            // Re-enable submit button only if ALL response audio fields have been submitted
            var incomplete_responses = [];
            $("[name^='response_audio_']").each(function() {
                if ($(this).val() == "") {
                    incomplete_responses.push($(this).attr("name"));
                }
            });
            if (incomplete_responses.length == 0) {
                $("#submit_btn").prop('disabled',false);
            }
            
            // Disable the recording button to prevent redoing the task
            $("#status_recording_" + instanceid).find("img").addClass("invisible");
            $("#status_recording_" + instanceid + "_msg").html("Done!");
            
            
        }
    });
  }

  Recorder.setupDownload = function(blob, filename){
    
    var url = (window.URL || window.webkitURL).createObjectURL(blob);
    var link = document.getElementById("save");
    link.href = url;
    link.download = filename || 'output.wav';
  }

  window.Recorder = Recorder;

})(window);
