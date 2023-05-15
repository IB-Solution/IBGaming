import socket
import zlib
from mss import mss
import numpy as np
import cv2


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


def main():
    # Create a socket
    server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    server_socket.bind(('localhost', 8000))
    server_socket.listen(1)

    print("Server started. Waiting for client connection...")

    # Accept a client connection
    client_socket, addr = server_socket.accept()
    print("Client connected:", addr)

    # Initialize screen capture
    with mss() as sct:
        rect = {'top': 0, 'left': 0, 'width': 640, 'height': 640}

        while True:
            # Capture the screen
            img = np.array(sct.grab(rect))

            # Send the image to the client
            send_image(client_socket, img)

    # Close the connection
    client_socket.close()
    server_socket.close()


if __name__ == '__main__':
    main()
