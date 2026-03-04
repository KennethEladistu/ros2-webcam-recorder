#!/usr/bin/env python3
import rclpy
from rclpy.node import Node
from rclpy.serialization import serialize_message
from robot_interfaces.msg import CameraData
from robot_interfaces.msg import LanguageInstruction
from sensor_msgs.msg import JointState
import rosbag2_py
import os
import uuid
import json
from datetime import datetime

class NewBagRecorderNode(Node):
    def __init__(self):
        super().__init__('new_bag_recorder_node')

        bag_name = 'webcam_bags'
        os.makedirs(bag_name, exist_ok=True)

        current_time = datetime.now()
        self.episode_id = str(uuid.uuid1())
        unique_bag_name = "{month}-{day}-{year}-{time_now}-{unique_id}".format(
            month=current_time.month,
            day=current_time.day,
            year=current_time.year,
            time_now=current_time.strftime("%H-%M-%S"),
            unique_id=self.episode_id
        )

        self.output_directory = os.path.join(bag_name, unique_bag_name)

        # Rosbag Writer
        self.writer = rosbag2_py.SequentialWriter()
        storage_options = rosbag2_py.StorageOptions(uri=self.output_directory, storage_id='mcap')
        converter_options = rosbag2_py.ConverterOptions('', '')
        self.writer.open(storage_options, converter_options)

        # Topic 1 - Camera A4ech (CameraData)
        topic_info1 = rosbag2_py.TopicMetadata(
            id=0,
            name='/camera/a4ech/camera_data',
            type='robot_interfaces/msg/CameraData',
            serialization_format='cdr')
        self.writer.create_topic(topic_info1)

        # Topic 2 - Webcam (CameraData)
        topic_info2 = rosbag2_py.TopicMetadata(
            id=1,
            name='/camera/webcam/camera_data',
            type='robot_interfaces/msg/CameraData',
            serialization_format='cdr')
        self.writer.create_topic(topic_info2)

        # Topic 3 - Language Instruction
        topic_info3 = rosbag2_py.TopicMetadata(
            id=2,
            name='/language_instruction',
            type='robot_interfaces/msg/LanguageInstruction',
            serialization_format='cdr')
        self.writer.create_topic(topic_info3)

        # Topic 4 - Joint States
        topic_info4 = rosbag2_py.TopicMetadata(
            id=3,
            name='/joint_states',
            type='sensor_msgs/msg/JointState',
            serialization_format='cdr')
        self.writer.create_topic(topic_info4)

        # Subscribers
        self.sub1 = self.create_subscription(
            CameraData, '/camera/a4ech/camera_data', self.callback_a4ech, 10)
        self.sub2 = self.create_subscription(
            CameraData, '/camera/webcam/camera_data', self.callback_webcam, 10)
        self.sub3 = self.create_subscription(
            LanguageInstruction, '/language_instruction', self.callback_language, 10)
        self.sub4 = self.create_subscription(
            JointState, '/joint_states', self.callback_joint_states, 10)

        # Save metadata
        self.save_metadata(current_time, unique_bag_name)

        self.get_logger().info('\033[92mNew Bag Recorder Started — Recording cameras + joint states + language!\033[0m')

    def save_metadata(self, current_time, bag_name):
        metadata = {
            "episode_id": self.episode_id,
            "experiment_id": str(uuid.uuid4()),
            "agent_id": "unknown",
            "robot_type": "unknown",
            "task_name": "webcam_recording",
            "environment_config": {
                "cameras": ["a4ech", "webcam"],
                "fps": 20
            },
            "timestamp": current_time.isoformat(),
            "bag_name": bag_name,
            "invalid": False,
            "reward": 0.0,
            "discount": 0.99
        }
        metadata_path = os.path.join(self.output_directory, 'episode_metadata.json')
        os.makedirs(self.output_directory, exist_ok=True)
        with open(metadata_path, 'w') as f:
            json.dump(metadata, f, indent=2)
        self.get_logger().info(f'\033[92mMetadata saved to {metadata_path}\033[0m')

    def callback_a4ech(self, msg):
        self.writer.write(
            '/camera/a4ech/camera_data',
            serialize_message(msg),
            self.get_clock().now().nanoseconds)

    def callback_webcam(self, msg):
        self.writer.write(
            '/camera/webcam/camera_data',
            serialize_message(msg),
            self.get_clock().now().nanoseconds)

    def callback_language(self, msg):
        self.writer.write(
            '/language_instruction',
            serialize_message(msg),
            self.get_clock().now().nanoseconds)

    def callback_joint_states(self, msg):
        self.writer.write(
            '/joint_states',
            serialize_message(msg),
            self.get_clock().now().nanoseconds)

def main(args=None):
    rclpy.init(args=args)
    node = NewBagRecorderNode()
    rclpy.spin(node)
    rclpy.shutdown()

if __name__ == '__main__':
    main()
