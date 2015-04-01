var wsUri = 'ws://localhost:9000/';

window.addEventListener("load", function() {

    // init websocket
    var websocket = new WebSocket(wsUri);    
    websocket.binaryType = "arraybuffer";
    function status(m) { document.getElementById('socketStatus').innerHTML = m; }
    websocket.onopen  = function(e) { status('CONNECTED'); };
    websocket.onclose = function(e) { status('DISCONNECTED'); };
    websocket.onerror = function(e) { status('ERROR: '+e.data); };

    // on every frame, send a png of the canvas to the websocket
    var origFrame = JSNES.prototype.frame;
    JSNES.prototype.frame = function() {
        websocket.send(document.querySelector('.nes-screen').toDataURL("image/png"));
        origFrame.apply(this);
    }

}, false);
