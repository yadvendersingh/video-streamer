# Video Streamer [🔗](https://github.com/yadvendersingh/video-streamer.git)

## Overview
Video-streamer is a lightweight Python library designed for efficient point-to-point video streaming. It enables seamless transmission of video content from a source device to a destination with minimal setup and configuration.

## Features
- TCP socket-based video streaming
- Support for both camera feeds and video file streaming
- Configurable frame resolution, quality, and FPS
- Optional grayscale conversion to reduce bandwidth
- Frame resizing options for bandwidth optimization
- Simple client-server architecture

## Installation
```bash
# Clone the repository
git clone https://github.com/yadvendersingh/video-streamer.git
cd video-streamer

# Install dependencies
pip install opencv-python numpy
```

## Requirements
- Python 3.7+
- OpenCV
- Socket
- Pickle
- Struct

## Usage

### Setting up the receiver
```
refer sample_code_for_receiver.py
```

### Setting up the sender
```
refer sample_code_for_sender.py
```

## Configuration Options

### VideoSender
- `server_ip` - IP address of the receiving server
- `send_port` - Port for sending video frames
- `camera_index` - Index of the camera device (default: 0)
- `width` - Width of the frame (default: 640)
- `height` - Height of the frame (default: 480)
- `resize_ratio` - Factor to resize frames (default: None)
- `grayscale` - Convert to grayscale to save bandwidth (default: False)
- `fps` - Frames per second (default: 30)
- `restore_at_server` - Enable frame interpolation at server (default: False)
- `camera_running` - Using camera as source (default: False)

### VideoReceiver
- `host` - Host address for the server (default: '0.0.0.0')
- `receive_port` - Port for receiving video frames (default: 5556)

## Development Status

**Note: This project is still under active development.**

### Future
1. **Video Restoration at Receiver**: Integration with VFIMamba for frame interpolation and quality enhancement
2. **Encryption**: Secure video transmission with end-to-end encryption
3. **Additional Transport Protocols**: 
   - Message queue-based transmission
   - Multipoint streaming support
   - WebRTC integration
4. **Advanced Compression**: Adaptive video compression based on network conditions
5. **Web Interface**: Browser-based monitoring and control panel

## License
This project is licensed under the Apache 2.0 License - see the LICENSE file for details.