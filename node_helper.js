'use strict';
const NodeHelper = require('node_helper');

const PythonShell = require('python-shell');
var pythonStarted = false

module.exports = NodeHelper.create({

  python_start: function() {
    const self = this;
    const pyshell = new PythonShell('modules/' + this.name + '/code/main.py', {
      mode: 'json',
      args: [JSON.stringify(this.config)]
    });

    pyshell.on('message', function(message) {


      if (message.hasOwnProperty('result')) {
        console.log("[" + self.name + "] " + (message.result.smiling ? "Smiling" : "Not smiling"));
        self.sendSocketNotification('user', {

          smiling: message.result.smiling
        });

      } else if (message.hasOwnProperty('error')) {
        console.log("[" + self.name + "] " + message.message)
      }
    });

    pyshell.end(function(err) {
      if (err) throw err;
      console.log("[" + self.name + "] " + 'finished running...');
    });
  },

  // Subclass socketNotificationReceived received.
  socketNotificationReceived: function(notification, payload) {
    if (notification === 'CONFIG') {
      this.config = payload
      if (!pythonStarted) {
        pythonStarted = true;
        this.python_start();
      };
    };
  }

});