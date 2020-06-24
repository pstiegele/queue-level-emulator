#!/bin/bash
mkdir -p out
sudo rm stopQueueingRunner
sudo python3 topo.py
#cat out/*.json | grep "bits_per_second"
python plotJson.py --path out/iperf_client_1.json --out out/iperf_client_1.pdf
python plotJson.py --path out/iperf_client_2.json --out out/iperf_client_2.pdf
python plotPcap.py
python plotting.py
