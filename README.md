# CN-Reliable-UDP
Reliable UDP implementation, for CS F303 Computer Networks

## Group:  
Ekanshi Agrawal - 2017A7PS0233H  
Kushagra Srivastava - 2017A7PS0146H  
Sandesh Thakar  - 2017A7PS0181H  
Kunal Verma - 2017A7PS0120H  

# How to run:
Open two terminals.  
- On one terminal, type the command `python3 server.py -ip <ip-address> -p <port>`
- On another termincal, type the command `python3 client.py -ip <ip-address> -p <port>`

These two are the server and client terminals respectively. Make sure that the Address and port number entered in the two are the same. This will be the address of the server. The client will be prompted to enter a filename that it wants from the server. The file will be saved as `<filename>_client_copy.<extension>` once the transfer is successful.

# Libraries
The following python libraries are required:
'''
socket
datetime
time
hashlib
argparse
os
'''

