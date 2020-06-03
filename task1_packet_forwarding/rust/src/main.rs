extern crate pnet;

use pnet::datalink::{self, NetworkInterface};
use pnet::datalink::Channel::Ethernet;
use pnet::packet::ethernet::{EthernetPacket};
use std::thread;
use std::time::Duration;


fn main() {

    thread::spawn(|| {
        forward("h2-eth0".to_string(), "h2-eth1".to_string(), "00:00:00:00:00:01".to_string(), "00:00:00:00:00:03".to_string());
    });

    thread::spawn(|| {
        forward("h2-eth1".to_string(), "h2-eth0".to_string(), "00:00:00:00:00:03".to_string(), "00:00:00:00:00:01".to_string());
    });

    loop {
        thread::sleep(Duration::from_millis(1000)); 
    }

}

fn forward(receiving_interface:String, sending_interface:String, src_mac:String, dest_mac:String){

    let interface_name_rec = receiving_interface;
    let interface_names_match_rec =
        |iface: &NetworkInterface| iface.name == interface_name_rec;

    let interfaces_rec = datalink::interfaces();
    let interface_rec = interfaces_rec.into_iter()
                              .filter(interface_names_match_rec)
                              .next()
                              .unwrap();




    let interface_name_send = sending_interface;
    let interface_names_match_send =
        |iface: &NetworkInterface| iface.name == interface_name_send;

    let interfaces_send = datalink::interfaces();
    let interface_send = interfaces_send.into_iter()
                            .filter(interface_names_match_send)
                            .next()
                            .unwrap();

    // Create receiver
    let (_tx_rec, mut rx_rec) = match datalink::channel(&interface_rec, Default::default()) {
        Ok(Ethernet(tx, rx)) => (tx, rx),
        Ok(_) => panic!("Unhandled channel type"),
        Err(e) => panic!("An error occurred when creating the datalink channel: {}", e)
    };


    // Create transmitter
    let (mut tx_send, _rx_send) = match datalink::channel(&interface_send, Default::default()) {
        Ok(Ethernet(tx, rx)) => (tx, rx),
        Ok(_) => panic!("Unhandled channel type"),
        Err(e) => panic!("An error occurred when creating the datalink channel: {}", e)
    };

    loop {
        match rx_rec.next() {
            Ok(packet) => {
                //println!("packet received");
                let packet_unwrapped = EthernetPacket::new(packet).unwrap();


                if packet_unwrapped.get_source().to_string()==src_mac {
                    if packet_unwrapped.get_destination().to_string()==dest_mac || packet_unwrapped.get_destination().to_string()=="ff:ff:ff:ff:ff:ff" {
                        tx_send.send_to(&packet, None);
                    }

                }
                                    
                
            },
            Err(e) => {
                // If an error occurs, we can handle it here
                panic!("An error occurred while reading: {}", e);
            }
        }
    }
}
