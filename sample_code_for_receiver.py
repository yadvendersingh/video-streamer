from receive import VideoReceiver
import cv2


server = VideoReceiver(host='0.0.0.0', receive_port=5555)
fourcc = cv2.VideoWriter_fourcc(*'XVID')
out = cv2.VideoWriter('./data/output.avi', fourcc, server.fps, (server.frame_width, server.frame_height))
for frame,original in server.receive_frames():
    if frame is None:
        print("No frame received.")
        break
    # cv2.imshow("Frame", frame)
    out.write(frame)
    
# cv2.destroyAllWindows()
out.release()