"""
PCMMS Pendel-Tracker
Verfolgt roten Marker in Video und speichert Positionen als CSV.
"""

import cv2
import numpy as np
import csv
import sys
from collections import deque

def track_red_marker(video_path, output_csv="tracking_data.csv", smoothing=5):
    cap = cv2.VideoCapture(video_path)
    if not cap.isOpened():
        print(f"Fehler: Video {video_path} konnte nicht geöffnet werden.")
        sys.exit(1)

    fps = cap.get(cv2.CAP_PROP_FPS)
    print(f"Video: {video_path} ({fps:.2f} FPS)")

    positions = deque(maxlen=smoothing)

    with open(output_csv, 'w', newline='') as f:
        writer = csv.writer(f)
        writer.writerow(["frame", "time_sec", "x", "y", "x_smoothed", "y_smoothed"])

        frame_idx = 0
        while True:
            ret, frame = cap.read()
            if not ret:
                break

            hsv = cv2.cvtColor(frame, cv2.COLOR_BGR2HSV)
            mask1 = cv2.inRange(hsv, np.array([0, 120, 70]), np.array([10, 255, 255]))
            mask2 = cv2.inRange(hsv, np.array([170, 120, 70]), np.array([180, 255, 255]))
            mask = mask1 | mask2

            mask = cv2.erode(mask, None, iterations=2)
            mask = cv2.dilate(mask, None, iterations=2)

            contours, _ = cv2.findContours(mask, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
            if contours:
                c = max(contours, key=cv2.contourArea)
                ((x, y), radius) = cv2.minEnclosingCircle(c)
                if radius > 4:
                    positions.append((x, y))
                    if len(positions) == smoothing:
                        xs, ys = zip(*positions)
                        x_s = sum(xs) / smoothing
                        y_s = sum(ys) / smoothing
                        time_sec = frame_idx / fps
                        writer.writerow([frame_idx, f"{time_sec:.3f}", f"{x:.2f}", f"{y:.2f}", f"{x_s:.2f}", f"{y_s:.2f}"])
                        print(f"Frame {frame_idx}: x={x_s:.1f}, y={y_s:.1f}")
            frame_idx += 1

    cap.release()
    print(f"Tracking abgeschlossen. {frame_idx} Frames. CSV: {output_csv}")

if __name__ == "__main__":
    if len(sys.argv) != 2:
        print("Verwendung: python pcmms_pendel_tracker.py <video.mp4>")
    else:
        track_red_marker(sys.argv[1])
