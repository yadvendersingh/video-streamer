from collections import deque
import cv2
import socket
import pickle
import struct
# import numpy as np
import sys
# from VFIMamba.vfimamba import VFIMamba

sys.path.append('.')

class VideoReceiver:
    def __init__(self, host='0.0.0.0', receive_port=5556, initialize_server=True):
        self.host = host
        self.receive_port = receive_port
        self.client_socket = None
        self.addr = None
        self.grayscale = False
        self.frame_width = 640
        self.frame_height = 480
        self.fps = 30
        self.restore_at_server = False
        self.camera_running = False
        self.vfimamba = None
        self.frames_received = deque()
        if initialize_server:
            self.setup_server()

    def setup_server(self):
        # Socket for receiving frames
        self.receive_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.receive_socket.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
        self.receive_socket.bind((self.host, self.receive_port))
        self.receive_socket.listen(5)
        
        print(f"Server started on {self.host}.")
        print(f"Receiving on port {self.receive_port}")
        self.client_socket, self.addr = self.receive_socket.accept()
        print(f"Connection from {self.addr}")
        
        # Receive properties first
        self.receive_properties()
        print("Properties received")
        print(f"Frame width: {self.frame_width}")
        print(f"Frame height: {self.frame_height}")
        print(f"Grayscale: {self.grayscale}")
        print(f"fps: {self.fps}")
        print(f"Restore at server: {self.restore_at_server}")
        print(f"Camera running: {self.camera_running}")
        return True
    
    def receive_properties(self):
        # Receive size of the properties data
        properties_size_data = self.client_socket.recv(struct.calcsize("L"))
        properties_size = struct.unpack("L", properties_size_data)[0]
        
        # Receive properties data
        properties_data = b""
        while len(properties_data) < properties_size:
            packet = self.client_socket.recv(min(properties_size - len(properties_data), 4096))
            if not packet:
                return None
            properties_data += packet
            
        # Unpack properties
        self.frame_properties = pickle.loads(properties_data)
        print(f"Received properties: {self.frame_properties}")
        
        # Extract the properties
        self.frame_width = self.frame_properties.get('frame_width', 640)
        self.frame_height = self.frame_properties.get('frame_height', 480)
        self.fps = self.frame_properties.get('fps', None)
        self.restore_at_server = self.frame_properties.get('restore_at_server', False)
        self.grayscale = self.frame_properties.get('grayscale', False)
        self.camera_running = self.frame_properties.get('camera_running', False)
        # if self.restore_at_server and self.fps<30:
        #     self.vfimamba = VFIMamba(n=30//self.fps)
        #     # Create a black image with the specified frame height and width
        #     black_image = np.zeros((self.frame_height, self.frame_width, 3), dtype=np.uint8)
        #     self.frames_received.append(black_image)
    
    def receive_frames(self):
        receive_conn = self.client_socket
        data = b""
        payload_size = struct.calcsize("L")
        
        while True:
            try:
                # Receive message size
                while len(data) < payload_size:
                    packet = receive_conn.recv(4096)
                    if not packet:
                        return
                    data += packet
                
                # Extract message size
                packed_msg_size = data[:payload_size]
                data = data[payload_size:]
                msg_size = struct.unpack("L", packed_msg_size)[0]
                
                # Receive frame data
                while len(data) < msg_size:
                    data += receive_conn.recv(4096)
                
                # Extract frame
                frame_data = data[:msg_size]
                data = data[msg_size:]
                
                # Decode the frame
                encoded_frame = pickle.loads(frame_data)
                frame = cv2.imdecode(encoded_frame, cv2.IMREAD_COLOR)
                
                # Process the frame
                processed_frame = self.process_frame(frame)
                # Yield the processed frame
                for idx, processed_frame in enumerate(processed_frame):
                    if idx == 0 or idx == (30//self.fps)-1:
                        yield processed_frame, True
                    else:
                        yield processed_frame, False
                
            except Exception as e:
                print(f"Error receiving frames: {e}")
                break
        self.cleanup()
    
    def process_frame(self, frame):
        # Currently under development
        # if self.restore_at_server:
        #     if self.grayscale:
        #         frame = cv2.cvtColor(frame, cv2.COLOR_GRAY2BGR)
        #     self.frames_received.append(frame)
        #     clip = self.vfimamba.process_frames(self.frames_received.popleft(), self.frames_received[0])
        #     return clip
        # else:
        return [frame]
        
    
    def cleanup(self):
        try:
            self.client_socket.close()
            self.addr.close()
        except:
            pass
        
        # Close server sockets
        if hasattr(self, 'receive_socket'):
            self.receive_socket.close()
        
        print("Server shutdown complete")