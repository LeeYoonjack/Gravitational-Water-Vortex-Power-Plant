from venv import create
import numpy as np
import cv2
import os

# Reduces the size of the video displayed
def rescaleFrame(frame, scale=0.5):
    width = int(frame.shape[1] * scale)
    height = int(frame.shape[0] * scale)
    dimensions = (width, height)

    return cv2.resize(frame, dimensions, interpolation=cv2.INTER_AREA)

# Tracks the moving blade
tracker = cv2.TrackerKCF_create()

cap = cv2.VideoCapture("File Path to the video")

# Gets the fps of the video
fps = int(cap.get(cv2.CAP_PROP_FPS))

success, img = cap.read()
frame_resized = rescaleFrame(img)

roi = cv2.selectROI(frame_resized, False)

success = tracker.init(frame_resized, roi)
object_detector = cv2.createBackgroundSubtractorMOG2()

total_frames = []
array1 = []
array2 = []
frames = 0
f = 1

while True:
    frames += 1
    success, img = cap.read()
    frame_resized = rescaleFrame(img)

    success, roi = tracker.update(frame_resized)

    if frames < 201:
        if success:
            (x, y, w, h) = [int(v) for v in roi]
            cv2.rectangle(frame_resized, (x, y), (x + w, y + h), (0, 255, 0), 2, 1)

            height_a = y - 25
            width_a = y - 20

            new_height = x + 25
            new_width = x + 20

            area1 = [(width_a, height_a), (new_width, height_a), (new_width, new_height), (width_a, new_height)]

            for area in [area1]:
                cv2.polylines(frame_resized, [np.array(area, np.int32)], True, (0, 220, 0), 2)

            check_in_roi = cv2.pointPolygonTest(np.array(area1, np.int32), (x, y), False)

            if check_in_roi == 1:
                total_frames.append(frames)

            for i in total_frames:
                if i == f:
                    array1.append(i)
                    f += 1
                elif i > f:
                    array2.append(i)
                    f = i + 1
    else:
        break

    cv2.imshow("Frame", frame_resized)

    key = cv2.waitKey(30)
    if key == 27:
        break

# Calculates frames per rotation
fpr = ((array2[2] - array2[0]) + (array2[3] - array2[1]) + (array2[4] - array2[2]) + (array2[5] - array2[3])) / 4
rounded_fpr = "{:.1f}".format(fpr)
# Finds revolutions per minute
rpm = float((fps / fpr) * 60)
rounded_rpm = "{:.2f}".format(rpm)
print(
    "In this " + str(fps) + " fps video, the blade completes a full rotation every " + rounded_fpr + " frames. The blade has " + rounded_rpm + " revolutions per minute.")

cap.release()
cv2.destroyAllWindows()
