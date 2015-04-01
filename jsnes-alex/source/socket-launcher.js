console.log('pwnage');

var wsUri = 'ws://localhost:9000/';

window.addEventListener("load", function() {

    var status = document.getElementById('socketStatus'); 
    function output(m) { status.innerHTML = m; }

    // init websocket
    var websocket = new WebSocket(wsUri);    
    websocket.binaryType = "arraybuffer";
    websocket.onopen  = function(e) { output('CONNECTED'); };
    websocket.onclose = function(e) { output('DISCONNECTED'); };
    websocket.onerror = function(e) { output('ERROR: ' + e.data); };

    // hook frame function
    var origFrame = JSNES.prototype.frame;
    JSNES.prototype.frame = function() {
        onFrame();
        origFrame.apply(this);
    }

    var canvas = document.querySelector('.nes-screen');
    var context = canvas.getContext('2d');
    var width = canvas.clientWidth;
    var height = canvas.clientHeight;

    function onFrame() {
        var pixels = context.getImageData(0, 0, width, height);
        var pngdata = canvas.toDataURL("image/png");
        websocket.send(pngdata);
    }

}, false);
