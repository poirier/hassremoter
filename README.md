# hassremoter
Custom homeassistant component for me to control my tv, roku, receiver, firestick, and chromecast

This is not intended to be useful for anyone else, but might be interesting to look at.

Start reading at ```remoter/__init__.py```.

# How to install

* Find the ```configuration.yaml``` file in the Homeassistant installation.
* If there's not a ```custom_components``` directory in the same directory as configuration.yaml, create it.
* Copy the remoter directory from here into custom_components.
* Make a 
* Add "lirc:" and "remoter:" to configuration.yaml.
* Restart homeassistant.

For debugging, I usually add logging statements at level warning or greater, and tail the homeassistant.log file in the same directory as configuration.yaml.

# What's this for?

Basically this replaces a universal remote like the Logitech Harmony. I've liked and used older Harmony models, 
except for the reliance on the internet for programming them, but once programmed, they worked solo. The
latest flagship models, though, with the hub, don't work at all, or only poorly, if they don't always have
internet. Bah on that.

I have a cheap [StreamZap remote and IR receiver](http://www.streamzap.com/consumer/pc_remote/).
The receiver is plugged into a USB port on the computer where I run homeassistant.

I set up LIRC on the Linux account running homeassistant, configured
to send button events like KEY_POWER, KEY_UP, etc to the "home-assistant" LIRC client.

I enable the lirc integration on homeassistant. 
Now my custom component can register for ``ir_command_received`` events
and be called whenever a button is pressed on the remote.  Then I can
do whatever I want with it. 

All the components of my home TV setup can be controlled over the network, and have integrations
in Home Assistant:

* Denon receiver: plays all audio. Routes video from other devices to the TV.
  Has Chromecast and Firestick plugged into it.
  Uses the [denonavr](https://www.home-assistant.io/integrations/denonavr/) integration.

* TCL Roku television: shows all video. If I'm watching something in a Roku channel, the optical audio output
  goes to the Denon and it has its current input set to its optical audio input, so the sound comes out the
  big speakers. Otherwise, the roku is set to accept input from one of its HDMI in ports, and the Denon
  sets its input to one of the devices plugged into its own HDMI ports, plays the audio over its speakers,
  and sends the video to the TV. Uses the [Roku](https://www.home-assistant.io/integrations/roku)
  integration.

* Amazon Firestick: plugged into the Denon receiver. I mainly got this because the Jellyfin client is much
  more mature than the one for Roku.  Uses the [androidtv](https://www.home-assistant.io/integrations/androidtv)
  integration.

* Chromecast (4K UHD): plugged into the Denon receiver. I like this least for watching movies and TV because
  you pretty much have to control it from your phone or computer, not a convenient remote. But it's the only
  way to get HBOMax onto your television until HBO makes a deal with Roku and/or Amazon.
  Uses the [cast](https://www.home-assistant.io/integrations/cast) integration, but I'm not doing much
  with that.
  
(NOTE: the Chromecast is obviously on the network. I wonder if I could figure out a way to at least
pause and start it from home assistant.)

Right now, the anonymous red button on the remote turns on
the Denon and the Roku TV and goes to the home screen ready to select a channel. 

The volume keys on the remote always forward to the Denon, because it handles all audio.

The navigation keys are forwarded to whatever device is the current source for the Denon.
E.g. if the Denon source is the Firestick, arrows etc. go to the firestick.

# Why not ...?

Why don't I use scenes? I don't like editing them
in the HA UI. Plus they're not transparent enough - I don't trust that they're going
to do exactly what I want. And the way opening a scene for editing changes its configuration
to match what the devices are currently doing, without my ever asking it to do that,
is obnoxious.
