import socket
import sys
import subprocess
from Crypto.PublicKey import RSA
from base64 import urlsafe_b64encode, urlsafe_b64decode
from Crypto.Cipher import AES
from Crypto import Random

# Create a TCP/IP socket
sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)

# Bind the socket to the port
server_address = ('10.142.0.4', 8090)
print >>sys.stderr, 'starting up on %s port %s' % server_address
sock.bind(server_address)

# Listen for incoming connections
sock.listen(1)

# Wait for a connection
print >>sys.stderr, 'waiting for a connection'
connection, client_address = sock.accept()

vpnName = connection.recv(1024)
clientName = connection.recv(1024)
print >>sys.stderr, 'vpn:', vpnName
print >>sys.stderr, 'client:', clientName

# Generate 4096 bit RSA keys
print >>sys.stderr, "Generating RSA Keys..."
rsa_key = RSA.generate(4096, e=65537)
private_key = rsa_key.exportKey("PEM")
public_key = rsa_key.publickey().exportKey("PEM")
print >>sys.stderr, "Created Keys..."

# Send public key to client
print >>sys.stderr, "Sending Public Key..."
connection.sendall(public_key)
print >>sys.stderr, "Sent Public Key..."

print >>sys.stderr, "waiting for AES key..."
# receive encrypted AES key
aesKey = ""
data = connection.recv(1024)
print >>sys.stderr, "got part of it"
while(data != "done"):
    aesKey += data
    data = connection.recv(1024)
    print >>sys.stderr, "..."
print >>sys.stderr, "received AES key..."

# decrypt AES key with private key
aesKey = rsa_key.decrypt(aesKey)

print >>sys.stderr, aesKey

# call the docker command to get .OVPN config
# docker run --volumes-from $OVPN-DATA --rm kylemanna/openvpn ovpn_getclient $CLIENT > $CLIENT.ovpn
bashCmd = 'sudo docker run --volumes-from ' + vpnName + ' --rm kylemanna/openvpn ovpn_getclient ' + clientName
process = subprocess.Popen(bashCmd.split(), stdout=subprocess.PIPE)
vpnConf, error = process.communicate()

# encrypt output with aesKey
BS = 16 # block size
pad = lambda s: s + (BS - len(s) % BS) * chr(BS - len(s) % BS)
unpad = lambda s: s[:-ord(s[len(s) - 1:])]

base64pad = lambda s: s + '=' * (4 - len(s) % 4)
base64unpad = lambda s: s.rstrip("=")
encrypt_key = aesKey

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

# Encrypted VPN conf
encVpnConf = encrypt(encrypt_key, vpnConf)

try:
    print >>sys.stderr, 'connection from', client_address
    connection.sendall(encVpnConf) # send the .ovpn config data
    print >>sys.stderr, 'Finished sending data to the client'
finally:
    # Clean up the connection
    connection.shutdown(socket.SHUT_WR) # let client know that no more data will be sent
    connection.close()
