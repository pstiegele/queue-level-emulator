#!/bin/bash
#forwardTraffic needs to be placed into the go src folder
cd /usr/local/go/bin
./go build forwardTraffic
./forwardTraffic
