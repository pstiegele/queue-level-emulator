/*
    Packet sniffer at Host 2, process packet and then forwardi packet using libpcap library
*/
#include<pcap.h>
#include<stdio.h>
#include<stdlib.h> // for exit()
#include<string.h> //for memset
 
#include<sys/socket.h>
#include<arpa/inet.h> // for inet_ntoa()
#include<net/ethernet.h>
#include<netinet/ip_icmp.h>   //Provides declarations for icmp header
#include<netinet/udp.h>   //Provides declarations for udp header
#include<netinet/tcp.h>   //Provides declarations for tcp header
#include<netinet/ip.h>    //Provides declarations for ip header

#include<pthread.h>   

void modify_ethernet_header_2(const u_char *Buffer, int Size);
void modify_ethernet_header(const u_char *Buffer, int Size);
void process_packet(u_char *, const struct pcap_pkthdr *, const u_char *);
void process_packet2(u_char *, const struct pcap_pkthdr *, const u_char *);
void* sniff_eth1(void*args);
void* sniff_eth0(void*args);

 
FILE *logfile;
struct sockaddr_in source,dest;
int tcp=0,udp=0,icmp=0,others=0,igmp=0,total=0,i,j; 
pcap_t *handle_2;
pcap_t *handle;
int main()
{    
    char errbuf[100];
     
    //Open the device for sniffing
    printf("Opening device h2-eth0");
    handle   = pcap_open_live("h2-eth0" , 65536 , 1 , 0 , errbuf);
    printf("Opening device h2-eth1");
	handle_2=pcap_open_live("h2-eth1" , 65536 , 1  , 0,  errbuf);

    if (handle == NULL) 
    {
        fprintf(stderr, "Couldn't open h2-eth0 : %s\n" ,  errbuf);
        exit(1);
    }
	
	if (handle_2 == NULL) 
    {
        fprintf(stderr, "Couldn't open h2-eth1 : %s\n" ,  errbuf);
        exit(1);
    }
	
	//Store log file
	logfile=fopen("log.txt","w");
    if(logfile==NULL) 
    {
        printf("Unable to create file.");
    }
     
    //Put these 2 devices in sniff loop with threading
    pthread_t tid;
    pthread_t tid2;
    pthread_create(&tid,NULL,sniff_eth0,NULL);
    pthread_create(&tid2,NULL,sniff_eth1,NULL);
    pthread_join(tid,NULL);
    pthread_join(tid2,NULL);

    printf("sniff done");
    return 0;   
}

void* sniff_eth0(void*args)
{ 
    pcap_loop(handle , -1 , process_packet , NULL);
}
void* sniff_eth1(void*args)
{   
    pcap_loop(handle_2 , -1 , process_packet2 , NULL);
}


/*Process packet at h2-eth1*/
void process_packet2(u_char*args,const struct pcap_pkthdr*header, const u_char*buffer)
{
    int size = header->len;

    //Get the IP Header part of this packet , excluding the ethernet header
    struct iphdr *iph = (struct iphdr*)(buffer + sizeof(struct ethhdr));
    ++total;
    switch (iph->protocol) //Check the Protocol and do accordingly...
    {
        case 1:  //ICMP Protocol
            ++icmp;
			printf("ICMP 1");
			modify_ethernet_header_2(buffer,size);
            pcap_inject(handle,buffer,size);
            break;
        default: //Some Other Protocol like ARP etc.
            ++others;
            printf("This is other packets at eth1");
			modify_ethernet_header_2(buffer,size);
            pcap_inject(handle,buffer,size);
            break;
			
    }
}

 /*Process packet at h2-eth0*/
void process_packet(u_char *args, const struct pcap_pkthdr *header, const u_char *buffer)
{
    int size = header->len;
     
    //Get the IP Header part of this packet , excluding the ethernet header
    struct iphdr *iph = (struct iphdr*)(buffer + sizeof(struct ethhdr));
    ++total;
    switch (iph->protocol) //Check the Protocol and do accordingly...
    {
        case 1:  //ICMP Protocol
            ++icmp;
            //print_icmp_packet( buffer , size);
			printf("ICMP 1");
			modify_ethernet_header(buffer,size);
            pcap_inject(handle_2,buffer,size);
			break;
        default: //Some Other Protocol like ARP etc.
            ++others;
			modify_ethernet_header(buffer,size);
			pcap_inject(handle_2,buffer,size);
            break;
    }
}


/*
When h3 ping h1, the L2-header is (dst: Host2's MAC, src: Host3's MAC). We have to modify to (dst: Host1's MAC, src: Host2's MAC)  (Host 2 is a gate way)
*/
void modify_ethernet_header_2(const u_char *Buffer, int Size)
{
    struct ethhdr *eth2 = (struct ethhdr *)Buffer;
    if(eth2->h_source[5]=0x03){

        eth2->h_dest[0]=0x00;
        eth2->h_dest[1]=0x00;
        eth2->h_dest[2]=0x00;
        eth2->h_dest[3]=0x00;
        eth2->h_dest[4]=0x00;
        eth2->h_dest[5]=0x01;


		eth2->h_source[0]=0x00;	
		eth2->h_source[1]=0x00;	
		eth2->h_source[2]=0x00;	
		eth2->h_source[3]=0x00;	
		eth2->h_source[4]=0x00;	
		eth2->h_source[5]=0x02;	
   }

    //fprintf(logfile , "\n");
    //fprintf(logfile , "Ethernet Header\n");
    //fprintf(logfile , "   |-Destination Address : %.2X-%.2X-%.2X-%.2X-%.2X-%.2X \n", eth->h_dest[0] , eth->h_dest[1] , eth->h_dest[2] , eth->h_dest[3] , eth->h_dest[4] , eth->h_dest[5] );
    //fprintf(logfile , "   |-Source Address      : %.2X-%.2X-%.2X-%.2X-%.2X-%.2X \n", eth->h_source[0] , eth->h_source[1] , eth->h_source[2] , eth->h_source[3] , eth->h_source[4] , eth->h_source[5] );
    //fprintf(logfile , "   |-Protocol            : %u \n",(unsigned short)eth->h_proto);
}

/*
When h1 pings h3, the L2-header is (dst: Host2's MAC, src: Host1's MAC). We have to modify to (dst: Host3's MAC, src: Host2's MAC)  (Host 2 is a gate way)
*/
void modify_ethernet_header(const u_char *Buffer, int Size)
{
    struct ethhdr *eth = (struct ethhdr *)Buffer;
   if(eth->h_source[5]=0x01){ 
		eth->h_dest[0]=0x00;
		eth->h_dest[1]=0x00;
		eth->h_dest[2]=0x00;
    	eth->h_dest[3]=0x00;
    	eth->h_dest[4]=0x00;
		eth->h_dest[5]=0x03;
		
		eth->h_source[0]=0x32;
		eth->h_source[1]=0x75;
		eth->h_source[2]=0x3b;
    	eth->h_source[3]=0x81;
    	eth->h_source[4]=0x9f;
		eth->h_source[5]=0xd8;
	
   }
	   
    //fprintf(logfile , "\n");
    //fprintf(logfile , "Ethernet Header\n");
    //fprintf(logfile , "   |-Destination Address : %.2X-%.2X-%.2X-%.2X-%.2X-%.2X \n", eth->h_dest[0] , eth->h_dest[1] , eth->h_dest[2] , eth->h_dest[3] , eth->h_dest[4] , eth->h_dest[5] );
    //fprintf(logfile , "   |-Source Address      : %.2X-%.2X-%.2X-%.2X-%.2X-%.2X \n", eth->h_source[0] , eth->h_source[1] , eth->h_source[2] , eth->h_source[3] , eth->h_source[4] , eth->h_source[5] );
    //fprintf(logfile , "   |-Protocol            : %u \n",(unsigned short)eth->h_proto);
}
 

