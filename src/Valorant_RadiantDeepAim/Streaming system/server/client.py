import socket
import zlib
import numpy as np
import cv2

IP = '192.168.1.64'  # Adresse IP du serveur
PORT = 9000        # Port d'écoute du serveur

WIDTH = 640
HEIGHT = 640


def receive_image(server_socket):
    size_bytes = server_socket.recv(4)
    size = int.from_bytes(size_bytes, byteorder='big')
    received_data = b''
    while len(received_data) < size:
        data = server_socket.recv(size - len(received_data))
        if not data:
            break
        received_data += data
    img_data = zlib.decompress(received_data)
    img_np = np.frombuffer(img_data, dtype=np.uint8)
    img = cv2.imdecode(img_np, flags=cv2.IMREAD_COLOR)
    cv2.imshow('Image', img)
    cv2.waitKey(1)
    server_socket.send('ok'.encode())



def main():
    # Create a socket
    client_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    client_socket.connect((IP, PORT))

    print("Connected to server.")

    while True:
        # Receive and display the image from the server
        receive_image(client_socket)

    # Close the connection
    client_socket.close()


if __name__ == '__main__':
    main()
