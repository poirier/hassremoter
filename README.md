# hassremoter
Custom homeassistant component for me to control my tv, roku, receiver, firestick, and chromecast

This is not intended to be useful for anyone else, but might be interesting to look at.

Start reading at ```remoter/__init__.py```.

# How to install

* Find the ```configuration.yaml``` file in the Homeassistant installation.
* If there's not a ```custom_components``` directory in the same directory as configuration.yaml, create it.
* Copy the remoter directory from here into custom_components.
* Add "remoter:" to configuration.yaml.
* Restart homeassistant.

For debugging, I usually add logging statements at level warning or greater, and tail the homeassistant.log file in the same directory as configuration.yaml.
