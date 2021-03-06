import time

import cv2
import numpy as np
from pyzbar.pyzbar import decode

from src.media import MediaModel

cv2.namedWindow("frame", cv2.WINDOW_NORMAL)
cv2.resizeWindow("frame", 1920, 1080)
cv2.setWindowProperty("frame", cv2.WND_PROP_FULLSCREEN, cv2.WINDOW_FULLSCREEN)


cap = cv2.VideoCapture(0)
mediaModel = MediaModel()

startTime = time.time()
timeElapsed = 0
time_since_lost = 0
QRLost = True

blackground = np.zeros((1080, 1920, 1), dtype="uint8")
loadedNow = False


while True:
    ret, frame = cap.read()
    if frame is None:
        continue
    decoded = decode(frame)

    if mediaModel.mediaLoaded() and not loadedNow:
        mediaModel.update(timeElapsed)
    if loadedNow:
        loadedNow = False

    if len(decoded) > 0:
        QRLost = False
        data = decoded[0].data.decode()
        position = decoded[0].rect
        folder = f"data/{data}"

        if not mediaModel.isStillSame(folder):
            mediaModel.loadFolder(folder)
            loadedNow = True
    elif mediaModel.mediaLoaded() and not QRLost:
        time_since_lost = time.time()
        QRLost = True
    elif QRLost and time.time() - time_since_lost > 1.5:
        mediaModel.kill()

    if not mediaModel.mediaLoaded():
        cv2.imshow('frame', blackground)

    if cv2.waitKey(10) & 0xFF == ord('q'):
        break

    timeElapsed = time.time() - startTime
    startTime = time.time()


cap.release()
cv2.destroyAllWindows()
