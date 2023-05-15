import socket
import zlib
import numpy as np
import cv2
import torch
import numpy as np
from time import time, sleep

WIDTH, HEIGHT = (640 ,640)
# WIDTH, HEIGHT = (1080 ,1080)

HOST = '192.168.1.64'  # Adresse IP du serveur
PORT = 9000        # Port d'écoute du serveur

global client_socket

model_file_path = 'best.engine'
# model_file_path = 'best.pt'
model = torch.hub.load('ultralytics/yolov5', 'custom', path=model_file_path, force_reload=True)
model.cuda()
model.multi_label = False
classes = ["ennemy","ennemy head"]




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
    return img







client_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
client_socket.connect((HOST, PORT))
print("Connecting to server...")
while True:
    img = receive_image(client_socket)
    loop_time = time()
    results = model(img.copy())
    labels, cord = results.xyxyn[0][:, -1].cpu().numpy(), results.xyxyn[0][:, :-1].cpu().numpy()
    print("FPS {}".format(1.0 / (time() - loop_time)))

    client_socket.send('ok'.encode())

    n = len(labels)
    for i in range(n):
        row = cord[i]
        if row[4] >= 0.65:
            x1, y1, x2, y2 = int(row[0] * WIDTH), int(row[1] * HEIGHT), int(row[2] * WIDTH), int(row[3] * HEIGHT)
            bgr = (0, 255, 0)
            cv2.rectangle(img, (x1, y1), (x2, y2), bgr, 2)
            cv2.putText(img, classes[int(labels[i])], (x1, y1), cv2.FONT_HERSHEY_SIMPLEX, 0.9, bgr, 2)

    img = cv2.cvtColor(img, cv2.COLOR_RGB2BGR)
    cv2.imshow("YOLOv5", img)

    key = cv2.waitKey(1)
    if key == ord("q"):
        cv2.destroyAllWindows()
        break
client_socket.close()
