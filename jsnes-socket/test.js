

var page = require('webpage').create();

page.onError = function(msg, trace) {

  var msgStack = ['ERROR: ' + msg];

  if (trace && trace.length) {
    msgStack.push('TRACE:');
    trace.forEach(function(t) {
      msgStack.push(' -> ' + t.file + ': ' + t.line + (t.function ? ' (in function "' + t.function +'")' : ''));
    });
  }

  console.error(msgStack.join('\n'));

};

page.onConsoleMessage = function(msg, lineNum, sourceId) {
  console.log('> ' + msg);
};

page.open('http://127.0.0.1:8000/index.html', function (status) {
    if (status == 'success') {
        console.log('success???');


        console.log(page);
        // Select game to play...
        page.evaluate(function() {
            console.log('setting game...');
            $('select')[0].value = 'local-roms/Mario Bros. (JU) [!].nes';
            nes.ui.loadROM();
        });

        //page.includeJs('http://127.0.0.1:8000/test2.js', function () {
        //    console.log('what is going on...' + foo);
        //});
    } else {
        console.log('failure???');
    }
    //phantom.exit();
});

//page.includeJs('test2.js', function () { console.log('included...' + foo); });

