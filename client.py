import socket
import sys
from Crypto.PublicKey import RSA
from base64 import urlsafe_b64encode, urlsafe_b64decode
from Crypto.Cipher import AES
from Crypto import Random
from Crypto.Random import random
import string

def keyGenAES(size=6, chars=string.ascii_letters + string.digits):
    return ''.join(random.choice(chars) for _ in range(size))

def encrypt(key, msg):
    iv = Random.new().read(BS)
    cipher = AES.new(key, AES.MODE_CFB, iv, segment_size=AES.block_size * 8)
    encrypted_msg = cipher.encrypt(pad(str(msg)))
    return base64unpad(urlsafe_b64encode(iv + encrypted_msg))

def decrypt(key, msg):
    decoded_msg = urlsafe_b64decode(base64pad(msg))
    iv = decoded_msg[:BS]
    encrypted_msg = decoded_msg[BS:]
    cipher = AES.new(key, AES.MODE_CFB, iv, segment_size=AES.block_size * 8)
    return unpad(cipher.decrypt(encrypted_msg))

# Create a TCP/IP socket
sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
# Connect the socket to the port where the server is listening
#server_address = ('35.201.26.73', 8090) # AWS
server_address = ('35.231.58.65', 8090) # GCP
print >>sys.stderr, 'connecting to %s port %s' % server_address
sock.connect(server_address)

# Ask user for the vpn name and client config they want from it
vpnName = raw_input("VPN Name: ")
clientName = raw_input("Client Name: ")
# Send vpnName and clientName to server
sock.sendall(vpnName)
sock.sendall(clientName)

# Receive public key
data = ""
l = sock.recv(1024)
# dumb while loop doesnt work
data = l
print data

rsa_key = RSA.importKey(data) # importing servers public key

# Generate AES key
BS = 16 # block size
pad = lambda s: s + (BS - len(s) % BS) * chr(BS - len(s) % BS)
unpad = lambda s: s[:-ord(s[len(s) - 1:])]

base64pad = lambda s: s + '=' * (4 - len(s) % 4)
base64unpad = lambda s: s.rstrip("=")
encrypt_key = keyGenAES(16)

# Encrypt AES key
enc_aes_key = rsa_key.encrypt(encrypt_key, 32)

# Send AES key
sock.sendall(enc_aes_key[0])
sock.sendall("done")

fileName = clientName + '.ovpn'
f = open(fileName, 'wb')

print >>sys.stderr, "Sent AES key"

# Receive the OVPN config data and write it to file
try:
    data = ""
    l = sock.recv(1024)
    while(l):
        print("Receiving chunk...")
        data += l
        l = sock.recv(1024)
    # decrypt data
    #test = new_key.decrypt(data)
    data = decrypt(encrypt_key, data)
    f.write(data)
    f.close()

finally:
    sock.close()

