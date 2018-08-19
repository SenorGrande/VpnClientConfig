import socket
import sys
from Crypto.PublicKey import RSA
#import pickle
from base64 import urlsafe_b64encode, urlsafe_b64decode
from Crypto.Cipher import AES
from Crypto import Random


# Create a TCP/IP socket
sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
# Connect the socket to the port where the server is listening
server_address = ('35.231.58.65', 8090)
print >>sys.stderr, 'connecting to %s port %s' % server_address
sock.connect(server_address)

# Ask user for the vpn name and client config they want from it
vpnName = raw_input("VPN Name: ")
clientName = raw_input("Client Name: ")
# Send vpnName and clientName to server
sock.sendall(vpnName)
sock.sendall(clientName)

print >>sys.stderr, "Generating Public Private Key..."
# create public and private keys
 # Generate a public/private key pair using 4096 bits key length (512 bytes)
new_key = RSA.generate(4096, e=65537)
 # The private key in PEM format
private_key = new_key.exportKey("PEM")
 # The public key in PEM format
public_key = new_key.publickey().exportKey("PEM")

print("Created key")

# send public key
#sock.sendall(str(public_key))
#sock.sendall("This is what the public key is")
#sock.sendall("done")
fileName = clientName + '.ovpn'
f = open(fileName, 'wb')

print("Sent key")

# Receive the OVPN config data and write it to file
try:
    data = ""
    l = sock.recv(1024)
    while(l):
        print("Receiving chunk...")
        #f.write(l)
        data += l
        l = sock.recv(1024)
    # decrypt data
    #test = new_key.decrypt(data)
    f.write(data)
    f.close()

finally:
    sock.close()

