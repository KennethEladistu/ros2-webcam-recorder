#!/usr/bin/env python3

import rclpy
from rclpy.node import Node
from robot_interfaces.msg import CameraData
from sensor_msgs.msg import Image
from cv_bridge import CvBridge
import cv2

class WebcamNode(Node):
    def __init__(self):
        super().__init__('webcam_node')

        self.br = CvBridge()

        # Camera 1 - A4ech
        self.cap1 = cv2.VideoCapture(4)
        # Camera 2 - Web Camera
        self.cap2 = cv2.VideoCapture(6)

        # Now publishing CameraData instead of Image
        self.publisher1 = self.create_publisher(CameraData, '/camera/a4ech/camera_data', 10)
        self.publisher2 = self.create_publisher(CameraData, '/camera/webcam/camera_data', 10)

        self.timer = self.create_timer(0.05, self.publish_frames)  # 20fps

        if not self.cap1.isOpened():
            self.get_logger().error('Could not open A4ech camera!')
        else:
            self.get_logger().info('\033[92mA4ech Camera Ready!\033[0m')

        if not self.cap2.isOpened():
            self.get_logger().error('Could not open Web Camera!')
        else:
            self.get_logger().info('\033[92mWeb Camera Ready!\033[0m')

    def publish_frames(self):
        now = self.get_clock().now().to_msg()

        # Camera 1 - A4ech
        ret1, frame1 = self.cap1.read()
        if ret1:
            rgb1 = self.br.cv2_to_imgmsg(frame1, encoding='bgr8')
            rgb1.header.stamp = now
            rgb1.header.frame_id = 'a4ech_frame'

            depth1 = Image()
            depth1.header.stamp = now
            depth1.header.frame_id = 'a4ech_frame'
            depth1.encoding = '16UC1'

            msg1 = CameraData()
            msg1.rgb_image = rgb1
            msg1.depth_image = depth1

            self.publisher1.publish(msg1)
            cv2.imshow('A4ech Camera', frame1)

        # Camera 2 - Webcam
        ret2, frame2 = self.cap2.read()
        if ret2:
            rgb2 = self.br.cv2_to_imgmsg(frame2, encoding='bgr8')
            rgb2.header.stamp = now
            rgb2.header.frame_id = 'webcam_frame'

            depth2 = Image()
            depth2.header.stamp = now
            depth2.header.frame_id = 'webcam_frame'
            depth2.encoding = '16UC1'

            msg2 = CameraData()
            msg2.rgb_image = rgb2
            msg2.depth_image = depth2

            self.publisher2.publish(msg2)
            cv2.imshow('Web Camera', frame2)

        cv2.waitKey(1)

    def destroy_node(self):
        self.cap1.release()
        self.cap2.release()
        cv2.destroyAllWindows()
        super().destroy_node()


def main(args=None):
    rclpy.init(args=args)
    node = WebcamNode()
    rclpy.spin(node)
    node.destroy_node()
    rclpy.shutdown()

if __name__ == '__main__':
    main()
