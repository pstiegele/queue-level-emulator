extern crate pnet;

use pnet::datalink::{self, NetworkInterface};
use pnet::datalink::Channel::Ethernet;
use pnet::packet::{Packet, MutablePacket};
use pnet::packet::ethernet::{EthernetPacket, MutableEthernetPacket};
use std::thread;
use std::time::Duration;

use std::env;

// Invoke as echo <interface name>
fn main() {

    thread::spawn(|| {
        forward("h2-eth0".to_string(), "h2-eth1".to_string(), "00:00:00:00:00:01".to_string(), "00:00:00:00:00:03".to_string());
    });

    thread::spawn(|| {
        forward("h2-eth1".to_string(), "h2-eth0".to_string(), "00:00:00:00:00:03".to_string(), "00:00:00:00:00:01".to_string());
    });

    while true {
        thread::sleep(Duration::from_millis(1000)); 
    }

}

fn forward(receivingInterface:String, sendingInterface:String, srcMac:String, destMac:String){

    let interface_name_rec = receivingInterface;
    let interface_names_match_rec =
        |iface: &NetworkInterface| iface.name == interface_name_rec;

    // Find the network interface with the provided name
    let interfaces_rec = datalink::interfaces();
    let interface_rec = interfaces_rec.into_iter()
                              .filter(interface_names_match_rec)
                              .next()
                              .unwrap();




    let interface_name_send = sendingInterface;
    let interface_names_match_send =
        |iface: &NetworkInterface| iface.name == interface_name_send;

    // Find the network interface with the provided name
    let interfaces_send = datalink::interfaces();
    let interface_send = interfaces_send.into_iter()
                            .filter(interface_names_match_send)
                            .next()
                            .unwrap();

    // Create receiver
    let (mut tx_rec, mut rx_rec) = match datalink::channel(&interface_rec, Default::default()) {
        Ok(Ethernet(tx, rx)) => (tx, rx),
        Ok(_) => panic!("Unhandled channel type"),
        Err(e) => panic!("An error occurred when creating the datalink channel: {}", e)
    };


    // Create transmitter
    let (mut tx_send, mut rx_send) = match datalink::channel(&interface_send, Default::default()) {
        Ok(Ethernet(tx, rx)) => (tx, rx),
        Ok(_) => panic!("Unhandled channel type"),
        Err(e) => panic!("An error occurred when creating the datalink channel: {}", e)
    };

    loop {
        match rx_rec.next() {
            Ok(packet) => {
                //println!("packet received");
                let packet_unwrapped = EthernetPacket::new(packet).unwrap();

                // Constructs a single packet, the same length as the the one received,
                // using the provided closure. This allows the packet to be constructed
                // directly in the write buffer, without copying. If copying is not a
                // problem, you could also use send_to.
                //
                // The packet is sent once the closure has finished executing.
                // let interface_name = &sendingInterface;
                // let interface_names_match =
                //     |iface: &NetworkInterface| iface.name == *interface_name;
            
                // // Find the network interface with the provided name
                // let interfaces = datalink::interfaces();
                // let interface = interfaces.into_iter()
                //                           .filter(interface_names_match)
                //                           .next()
                //                           .unwrap();
                //if(packet_unwrapped.get_destination()=="123"){
                    //println!("destination: {}", packet_unwrapped.get_destination().to_string());
                    //println!("source: {}", packet_unwrapped.get_source().to_string());

                if(packet_unwrapped.get_source().to_string()==srcMac){
                    if(packet_unwrapped.get_destination().to_string()==destMac||packet_unwrapped.get_destination().to_string()=="ff:ff:ff:ff:ff:ff"){
                        tx_send.send_to(&packet, None);
                    }

                }
                    
                //}
                

                // tx.build_and_send(1, packet.packet().len(),
                //     &mut |mut new_packet| {
                //         let mut new_packet = MutableEthernetPacket::new(new_packet).unwrap();

                //         // Create a clone of the original packet
                //         new_packet.clone_from(&packet);

                //         // Switch the source and destination
                //         new_packet.set_source(packet.get_destination());
                //         new_packet.set_destination(packet.get_source());
                // });
            },
            Err(e) => {
                // If an error occurs, we can handle it here
                panic!("An error occurred while reading: {}", e);
            }
        }
    }
}