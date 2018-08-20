import socket
import sys
import subprocess
from Crypto.PublicKey import RSA
import pickle

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

print >>sys.stderr, "waiting for key..."
# receive public key
publicKey = ""
data = connection.recv(1024)
print >>sys.stderr, "got part of it"
while(data != "done"):
    publicKey += data
    data = connection.recv(1024)
    print >>sys.stderr, "..."
print >>sys.stderr, "received key..."

print >>sys.stderr, publicKey

# call the docker command to get .OVPN config
# docker run --volumes-from $OVPN-DATA --rm kylemanna/openvpn ovpn_getclient $CLIENT > $CLIENT.ovpn
bashCmd = 'sudo docker run --volumes-from ' + vpnName + ' --rm kylemanna/openvpn ovpn_getclient ' + clientName
process = subprocess.Popen(bashCmd.split(), stdout=subprocess.PIPE)
vpnConf, error = process.communicate()

# encrypt output with publicKey
rsa_key = RSA.importKey(publicKey)
#rsa_key = PKCS1_OAEP.new(rsa_key)
vpnConf += ""
encConf = rsa_key.encrypt(str(vpnConf), 32) # 32 should be a random number

#print vpnConf
#print "length: " + str(len(encConf))
#print "=== VPN CONFIG ==="
#print vpnConf
thingy = "abcdefghijk"
encConf = rsa_key.encrypt(thingy, 32)
print encConf
#encConf = encConf[0]
#print "=== 0 ==="
#print encConf

try:
    print >>sys.stderr, 'connection from', client_address
    #for thing in encConf:
    connection.sendall(pickle.dumps(encConf)) # send the .ovpn config data
    print >>sys.stderr, 'Finished sending data to the client'
finally:
    # Clean up the connection
    connection.shutdown(socket.SHUT_WR) # let client know that no more data will be sent
    connection.close()
