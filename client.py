import os
import struct
import socket
import select
import fcntl
import threading

TUNSETIFF = 0x400454ca
IFF_TUN   = 0x0001
IFF_NO_PI = 0x1000

def create_tun_interface():
    tun = open('/dev/net/tun', 'r+b', buffering=0)
    ifr = struct.pack('16sH', b'tun0', IFF_TUN | IFF_NO_PI)
    fcntl.ioctl(tun, TUNSETIFF, ifr)
    return tun

def setup_routing(tun_name, server_ip):
    os.system(f'ip addr add 10.0.0.2/24 dev {tun_name}')
    os.system(f'ip link set {tun_name} up')
    os.system(f'ip route add default via 10.0.0.1 dev {tun_name}')

def handle_server_traffic(tun, sock):
    while True:
        readable, _, _ = select.select([tun, sock], [], [])
        for fd in readable:
            if fd is tun:
                packet = os.read(tun.fileno(), 2048)
                sock.send(packet)
            elif fd is sock:
                packet = sock.recv(2048)
                os.write(tun.fileno(), packet)

def main():
    SERVER_IP = '1.2.3.4'  # Replace with your server's IP
    
    tun = create_tun_interface()
    
    sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    sock.connect((SERVER_IP, 5000))
    
    setup_routing('tun0', SERVER_IP)
    
    handle_server_traffic(tun, sock)

if __name__ == '__main__':
    main()