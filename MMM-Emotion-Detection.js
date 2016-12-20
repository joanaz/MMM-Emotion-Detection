/* global Module */

/* Magic Mirror
 * Module: MMM-Facial-Recognition
 *
 * By Paul-Vincent Roll http://paulvincentroll.com
 * MIT Licensed.
 */

Module.register('MMM-Emotion-Detection', {

  defaults: {
    // recognition intervall in seconds (smaller number = faster but CPU intens!)
    interval: 10

  },

  // Override socket notification handler.
  socketNotificationReceived: function(notification, payload) {

    if (payload.smiling != this.smiling) {
      this.smiling = payload.smiling
      if (this.smiling) {
        this.message = "You are smiling~"
          // this.sendNotification("SHOW_ALERT", {
          //   type: "notification",
          //   message: "You are smiling"

        // });
      } else {
        this.message = "You are not smiling~"
          // this.sendNotification("SHOW_ALERT", {
          //   type: "notification",
          //   message: "You are not smiling"

        // });
      }
      this.updateDom()
    }
  },

  start: function() {
    this.message = "detecting your smile...";
    this.smiling = undefined

    this.sendSocketNotification('CONFIG', this.config);
    Log.info('Starting module: ' + this.name);
  },

  getDom: function() {
    var wrapper = document.createElement("div");
    // this.message = "Hello"
    var message = document.createTextNode(this.message);

    wrapper.className = 'thin large bright';
    wrapper.appendChild(message);

    return wrapper;
  },

});