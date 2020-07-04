#!/bin/bash
rm ./aqmEmulator
/usr/local/go/bin/go build -o ./ aqmEmulator.go
echo ""
echo ""
chmod +x ./aqmEmulator
./aqmEmulator
