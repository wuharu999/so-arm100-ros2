#!/usr/bin/env python3

import rclpy
from builtin_interfaces.msg import Duration
from rclpy.node import Node
from trajectory_msgs.msg import JointTrajectory, JointTrajectoryPoint


class ArmTrajectoryPublisher(Node):
    def __init__(self):
        # Node name shown by `ros2 node list`.
        super().__init__('arm_trajectory_publisher')

        # Publisher to the JointTrajectoryController command topic.
        self.publisher = self.create_publisher(
            JointTrajectory,
            '/arm_controller/joint_trajectory',
            10,  # QoS queue depth
        )

        # Must match the joint order configured in controllers.yaml.
        self.joint_names = [
            'shoulder_pan',
            'shoulder_lift',
            'elbow_flex',
            'wrist_flex',
            'wrist_roll',
            'gripper',
        ]

        # Two example target poses (radians for revolute joints).
        self.targets = [
            [0.0, -0.5, 1.0, -0.5, 0.0, 0.2],
            [0.4, -0.3, 0.8, -0.2, 0.4, 0.0],
        ]
        self.target_index = 0

        # Publish one command every 4 seconds.
        self.timer = self.create_timer(4.0, self.publish_trajectory)

        self.get_logger().info('Publishing to /arm_controller/joint_trajectory every 4.0s')

    def publish_trajectory(self):
        # JointTrajectory can contain multiple future points.
        # Here we send a single point target each cycle.
        msg = JointTrajectory()
        msg.joint_names = self.joint_names

        point = JointTrajectoryPoint()
        point.positions = self.targets[self.target_index]
        # Zero velocity hints; controller mainly tracks positions here.
        point.velocities = [0.0] * len(self.joint_names)
        # Reach the target 2 seconds after receiving this command.
        point.time_from_start = Duration(sec=2, nanosec=0)

        msg.points = [point]
        self.publisher.publish(msg)

        # Alternate between target #1 and #2.
        self.get_logger().info(f'Sent target #{self.target_index + 1}: {point.positions}')
        self.target_index = (self.target_index + 1) % len(self.targets)


def main(args=None):
    # Standard ROS 2 Python node lifecycle.
    rclpy.init(args=args)
    node = ArmTrajectoryPublisher()
    rclpy.spin(node)
    node.destroy_node()
    rclpy.shutdown()


if __name__ == '__main__':
    main()
