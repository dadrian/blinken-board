var wsUri = 'ws://localhost:8765/png';

window.addEventListener("load", function() {

    // kindle a websocket
    var websocket = new WebSocket(wsUri);
    function status(m) { document.getElementById('socketStatus').innerHTML = m; }
    websocket.onopen  = function(e) { status('CONNECTED'); };
    websocket.onclose = function(e) { status('DISCONNECTED'); };
    websocket.onerror = function(e) { status('ERROR: '+e.data); };

    // on every frame, send a png of the canvas over the socket
    var origFrame = JSNES.prototype.frame;
    JSNES.prototype.frame = function() {
        websocket.send(document.querySelector('.nes-screen').toDataURL("image/png"));
        origFrame.apply(this);
    }

}, false);
