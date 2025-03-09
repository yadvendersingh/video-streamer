# LAPTOP CLIENT CODE (client.py)
import cv2
import socket
import pickle
import struct

class VideoSender:
    def __init__(self, server_ip='0.0.0.0', 
                 send_port=5556, 
                 camera_index=0, 
                 width=640, 
                 height=480, 
                 resize_ratio=None, 
                 grayscale=False, 
                 fps=30, 
                 restore_at_server=False, 
                 camera_running=False, 
                 establish_connection = True):
        self.server_ip = server_ip
        self.send_port = send_port
        self.camera_index = camera_index
        self.send_socket = None
        self.frame_width = width
        self.frame_height = height
        self.resize_ratio = resize_ratio
        self.grayscale = grayscale
        self.fps = fps
        self.frame_interval = 1 / self.fps
        self.frame_counter = 0
        self.camera_running = camera_running
        self.restore_at_server = restore_at_server
        if establish_connection:
            if not self.connect_to_server():
                raise Exception("Failed to connect to server")
        
    def start_camera(self):
        self.cap = cv2.VideoCapture(self.camera_index)
        if not self.cap.isOpened():
            raise Exception("Could not open video device")
        # Set resolution to reduce bandwidth
        self.cap.set(cv2.CAP_PROP_FRAME_WIDTH, self.frame_width)
        self.cap.set(cv2.CAP_PROP_FRAME_HEIGHT, self.frame_height)
        return self.cap.isOpened()
        
    def connect_to_server(self):
        # Socket for sending frames
        print(f"Connecting to server at {self.server_ip}")
        self.send_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        
        try:
            self.send_socket.connect((self.server_ip, self.send_port))
            print(f"Connected to server at {self.server_ip}")
            # Send initial properties to the server
            properties = {
                'frame_width': self.frame_width,
                'frame_height': self.frame_height,
                # 'resize_ratio': self.resize_ratio,
                'fps': self.fps,
                'restore_at_server': self.restore_at_server,
                'camera_running': self.camera_running,
                'grayscale': self.grayscale
            }
            properties_data = pickle.dumps(properties)
            properties_size = struct.pack("L", len(properties_data))
            self.send_socket.sendall(properties_size + properties_data)
            return True
        except ConnectionRefusedError:
            print(f"Connection refused by server at {self.server_ip}:{self.send_port}")
            return False
        except Exception as e:
            print(f"Connection error: {e}")
            return False
        
    def send_frame(self, frame):
        # Compress frame to reduce bandwidth
        
        # start_time = time.time()
        if self.frame_counter % (30//self.fps)  == 0:
            if self.resize_ratio:
                frame = cv2.resize(frame, None, fx=self.resize_ratio, fy=self.resize_ratio)
            elif not self.camera_running:
                frame = cv2.resize(frame, (self.frame_width, self.frame_height))
            if self.grayscale:
                frame = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
            
            # Encode the frame
            _, encoded_frame = cv2.imencode('.jpg', frame, [cv2.IMWRITE_JPEG_QUALITY, 80])
            data = pickle.dumps(encoded_frame)
            
            # Send frame size followed by frame data
            message_size = struct.pack("L", len(data))
            try:
                self.send_socket.sendall(message_size + data)
            except (ConnectionResetError, BrokenPipeError) as e:
                print(f"Connection error: {e}")
                self.camera_running = False
        self.frame_counter+=1
        # processing_time = time.time() - start_time
        # sleep_time = max(0, self.frame_interval - processing_time)
        # time.sleep(sleep_time)
        # Check for key press to stop the client
        key = cv2.waitKey(1)
        if key == ord('Q'):  # Shift + q
            self.camera_running = False
    
    def send_camera_feed(self):
        self.camera_running = True
        if self.start_camera():
            while self.camera_running:
                ret, frame = self.cap.read()
                if not ret:
                    print("Failed to capture frame")
                    self.camera_running = False
                    break
                self.send_frame(frame)
            self.cleanup()
        else:
            print("Failed to initialize camera")

    def cleanup(self):
        self.running = False
        if hasattr(self, 'cap') and self.cap is not None:
            self.cap.release()
        if self.send_socket:
            self.send_socket.close()
        print("Client shutdown complete")