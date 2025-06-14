import os
import struct
import socket
import select
import fcntl
import array
import threading

TUNSETIFF = 0x400454ca
IFF_TUN   = 0x0001
IFF_NO_PI = 0x1000

def create_tun_interface():
    tun = open('/dev/net/tun', 'r+b', buffering=0)
    ifr = struct.pack('16sH', b'tun0', IFF_TUN | IFF_NO_PI)
    fcntl.ioctl(tun, TUNSETIFF, ifr)
    return tun

def setup_routing(tun_name):
    os.system(f'ip addr add 10.0.0.1/24 dev {tun_name}')
    os.system(f'ip link set {tun_name} up')
    os.system('echo 1 > /proc/sys/net/ipv4/ip_forward')

def handle_client_traffic(tun, sock):
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
    tun = create_tun_interface()
    setup_routing('tun0')

    sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    sock.bind(('0.0.0.0', 5000))
    sock.listen(1)

    print("[*] Waiting for client connection...")
    client, addr = sock.accept()
    print(f"[+] Connection from {addr}")

    handle_client_traffic(tun, client)

if __name__ == '__main__':
    main()