#!/usr/bin/env python3
import rclpy
from rclpy.node import Node
from kenneth_interfaces.msg import LanguageInstruction

class LanguagePublisherNode(Node):
    def __init__(self):
        super().__init__('language_publisher_node')

        self.publisher = self.create_publisher(
            LanguageInstruction,
            '/language_instruction',
            10
        )

        # Publish every 0.1 seconds (10Hz)
        self.timer = self.create_timer(0.1, self.publish_language)

        self.get_logger().info('\033[92mLanguage Publisher Node Started!\033[0m')

    def publish_language(self):
        msg = LanguageInstruction()
        msg.task_name = "webcam_recording"
        msg.action_text = "Record objects in front of the camera"
        msg.init_scene_text = "Camera is pointing at the workspace"
        msg.skill = "Record"
        msg.environment_config = "fps=20, cameras=2"

        self.publisher.publish(msg)

def main(args=None):
    rclpy.init(args=args)
    node = LanguagePublisherNode()
    rclpy.spin(node)
    rclpy.shutdown()

if __name__ == '__main__':
    main()
