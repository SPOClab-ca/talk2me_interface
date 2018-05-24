"""
    Constants used by OISE study (Talk2Me Jr)
"""
yes_no_map = {
    'yes': 1,
    'no': 0,
    'idk': -1
}

READING_FLUENCY_TASK_ID = 16

MINDMAP_IMAGE_LIGHT = "data:image/png;base64,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"

MINDMAP_IMAGE_MINOR = "data:image/png;base64,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"
DEFAULT_MINDMAP_IMAGE = "data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAATcAA" + \
                        "AChCAYAAACiavjYAAAC13pUWHRteEdyYXBoTW9kZWwAAE1T27Ki" + \
                        "MBD8Gqt2H7QwQcBH7ojA0cOdNzDhJhIEBPXrNxx3q7aKgqFneqa" + \
                        "TdFZQvj3zqsErwDwG3IsFbscVVFYA2ORdNU26Atpuw9D0r7BqEZ" + \
                        "kHGjoefW0ZCkOJRjTBsZ/wybG/6UfsugaHODtW48KH/AZyS4uj4" + \
                        "dnWCsg0bqrrMlTHlytZKHLZkxtFNI6O20AIdputsKUJN83Tvvqv" + \
                        "DaDghPuhIu1HqbD5UbjgGFUj6T/wPM8b1KfzpiJLEqorKKMqLfr" + \
                        "0Risr9KnKGcxxIGXWTI6yNeB3aJ3yGK65LWABn1/2EAif3m1K9f" + \
                        "1wTmmB19tP03cS5R5rz6qdU416w0bkcNrx5psjh9b0HM+Qa0w0s" + \
                        "mOSmO6QNoX+JZ6Z2g70dnIoIvF8kRtCXw56EMJXibvTJS7gt+Bw" + \
                        "LEKPiJ1qnJe0LguPV9BGVimZr+/j8+vMyPr0FF2X68y4Ku+wuUt" + \
                        "6oxF//O7qVtUbi2W6MsnG0Xe6RN7xoquVRnTgA/Np9I1FDlDVqS" + \
                        "Ip0a95mJ3My9DXe9Yrw+CLjvt+5VmeRImwYw12EsbX7TR4dxfYX" + \
                        "emyIXlsg9BidJAZ4wCjU6TuEwWeuxdtmPjGrnH1bOrDgxdf08N4" + \
                        "7HZl8X4Ed58evQZ5X81mJeQDPXctBbwdpQmE/fs+cEo+dUqmgxo" + \
                        "xh+nW+XGtIGNSxceRQZGn1Uai+k1maYEa1RxSU9Y9yHtA9ObrGI" + \
                        "p6V9Y1uUovK0oAUnnD9FpWudR2ca+QWdZ0Udqga+9IuWEyYiyKj" + \
                        "XfUC6qo6B4XOWUbozcSv5GMZyRWp1qkXpfAyyWhji4G3AfodnZu" + \
                        "tgknXCDzbDBtLQ3t8Vx2reNwwlXh27QswmiiNLNjsEKmnFdKG8T" + \
                        "TwTupmdMyIvO6OPlDik+LoWehoLWaET85XLN5ovSUaU0YklZ4hu" + \
                        "28uG15lk3759wfG9P/v9cWqn8At08tQwAADztJREFUeF7tnU1oV" + \
                        "Ncbxt8RTSIuVFpXhS66SFeBiboQWnFmU0V3SaGLtjRjCsGIIaIg" + \
                        "EepHG2oVQyGxSklCKG0XpWRAUTddTKCU7BJBXYhQQqGLQguKaGx" + \
                        "cTDn3z+QfzYfj3I/z8f4uzEJz7znv+zzPfe5z7tzk5qrValXYnE" + \
                        "JgZGREZmZm5NatW7JlyxaZmppyqj6KESkUCvLgwQNpb2+PPkeOH" + \
                        "AEWxxDIYW7uMHLt2jXp7OyUvr4+aWtrk3w+H33Y3ETAXHxmZ2fl" + \
                        "7t27Yi5I5XJZDhw44GaxCqvC3Bwh/fjx43L//n2ZnJyU9evXO1I" + \
                        "VZdSLwMLCgnR0dEQXpXPnztV7GPuliADmliK49Q5tjG3dunVy4c" + \
                        "KFeg9hP0cROHbsWHRxOn/+vKMV6ikLc7PMtVmKjo+Py9WrVy1Xw" + \
                        "vRJIWCWpocPH5b9+/cnNSTjNIAA5tYAaEkesmHDBpmfn2cpmiSo" + \
                        "lsd6+vSpbN26NeKVzR4CmJs97KOb0HNzczI0NGSxCqZOA4H+/n5" + \
                        "pbW2V3t7eNIZnzDoQwNzqACmtXUqlkuzZs0e6urrSmoJxLSFgbj" + \
                        "VMT0/L2NiYpQqYFnOzqAHzfNTExASPe1jkIK2pzSMi3d3d0fOKb" + \
                        "HYQwNzs4B7NWiwWpVKpWKyAqdNEAH7TRPflY2NuL8cotT1yuZzw" + \
                        "CyKpwWt9YPi1SwHmZhF/xG8R/Aymht8MQF5jCszNIv6I3yL4GUw" + \
                        "NvxmAjLnZBXm12RG/m7wkVRX8JoVkY+OQ3BrDLZGjEH8iMDo7CP" + \
                        "zapQZzs4g/4rcIfgZTw28GILMstQsyy1I38U+7KswtbYTXHp/kZ" + \
                        "hF/xG8R/Aymht8MQCa52QWZ5OYm/mlXhbmljTDJzS7Ca11ZeIjX" + \
                        "WW6SKAxzSwLFxsdgWdo4drGPRPyxIXR6APi1Sw/mZhF/xG8R/Ay" + \
                        "mht8MQOaem12QuefmJv5pV4W5pY0w99zsIsw9N2fxT7swzC1thD" + \
                        "E3uwhjbs7in3ZhmFvaCGNudhHG3JzFP+3CMLe0Ecbc7CIcuLl98" + \
                        "cUXcurUqWVd7t27V3788Ud57bXXnMU/7cIwt7QRxtzsIhy4udXa" + \
                        "++eff+TDDz+Uzz77TN555x1nMc+yMMwtS7SXz8WjIBbxD0n8K5n" + \
                        "bb7/9Jp9//rn89ddfsmvXLvn666+jdwq8++67Eeo9PT3R/23cuD" + \
                        "H699IU+MMPP0Rm6fMWEr8+8oC5WWQtJPGvZm7m5cQ//fSTvP322" + \
                        "3Lv3j3p6+uT4eFhefPNN+Xo0aPyxhtvRGnPLGF//fXXyOz++OMP" + \
                        "+eCDD+Sbb77xOgWGxK/F06ThqTG3hqGLf2BI4l/N3Ewaq917W2p" + \
                        "gJq2ZZPf999/Ll19+KSdPnpTdu3cvpjVz3FtvveV1eguJ3/hqz3" + \
                        "4EzC17zBdnDEn8q5mbMa/a0tOY20cfffQc4uaLB/Nuz8HBQfn22" + \
                        "2+f+5lZ0ppU5+sWEr8+coC5WWQtJPHXa26///77MsOan5+Plqgf" + \
                        "f/yx18vQF6UUEr8WT5OGp8bcGoYu/oEhib8ec1t6z83cgzNLzz/" + \
                        "//DNKduVyefGe25MnT6LlqDE7n79UCInf+GrPfgTMLXvM1S5LTe" + \
                        "PmPlvt29IXn4Vb+m2p70tS0yvmZvHkMvhXeSuwNQYQvzXoM5kYf" + \
                        "jOBedVJMDeL+CN+i+BnMDX8ZgDyGlNgbhbxR/wWwc9gavjNAGTM" + \
                        "zS7Iq82O+N3kJamq4DcpJBsbh+TWGG6JHIX4E4HR2UHg1y41mJt" + \
                        "F/BG/RfAzmBp+MwCZZaldkFmWuol/2lVhbmkjvPb4JDeL+CN+i+" + \
                        "BnMDX8ZgAyyc0uyCQ3N/FPuyrMLW2ESW52EV7rysJLmZ3lJonCM" + \
                        "LckUGx8DJaljWMX+0jEHxtCpweAX7v0YG4W8Uf8FsHPYGr4zQBk" + \
                        "7rnZBZl7bm7in3ZVmFvaCHPPzS7C3HNzFv+0C8Pc0kYYc7OLMOb" + \
                        "mLP5pF4a5pY0w5mYXYczNWfzTLgxzSxthzM0uwmvMXiwWpVKpOF" + \
                        "sfhcVDAH7j4Rf3aL4tjYtgjOPb29tlYmJC8vl8jFE41EUEZmdnp" + \
                        "bu7O3pPK5sdBDA3O7hHsx48eDB6nV2pVLJYBVOngcD4+LhMT09H" + \
                        "b/Zis4MA5mYH92jWS5cuydzcnFy8eNFiFUydBgL9/f3S2toqvb2" + \
                        "9aQzPmHUggLnVAVKauzQ3N8ujR4+kqakpzWkYO0MEzNu7tm3bJo" + \
                        "8fP85wVqZ6EQHMzbImbty4IVeuXJHr169broTpk0Jg37590XtYz" + \
                        "du92OwhgLnZw35x5oGBAVlYWJChoSEHqqGEOAgYU9u0aZMMDg7G" + \
                        "GYZjE0AAc0sAxCSGOHHihNy5c0cmJyelpaUliSEZI0MEzFK0o6N" + \
                        "Ddu7cibFliPtaU2FujhBhyrh586Z0dnZKT0+PtLW1yfbt28U8Ls" + \
                        "LmJgLmcQ/zqMft27dldHRUyuUyS1GHqMLcHCKjVsrly5ejk8Z8N" + \
                        "m/eLFNTUw5WqbukQqEgDx8+jC5AO3bskEOHDukGxMHuMTcHSQm1" + \
                        "JH4dKVRm3ewLc3OTlyCrwtyCpNXZpjA3Z6kJrzDMLTxOXe4Ic3O" + \
                        "ZncBqw9wCI9TxdjA3xwkKqTzMLSQ23e8Fc3Ofo2AqxNyCodKLRj" + \
                        "A3L2gKo0jMLQwefekCc/OFqQDqxNwCINGjFjA3j8jyvVTMzXcG/" + \
                        "aofc/OLL6+rxdy8ps+74jE37yjzt2DMzV/ufKwcc/ORNU9rxtw8" + \
                        "Jc7TsjE3T4nzsWzMzUfW/K0Zc/OXO+8qx9y8o8zrgjE3r+nzq3j" + \
                        "MzS++fK8Wc/OdQY/qx9w8IiuAUjG3AEj0pQXMzRemwqgTcwuDRy" + \
                        "+6wNy8oCmYIjG3YKh0vxHMzX2OQqpQnbkVi0XeSWBJwVu2bJEHD" + \
                        "x5Ymp1pX4aAeS9EpVJ52W7e/FyduZEevNEmhWaMQGjnBuaWsYCY" + \
                        "DgRcRQBzc5WZOusKjcA622Y3EHgpAqGdGyS3l1LODiCgAwHMzXO" + \
                        "eQyPQczoo3yEEQjs3SG4OiYtSQMAmApibTfQTmDs0AhOAhCFAIE" + \
                        "IgtHOD5IawQQAEMLcQNBDa1SkETujBDQRCOzdIbm7oiipAwDoCm" + \
                        "Jt1CuIVEBqB8dDgaBD4PwKhnRvBJ7dffvlF3n//fRkeHpZPPvlk" + \
                        "8abpd999J319ffLzzz/Le++9h8ZBQD0CmJuHEmhpaZH169fLxo0" + \
                        "b5e+//5bXX39d5ufn5dmzZ/Lvv/962BElg0B8BEK/8Aef3IwEvv" + \
                        "rqKzl9+rQsLCwsKqKpqUnOnDkjAwMD8VXCCCDgKQIhX/hVmJvRn" + \
                        "UltT58+XZRgc3Pzc//2VJuUDQKxEAj5wq/G3JaSSGqLdT5wcGAI" + \
                        "hHrhV2NuS9MbqS2ws5N2YiEQ6oVflbkZEk+dOiVnz57lXlus04G" + \
                        "DQ0Oglt5CuvCrMjfz7einn34qo6OjYpambCAAAv9DIMQL/6rmNj" + \
                        "IyIjMzM3Lr1i0xf/t+amoKHTiGgPmb9+adBO3t7dHnyJEjjlXoX" + \
                        "zno3n3O6tX9MnO7du2adHZ2Rg+4trW1ST6fjz5sbiJgLj6zs7Ny" + \
                        "9+5dMSdmuVyWAwcOuFmsw1Whe4fJWaG0enT/nLkdP35c7t+/L5O" + \
                        "Tk9FDr2x+IWCe4+vo6IguSufOnfOreIvVonuL4Ccw9Wq6XzQ3Q/" + \
                        "C6devkwoULCUzHEDYROHbsWHRxOn/+vM0yvJgb3XtBU11Fvqj7y" + \
                        "NxMJB8fH5erV6/WNQg7uY+AWZoePnxY9u/f736xlipE95aAT3Ha" + \
                        "pbqPzG3Dhg3R71qyFE0R9YyHNr+NsXXr1ohXtpURQPfhKWOp7nP" + \
                        "Dw8PVubk5GRoaCq9T5R319/dLa2ur9Pb2Kkdiefvmyxd0H6Ysar" + \
                        "rPdXV1Vffs2SNdXV1hdqq4K3OrYXp6WsbGxhSjsHLrpVJJ0H2Ys" + \
                        "qjpPpfP56sTExM87hEgz+YRke7u7uh5RbbnETDPBaL7MFVR032u" + \
                        "UChUK5VKmF3SlRSLRYHf5UIAl7BPDsNvTkTMdwphd6q4u9D+ump" + \
                        "SVIJLUki6OY7hF3Nzk5vEquIkXhlKcElMYk4OhLk5SUuyRXESY2" + \
                        "7JKsqP0TA3P3iKVSXmhrnFEpCnB2NunhL3KmVjbpjbq+gllH0xt" + \
                        "1CYXKMPzA1zUyDzZS1ibgpYx9wwNwUyx9y0ksyjPsuZx/TDPhtI" + \
                        "bmHzG3XHSUxyUyBzkptWkkluJDdt2ie5KWCc5EZyUyBzkptWkkl" + \
                        "uJDdt2ie5KWCc5EZyUyBzkptWkkluJDdt2ie5KWCc5EZyUyBzkp" + \
                        "tWkkluJDdt2ie5KWCc5EZyUyBzkptWkkluJDdt2ie5KWCc5EZyU" + \
                        "yBzkptWkkluJDdt2ie5KWCc5EZyUyBzkptWkkluJDdt2ie5KWCc" + \
                        "5EZyUyBzkptWkkluJDdt2ie5KWCc5EZyUyBzkptWkkluJDdt2ie" + \
                        "5KWCc5EZyUyBzkptWkkluJDdt2ie5KWCc5EZyUyBzkptWkkluJD" + \
                        "dt2ie5KWCc5EZyUyBzkptWkkluJDdt2ie5KWCc5EZyUyBzkptWk" + \
                        "kluJDdt2ie5KWCc5EZyUyBzkptWkkluJDdt2ie5KWCc5EZyUyBz" + \
                        "kptWkkluJDdt2ie5KWCc5EZyUyBzkptWkkluJDdt2ie5KWCc5EZ" + \
                        "yUyDzlZNboVCoVioVjf2r6LlYLAr8LqcaXMKWv+E3l8/nqxMTE5" + \
                        "LP58PuVmF3s7Oz0t3dLTMzMwq7X7vl9vZ2QfdhyqKm+1ypVKru3" + \
                        "r1bSqVSmJ0q7mp8fFymp6dlbGxMMQort37w4EFB92HKoqb73MjI" + \
                        "SHVubk4uXrwYZqeKu+rv75fW1lbp7e1VjMLKrV+6dEnQfZiyqOk" + \
                        "+V61Wq83NzfLo0SNpamoKs1uFXT158kS2bdsmjx8/Vth9fS2j+/" + \
                        "pw8mmvpbqPzO3GjRty5coVuX79uk99UOsaCOzbt0+OHj0qe/fuB" + \
                        "adVEED34Uljqe4jczMtDgwMyMLCggwNDYXXsbKOjKlt2rRJBgcH" + \
                        "lXX+6u2i+1fHzNUjXtT9ormZgk+cOCF37tyRyclJaWlpcbUH6lo" + \
                        "FARPJOzo6ZOfOnRjbK6gE3b8CWA7uuprunzM3U/fNmzels7NTen" + \
                        "p6pK2tTbZv3y7ma3M2NxEwX3ubRz1u374to6OjUi6XWYo2QBW6b" + \
                        "wA0i4fUo/tl5lar9/Lly9FJYz6bN2+Wqakpi60w9UoIFAoFefjw" + \
                        "YXQB2rFjhxw6dAigYiKA7mMCmMHh9er+P4Y/kZ/O0CH3AAAAAEl" + \
                        "FTkSuQmCC"

MINDMAP_HTML = """
<img class="drawio" id="mindmap_task_%d" style="cursor:default;" src="%s"><br><br>
  <script>



var close = function()
{
    window.removeEventListener('message', receive);
    document.body.removeChild(iframe);
};
    // Edits an image with drawio class on double click
    document.addEventListener('dblclick', function(evt)
    {
      var url = 'https://www.draw.io/?embed=1&ui=atlas&spin=1&modified=unsavedChanges&proto=json';
      var source = evt.srcElement || evt.target;

      if (source.nodeName == 'IMG' && source.className == 'drawio')
      {
        if (source.drawIoWindow == null || source.drawIoWindow.closed)
        {
          // Implements protocol for loading and exporting with embedded XML
          var receive = function(evt)
          {
            if (evt.data.length > 0 && evt.source == source.drawIoWindow)
            {
              var msg = JSON.parse(evt.data);

              // Received if the editor is ready
              if (msg.event == 'init')
              {
                // Sends the data URI with embedded XML to editor
                source.drawIoWindow.postMessage(JSON.stringify(
                  {action: 'load', xmlpng: source.getAttribute('src')}), '*');
              }
              // Received if the user clicks save
              else if (msg.event == 'save')
              {
                // Sends a request to export the diagram as XML with embedded PNG
                  source.drawIoWindow.postMessage(JSON.stringify(
                    {action: 'export', format: 'xmlpng', spinKey: 'saving'}), '*');
              }
              // Received if the export request was processed
              else if (msg.event == 'export')
              {
                // Updates the data URI of the image
                source.setAttribute('src', msg.data);
                document.getElementById('imageurl').value = msg.data;
              }

              // Received if the user clicks exit or after export
              if (msg.event == 'exit' || msg.event == 'export')
              {
                // Closes the editor
                window.removeEventListener('message', receive);
                source.drawIoWindow.close();
                source.drawIoWindow = null;
              }
            }
          };

          // Opens the editor
          window.addEventListener('message', receive);
          source.drawIoWindow = window.open(url);

        }
        else
        {
          // Shows existing editor window
          source.drawIoWindow.focus();
        }
      }
    });
  </script>"""