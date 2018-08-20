import socket
import sys
import subprocess

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

# call the docker command to get .OVPN config
# docker run --volumes-from $OVPN-DATA --rm kylemanna/openvpn ovpn_getclient $CLIENT > $CLIENT.ovpn
bashCmd = 'sudo docker run --volumes-from ' + vpnName + ' --rm kylemanna/openvpn ovpn_getclient ' + clientName
process = subprocess.Popen(bashCmd.split(), stdout=subprocess.PIPE)
output, error = process.communicate()

try:
    print >>sys.stderr, 'connection from', client_address
    connection.sendall(output) # send the .ovpn config data
    print >>sys.stderr, 'Finished sending data to the client'
finally:
    # Clean up the connection
    connection.shutdown(socket.SHUT_WR) # let client know that no more data will be sent
    connection.close()

