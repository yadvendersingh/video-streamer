from send import VideoSender
import cv2

video_file = "./data/video.mp4"

if video_file=="":
    video_sender = VideoSender(server_ip='0.0.0.0', send_port=5555,camera_running=True, fps=10)
    video_sender.send_camera_feed()
else:
    video_sender = VideoSender(server_ip='0.0.0.0', send_port=5555,camera_running=False, fps=15)
    cap = cv2.VideoCapture(video_file)
    while cap.isOpened():
        ret, frame = cap.read()
        if not ret:
            break
        video_sender.send_frame(frame)
    cap.release()