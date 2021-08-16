# TCP Reverse Shell

## Overview

a simple example for tcp reverse shell script. <br/>

once the victim runs the client script, we're expecting to receive an encrypted reverse TCP connection on port 8080. <br/>

Then, after completing the TCP three-way handshake, we can send certain shell commands to the victim/target, <br/>

make the victim execute them, and get the result back to us. <br/>

## Features

*   <b>Navigation</b> - Navigate and list files throgh target file system.
*   <b>Shell Commands</b> - Execute shell commands on target system.
*   <b>Download files</b> - Download files using `grab` command.
*   <b>Screenshoot</b> - Take target screen image using `screenshoot` command.
*   <b>Search</b> - Search for files using `search` command.
*   <b>Port Scanner</b> - check target for open ports using `scan` command.
*   <b>Keylogger</b> - check target keylogs by downloading 'keylogs.txt' from target file system.
*   <b>Hybrid Encryption</b> - all commuinication between target and server run through protected tunnel, the tunnel encrypted using AES symmetric algorithm with CTR mode and RSA asymmetric algorithm.
*   <b>Persistence</b> - script copy itself to target appdata folder, adding new registry key pointing to script location and waiting for server connection.

## Implementation

Client holds its own private key, and the server will holds the target's public key. <br/>
Once the TCP connection is started, the server will generate a random AES key and we will securely send this key to the target side.  <br/>
the transfer is encrypted via encrypting the random AES key with a target's public key. <br/>
At this point, both server and target machines have the same random generated AES keys which will be used for AES encryption. <br/>

To generate RSA key pair, you can use `rsa_generator.py` script. <br/>
run the script and it will generate `private.pem` and `public.pem` files.

## Usage

Change server ip address on client and server scripts to the correct address. <br/>
Make sure to run server script before running client script on target machine. <br/>
once a client connects to the server a shell will be opened. <br/>
use `cd` command to navigate target file system. <br/>
use `grab` command to download target files. <br/>
use `screenshoot` command to download target screen image. <br/>
use `search` command to search in target file system, ex: `search C://*.pdf`. <br/>
use `scan` command to scan target for open ports, ex: `scan 10.0.0.5:21,22,8080`. <br/>

## License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.