#!/bin/bash
sudo gcc -pthread h2_forwarding.c -lpcap 
./a.out &
