# TCP Reverse Shell

## Overview

a simple example for reverse shell script. <br/>

once the victim runs the client script, we're expecting to receive a reverse TCP connection on port 8080. <br/>

Then, after completing the TCP three-way handshake, we can send certain shell commands to the victim/target, <br/>

make the victim execute them, and get the result back to us. <br/>

## Features

*   <b>Navigation</b> - Navigate and list files through target file system.
*   <b>Shell Commands</b> - Execute shell commands on target system.
*   <b>Download files</b> - Download files using `grab` command.

## Usage

Change server ip address on client and server scripts to the correct address. <br/>
Make sure to run server script before running client script on target machine. <br/>
once a client connects to the server a shell will be opened. <br/>
use `cd` command to navigate target file system. <br/>
use `grab` command to download target files. <br/>

## License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.
