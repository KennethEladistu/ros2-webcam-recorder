#!/usr/bin/env python3

import rclpy
from rclpy.node import Node
from rclpy.serialization import serialize_message
from sensor_msgs.msg import Image
import rosbag2_py
import os
import uuid
import json
from datetime import datetime


class BagRecorderNode(Node):
    def __init__(self):
        super().__init__('bag_recorder_node')

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

        # Topic 1 - A4ech
        topic_info1 = rosbag2_py.TopicMetadata(
            id=0,
            name='/camera/a4ech/image_raw',
            type='sensor_msgs/msg/Image',
            serialization_format='cdr')
        self.writer.create_topic(topic_info1)

        # Topic 2 - Web Camera
        topic_info2 = rosbag2_py.TopicMetadata(
            id=1,
            name='/camera/webcam/image_raw',
            type='sensor_msgs/msg/Image',
            serialization_format='cdr')
        self.writer.create_topic(topic_info2)

        # Subscribers
        self.sub1 = self.create_subscription(
            Image, '/camera/a4ech/image_raw', self.callback1, 10)
        self.sub2 = self.create_subscription(
            Image, '/camera/webcam/image_raw', self.callback2, 10)

        # Save metadata.json
        self.save_metadata(current_time, unique_bag_name)

        self.get_logger().info('\033[92mBag Recorder Node Started — Recording 2 cameras!\033[0m')

    def save_metadata(self, current_time, bag_name):
        metadata = {
            "episode_id": self.episode_id,
            "experiment_id": str(uuid.uuid4()),
            "agent_id": "unknown",
            "robot_type": "unknown",
            "task_name": "webcam_recording",
            "init_scene_text": "",
            "skill": "",
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

    def callback1(self, msg):
        self.writer.write(
            '/camera/a4ech/image_raw',
            serialize_message(msg),
            self.get_clock().now().nanoseconds)

    def callback2(self, msg):
        self.writer.write(
            '/camera/webcam/image_raw',
            serialize_message(msg),
            self.get_clock().now().nanoseconds)


def main(args=None):
    rclpy.init(args=args)
    node = BagRecorderNode()
    rclpy.spin(node)
    rclpy.shutdown()

if __name__ == '__main__':
    main()
