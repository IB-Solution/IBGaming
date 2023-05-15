import mss
import torch
import cv2 as cv
import numpy as np
from time import time, sleep
from socket import socket
from zlib import decompress
import pygame

x0, y0, _, _ = (0,0,0,0)
x_corr = 8
y_corr = 31
w, h = 640, 640


def Screen_Shot(left=0, top=0, width=1920, height=1080):
	stc = mss.mss()
	scr = stc.grab({
		'left': left,
		'top': top,
		'width': width,
		'height': height
	})

	img = np.array(scr)
	img = cv.cvtColor(img, cv.IMREAD_COLOR)

	return img


model_file_path = 'best.engine'
# model_file_path = 'best.pt'
model = torch.hub.load('ultralytics/yolov5', 'custom', path=model_file_path, force_reload=True)
model.cuda()
model.multi_label = False


classes = ["ennemy","ennemy head"]

loop_time = time()
while(True):
	loop_time = time()
	screenshot = Screen_Shot(x0 + x_corr, y0 + y_corr, w, h)
	screenshot = cv.cvtColor(screenshot, cv.COLOR_BGR2RGB)
	
	results = model(screenshot.copy())

	labels, cord = results.xyxyn[0][:, -1].cpu().numpy(), results.xyxyn[0][:, :-1].cpu().numpy()
	
	print("FPS {}".format(1.0 / (time() - loop_time)))
	n = len(labels)

	for i in range(n):
		row = cord[i]
		if row[4] >= 0.65:
			x1, y1, x2, y2 = int(row[0] * w), int(row[1] * h), int(row[2] * w), int(row[3] * h)
			bgr = (0, 255, 0)
			cv.rectangle(screenshot, (x1, y1), (x2, y2), bgr, 2)
			cv.putText(screenshot, classes[int(labels[i])], (x1, y1), cv.FONT_HERSHEY_SIMPLEX, 0.9, bgr, 2)

	screenshot = cv.cvtColor(screenshot, cv.COLOR_RGB2BGR)
	cv.imshow("YOLOv5", screenshot)

	key = cv.waitKey(1)
	if key == ord("q"):
		cv.destroyAllWindows()
		break