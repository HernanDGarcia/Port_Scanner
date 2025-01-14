import socket
import argparse
import signal
from concurrent.futures import ThreadPoolExecutor
from termcolor import colored
import sys

open_sockets = []

def def_handler(sig, frame):
    print(colored(f"\n [!] Saliendo del programa ...", 'red'))

    for socket in open_sockets:
        socket.close()

    sys.exit(1)

signal.signal(signal.SIGINT, def_handler) # Ctrl+C

def get_arguments():
    parser = argparse.ArgumentParser(description='Fast TCP Port Scanner')
    parser.add_argument("-t", "--target", required=True, dest="target", help="Victim tarjet to scan (Ex = 192.3168.1.1)")
    parser.add_argument("-p", "--port",required=True,  dest="port", help="Port range to scan or ports to scan (Ex: -p 100-500 or -p 22,10,500)")
    options = parser.parse_args()
        
    return options.target, options.port

def create_socket():

    s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    s.settimeout(0.02)
    open_sockets.append(s)
    return s

def port_scanner(port, host):
    
    s = create_socket()

    try:
        s.connect((host, port))
        s.sendall(b"HEAD / HTTP/1.0\r\n\r\n")
        response = s.recv(1024)
        response = response.decode(errors='ignore').split('\n')

        if response:
            print(colored(f"\n[+] El puerto {port} esta abierto", 'green'))

            for line in response:
                print(colored(f"{line}", 'grey'))

        else:       
            print(colored(f"\n[+] El puerto {port} esta abierto", 'green'))
          

    except(socket.timeout, ConnectionRefusedError):
        s.close()

def scan_ports(ports, target):

    with ThreadPoolExecutor(max_workers=100) as executor:
        executor.map(lambda port: port_scanner(port, target), ports)
        
        
def parse_ports(ports_str):

    if '-' in ports_str:
        start, end = map(int , ports_str.split('-'))
        return range(start, end+1)
    elif ',' in ports_str:
       return map(int,ports_str.split(','))
    else:
        return (int(ports_str),)

def main():

    tarjet, ports_str = get_arguments()
    ports = parse_ports(ports_str)
    scan_ports(ports, tarjet)    

if __name__ == '__main__':
    main()
