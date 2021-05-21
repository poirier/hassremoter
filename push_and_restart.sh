#!/bin/bash

scp -r remoter homeassistant@junebug.mynet:.homeassistant/custom_components/

ssh -t poirier@junebug.mynet sudo systemctl stop homeassistant
sleep 1
ssh -t poirier@junebug.mynet sudo systemctl start homeassistant
