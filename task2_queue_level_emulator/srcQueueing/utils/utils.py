import struct, socket # needed for ip2int
import subprocess

def ip2int(addr):
    return struct.unpack("!I", socket.inet_aton(addr))[0]

def gettingMac(IP):
    p = subprocess.Popen(['ping', IP, '-c1'], stdout=subprocess.PIPE, stderr=subprocess.PIPE)
    out, err = p.communicate()
    p = subprocess.Popen(['arp', '-n'], stdout=subprocess.PIPE, stderr=subprocess.PIPE)
    out, err = p.communicate()    
    
    try:
        arp = [x for x in out.split('\n') if IP in x][0]
    except IndexError:
        return ""
    else:
        mac = ' '.join(arp.split()).split()[2]
        mac = mac.replace(":", "")
        mac = mac.decode("hex")
        return mac

def getBitAtPosition(code, position):
    shift_right = code >> position
    return shift_right & 1

if __name__ == '__main__':
    print(ip2int('10.0.2.2'))
    print(ip2int('10.0.3.2'))

