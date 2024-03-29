var wsUri = 'ws://localhost:8765/png';

var KeyMap = {A: [88], B: [90], Select: [17], Start: [13], Up: [38], Down: [40], Left: [37], Right: [39],
            UpLeft: [38, 37], UpRight: [38, 39], DownLeft: [40, 37], DownRight: [39, 40],
            A2: [103], B2: [105], Select2: [99], Start2: [97], Up2: [104], Down2: [98], Left2: [100], Right2: [102],
            UpLeft2: [104, 100], UpRight2: [104, 102], DownLeft2: [98, 100], DownRight2: [98, 102]};

window.addEventListener("load", function() {

    // kindle a websocket
    var websocket;
    function status(m) { document.getElementById('socketStatus').innerHTML = m; }

    function png_onopen(e) { status('CONNECTED'); }
    function png_onclose(e) { status('DISONNECTED'); setTimeout(connect_png_ws, 5000); }
    function png_onerror(e) { status('ERROR: '+e.data); setTimeout(connect_png_ws, 5000); }


    function connect_png_ws() {
        websocket = new WebSocket(wsUri);
        websocket.onopen  = png_onopen;
        websocket.onclose = png_onclose;
        websocket.onerror = png_onerror;
    }

    connect_png_ws();


    var controller_ws = new WebSocket('ws://localhost:8765/getcontrols');
    controller_ws.onopen  = function(evt) { console.log('controller sock opened'); };
    controller_ws.onclose = function(evt) { console.log('controller sock closed'); };
    controller_ws.onerror = function(evt) { console.log('controller sock error'); };
    controller_ws.onmessage = function(evt) {
        console.log(evt.data);
        // e.g. '+Right', '-Right', '+A', '-A', '>local roms/Super Mario.nes'
        var op = evt.data[0]
        value = evt.data.substr(1)

        //code = KeyMap[value]
        if (op == '+') {
            for (var ii=0; ii<KeyMap[value].length; ii++) {
                code = KeyMap[value][ii];
                nes.keyboard.keyDown({keyCode: code});
            }
        } else if (op == '-') {
            for (var ii=0; ii<KeyMap[value].length; ii++) {
                code = KeyMap[value][ii];
                nes.keyboard.keyUp({keyCode: code});
            }
        } else if (op == '>') {
            // Select game
            $('select')[0].value = value
            nes.ui.loadROM();
        }
    };

    // on every frame, send a png of the canvas over the socket
    var origFrame = JSNES.prototype.frame;
    var firstFrame;
    var how_frames = 0;
    var tot_frames = 0;
    var discard_frame = 0;
    JSNES.prototype.frame = function() {
        discard_frame = 1 - discard_frame;
        if (discard_frame == 0) {
            websocket.send(document.querySelector('.nes-screen').toDataURL("image/jpeg", 1.0)); //("image/png");
            how_frames++;
            tot_frames++;
        }
        origFrame.apply(this);
    }

    setInterval(function() {
        console.log((how_frames/5) + " actual frames/sec, " + tot_frames + " total");
        how_frames = 0;
    }, 5000);

}, false);
