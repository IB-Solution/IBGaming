import socket
import zlib
from mss import mss
import numpy as np
import cv2

IP = '192.168.1.64'  # Adresse IP du serveur
PORT = 9000        # Port d'écoute du serveur

X, Y, W, H = (100, 0, 1920, 1080)
# X, Y, W, H = (0, 0, 2560, 1440)
WIDTH, HEIGHT = (640 ,640)


def send_image(client_socket, image):
    # Compress the image using zlib
    _, img_encoded = cv2.imencode('.png', image)
    compressed_data = zlib.compress(img_encoded, level=9)

    # Send the image size first
    size = len(compressed_data)
    size_bytes = size.to_bytes(4, byteorder='big')
    client_socket.send(size_bytes)

    # Send the compressed image data
    client_socket.sendall(compressed_data)

    message = client_socket.recv(1024).decode()
    print("Received message from client:", message)



def main():
    # Create a socket
    server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    server_socket.bind((IP, PORT))
    server_socket.listen(1)

    print("Server started. Waiting for client connection...")

    # Accept a client connection
    client_socket, addr = server_socket.accept()
    print("Client connected:", addr)

    # Initialize screen capture
    with mss() as sct:
        rect = {'top': X, 'left': Y, 'width': W, 'height': H}

        while True:
            # Capture the screen
            img = np.array(sct.grab(rect))

            # Resize
            resized_img = cv2.resize(img, (WIDTH, HEIGHT))
            
            # Send the image to the client
            send_image(client_socket, resized_img)

    # Close the connection
    client_socket.close()
    server_socket.close()


if __name__ == '__main__':
    main()
