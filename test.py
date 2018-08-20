from Crypto.PublicKey import RSA
from Crypto import Random
random_generator = Random.new().read
key = RSA.generate(1024, random_generator)

public_key = key.publickey().exportKey("PEM")
test = RSA.importKey(public_key)


enc_data = test.encrypt('abcdefgh', 32)
print enc_data

print key.decrypt(enc_data)


f = open('PHONE.ovpn', 'rb')
vpnConf = f.read()
#print vpnConf

#encr = test.encrypt(vpnConf, 32)
#print encr
#print key.decrypt(encr)

from Crypto.Cipher import AES

obj = AES.new('This is a key123', AES.MODE_CBC, 'This is an IV456')
cipher_text = obj.encrypt("The answer is no")
print cipher_text

obj2 = AES.new('This is a key123', AES.MODE_CBC, 'This is an IV456')
plain_text = obj2.decrypt(cipher_text)
print plain_text

