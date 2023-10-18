from time import time
import mss
import cv2 as cv
import numpy as np
from win32gui import FindWindow, GetWindowRect, SetForegroundWindow

window_handle = FindWindow(None, "Albion Online Client")
window_rect   = GetWindowRect(window_handle)
SetForegroundWindow(window_handle)

x0, y0, _, _ = window_rect
x_corr = 8
y_corr = 31
w, h = 1920, 1080

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


while (True):
    
    screenshot = Screen_Shot(x0 + x_corr, y0 + y_corr, w, h)
    
    cv.imshow("Screenshot", screenshot)

    loop_time = time()

    key = cv.waitKey(1)
    if key == ord("q"):
        cv.destroyAllWindows()
        break
    elif key == ord('f'):
        print("[INFO] Screenshot taken...")
        cv.imwrite('screenshots/{}.jpg'.format(loop_time), screenshot)

print("[INFO] Done.")