#!/usr/bin/env python3
import rclpy
from rclpy.node import Node
from rclpy.serialization import serialize_message
from kenneth_interfaces.msg import CameraData
from kenneth_interfaces.msg import LanguageInstruction
from kenneth_interfaces.msg import JointData
from pickplace_interfaces.msg import Robot
import rosbag2_py
import os
import uuid
import json
import ast
from datetime import datetime

class NewBagRecorderNode(Node):
    def __init__(self):
        super().__init__('new_bag_recorder_node')
        bag_name = 'webcam_bags'
        os.makedirs(bag_name, exist_ok=True)
        current_time = datetime.now()
        self.episode_id = str(uuid.uuid1())
        unique_bag_name = "{month}-{day}-{year}-{time_now}-{unique_id}".format(
            month=current_time.month, day=current_time.day, year=current_time.year,
            time_now=current_time.strftime("%H-%M-%S"), unique_id=self.episode_id)
        self.output_directory = os.path.join(bag_name, unique_bag_name)
        self.writer = rosbag2_py.SequentialWriter()
        storage_options = rosbag2_py.StorageOptions(uri=self.output_directory, storage_id='mcap')
        converter_options = rosbag2_py.ConverterOptions('', '')
        self.writer.open(storage_options, converter_options)
        for i, (name, typ) in enumerate([
            ('/camera/od/camera_data', 'kenneth_interfaces/msg/CameraData'),
            ('/camera/ocr/camera_data', 'kenneth_interfaces/msg/CameraData'),
            ('/language_instruction', 'kenneth_interfaces/msg/LanguageInstruction'),
            ('/xarm/joint_data', 'kenneth_interfaces/msg/JointData'),
        ]):
            self.writer.create_topic(rosbag2_py.TopicMetadata(id=i, name=name, type=typ, serialization_format='cdr'))
        self.sub1 = self.create_subscription(CameraData, '/camera/od/camera_data', self.callback_od, 10)
        self.sub2 = self.create_subscription(CameraData, '/camera/ocr/camera_data', self.callback_ocr, 10)
        self.sub3 = self.create_subscription(LanguageInstruction, '/language_instruction', self.callback_language, 10)
        self.sub4 = self.create_subscription(Robot, '/arm_settings', self.callback_arm_settings, 10)
        self.save_metadata(current_time, unique_bag_name)
        self.get_logger().info('\033[92mNew Bag Recorder Started!\033[0m')

    def save_metadata(self, current_time, bag_name):
        metadata = {"episode_id": self.episode_id, "experiment_id": str(uuid.uuid4()),
            "agent_id": "unknown", "robot_type": "unknown", "task_name": "webcam_recording",
            "environment_config": {"cameras": ["od", "ocr"], "fps": 20},
            "timestamp": current_time.isoformat(), "bag_name": bag_name,
            "invalid": False, "reward": 0.0, "discount": 0.99}
        metadata_path = os.path.join(self.output_directory, 'episode_metadata.json')
        os.makedirs(self.output_directory, exist_ok=True)
        with open(metadata_path, 'w') as f:
            json.dump(metadata, f, indent=2)

    def callback_od(self, msg):
        self.writer.write('/camera/od/camera_data', serialize_message(msg), self.get_clock().now().nanoseconds)

    def callback_ocr(self, msg):
        self.writer.write('/camera/ocr/camera_data', serialize_message(msg), self.get_clock().now().nanoseconds)

    def callback_language(self, msg):
        self.writer.write('/language_instruction', serialize_message(msg), self.get_clock().now().nanoseconds)

    def callback_arm_settings(self, msg):
        try:
            parsed = ast.literal_eval(msg.arm_servo_angle_radian)
            angles = parsed[1][:6]
            joint_data = JointData()
            joint_data.positions = [float(a) for a in angles]
            joint_data.velocities = [0.0] * 6
            joint_data.efforts = [0.0] * 6
            joint_data.joint_names = ['joint1','joint2','joint3','joint4','joint5','joint6']
            self.writer.write('/xarm/joint_data', serialize_message(joint_data), self.get_clock().now().nanoseconds)
        except Exception as e:
            self.get_logger().warn(f'Failed to parse arm_settings: {e}')

def main(args=None):
    rclpy.init(args=args)
    node = NewBagRecorderNode()
    rclpy.spin(node)
    rclpy.shutdown()

if __name__ == '__main__':
    main()
