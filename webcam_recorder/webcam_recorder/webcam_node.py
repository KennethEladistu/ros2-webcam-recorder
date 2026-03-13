#!/usr/bin/env python3
import rclpy
from rclpy.node import Node
from kenneth_interfaces.msg import CameraData
from sensor_msgs.msg import Image
from cv_bridge import CvBridge
import threading
import sys
sys.path.insert(0, '/home/mailroom/dev_ws/install/my_yolo_pkg/lib/python3.12/site-packages')
from my_yolo_pkg.submodule.oak_cam import OakDProDevice

OD_MXID  = '18443010D1AEAC0F00'  # USB
OCR_MXID = '14442C1051231BD000'  # PoE

class CameraNode(Node):
    def __init__(self):
        super().__init__('camera_node')
        self.br = CvBridge()

        # Publishers
        self.publisher_od  = self.create_publisher(CameraData, '/camera/od/camera_data', 10)
        self.publisher_ocr = self.create_publisher(CameraData, '/camera/ocr/camera_data', 10)

        # Frames
        self.od_frame  = None
        self.od_depth  = None
        self.ocr_frame = None
        self.od_lock   = threading.Lock()
        self.ocr_lock  = threading.Lock()

        # Start both cameras in separate threads
        self.od_thread  = threading.Thread(target=self.od_stream,  daemon=True)
        self.ocr_thread = threading.Thread(target=self.ocr_stream, daemon=True)
        self.od_thread.start()
        self.ocr_thread.start()

        self.get_logger().info('\033[92mCamera Node Starting...\033[0m')
        self.timer = self.create_timer(0.05, self.publish_frames)  # 20fps

    def od_stream(self):
        cam = OakDProDevice(mxid=OD_MXID, ocr=False)
        self.get_logger().info('\033[92mOD Camera Ready!\033[0m')
        while rclpy.ok():
            rgb, _, depth = cam.run()
            with self.od_lock:
                self.od_frame = rgb
                self.od_depth = depth

    def ocr_stream(self):
        cam = OakDProDevice(mxid=OCR_MXID, ocr=True)
        self.get_logger().info('\033[92mOCR Camera Ready!\033[0m')
        while rclpy.ok():
            rgb, _, _ = cam.run()
            with self.ocr_lock:
                self.ocr_frame = rgb

    def make_camera_data(self, rgb_frame, frame_id, now):
        msg = CameraData()
        rgb_img = self.br.cv2_to_imgmsg(rgb_frame, encoding='bgr8')
        rgb_img.header.stamp = now
        rgb_img.header.frame_id = frame_id
        msg.rgb_image = rgb_img
        depth_img = Image()
        depth_img.header.stamp = now
        depth_img.header.frame_id = frame_id
        depth_img.encoding = '16UC1'
        msg.depth_image = depth_img
        return msg

    def publish_frames(self):
        now = self.get_clock().now().to_msg()

        # OD Camera
        with self.od_lock:
            od_frame = self.od_frame.copy() if self.od_frame is not None else None
        if od_frame is not None:
            self.publisher_od.publish(self.make_camera_data(od_frame, 'od_frame', now))
            self.get_logger().info('OD frame published', once=True)

        # OCR Camera
        with self.ocr_lock:
            ocr_frame = self.ocr_frame.copy() if self.ocr_frame is not None else None
        if ocr_frame is not None:
            self.publisher_ocr.publish(self.make_camera_data(ocr_frame, 'ocr_frame', now))
            self.get_logger().info('OCR frame published', once=True)

    def destroy_node(self):
        super().destroy_node()

def main(args=None):
    rclpy.init(args=args)
    node = CameraNode()
    rclpy.spin(node)
    node.destroy_node()
    rclpy.shutdown()

if __name__ == '__main__':
    main()
