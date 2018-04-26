"""
    Constants used by OISE study (Talk2Me Jr)
"""

READING_FLUENCY_TASK_ID = 16

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