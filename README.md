# Lab 2020 ACS5 - Queue Level Emulator

As part of the Multimedia Communications Lab in the summer semester 2020 at TU Darmstadt, we, Dat Tran and Paul Stiegele, are creating an user-space queue level simulator.

## Getting Started

These instructions will get you a copy of the project up and running on your virtual machine. 


### Task 1 - Package forwarding with implementations in different languages

We recommend Ubuntu 18.04. as operating system inside a virtual machine for example with Virtualbox. For the use of Mininet you will also need to create a *Host-only Adapter Network*. 
You also need to install the following packages:

* [Mininet](http://mininet.org/download/) (summarized: `git clone git://github.com/mininet/mininet || mininet/util/install.sh -a`)
* ifconfig (`apt-get install net-tools`)
* iperf3 (`apt-get install iperf3`)


To run the script simply cd into the *task1_packet_forwarding* folder and run
`sudo python3 lab1.py`

The script should then ask for the desired implementation and evaluation method and finally output the result.

### Task 2 - Active Queue Level Emulator

You can start the topology by running `sudo python3 lab2.py` inside the *task2_queue_level_emulator* folder. After running this, the Mininet CLI starts and you can type in `xterm h1 h2 h3` to open a console for every host. 
Then you can build and start the Active Queue Level Emulator inside the h2 console window by running `./buildAndRun.sh`. 
When you do not have golang installed, try to just run the executable: `cd aqmEmulator;./aqmEmulator`

To build the project manually, you need to have golang installed. Run this command inside the aqmEmulator folder: `/usr/local/go/bin/go build -o ./ aqmEmulator.go`, mark the file as executable by running `chmod +x ./aqmEmulator` and start the program by running `./aqmEmulator`

To install the Active Queue Level Emulator run `go install` inside of the *task2_queue_level_emulator/aqmEmulator* folder. After this you can run it with `sudo ~/go/bin/aqmEmulator`

h2.cmd('cd aqmEmulator')
    h2.cmd('/usr/local/go/bin/go build -o ./ aqmEmulator.go')
    #print("***** run aqm emulator")
    h2.cmd('chmod +x ./aqmEmulator')
    #h2.cmd('./aqmEmulator &')

## Authors

* **Dat Tran** - [dat.tran@stud.tu-darmstadt.de](mailto:dat.tran@stud.tu-darmstadt.de)
* **Paul Stiegele** - [paul@stiegele.name](mailto:paul@stiegele.name)


## License

tbd
