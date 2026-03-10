import os

from ament_index_python.packages import get_package_share_directory
from launch import LaunchDescription
from launch.actions import TimerAction
from launch_ros.actions import Node


def generate_launch_description():
    # 1) Resolve package share paths (portable; no hardcoded absolute paths).
    desc_pkg = get_package_share_directory('so_arm100_description')
    control_pkg = get_package_share_directory('so_arm_control')
    urdf_path = os.path.join(desc_pkg, 'urdf', 'so101_new_calib_control.urdf')
    controllers_path = os.path.join(control_pkg, 'config', 'controllers.yaml')

    # 2) Load URDF content into the `robot_description` parameter.
    with open(urdf_path, 'r') as infp:
        robot_description = infp.read()

    # 3) Publish TF from the robot model and joint states.
    robot_state_publisher_node = Node(
        package='robot_state_publisher',
        executable='robot_state_publisher',
        output='screen',
        parameters=[{'robot_description': robot_description}],
    )

    # 4) Start controller manager and load controller settings from YAML.
    ros2_control_node = Node(
        package='controller_manager',
        executable='ros2_control_node',
        output='screen',
        parameters=[controllers_path],
        # Read robot_description from the global topic/parameter namespace.
        remappings=[('~/robot_description', '/robot_description')],
    )

    # 5) Spawn joint_state_broadcaster after a short startup delay.
    joint_state_broadcaster_spawner = TimerAction(
        period=3.0,
        actions=[
            Node(
                package='controller_manager',
                executable='spawner',
                arguments=['joint_state_broadcaster'],
                output='screen',
            ),
        ],
    )

    # 6) Spawn arm_controller after the broadcaster is up.
    arm_controller_spawner = TimerAction(
        period=6.0,
        actions=[
            Node(
                package='controller_manager',
                executable='spawner',
                arguments=['arm_controller'],
                output='screen',
            ),
        ],
    )

    # 7) Launch in dependency order: model -> controller manager -> controllers.
    arm_trajectory_publisher_node = TimerAction(
        period=8.0,
        actions=[
            Node(
                package='so_arm_control',
                executable='arm_trajectory_publisher',
                output='screen',
            ),
        ],
    )

    # 8) Launch RViz for visualization.
    rviz_node = Node(
        package='rviz2',
        executable='rviz2',
        output='screen',
    )

    # 8) Launch in dependency order: model -> controller manager -> controllers -> trajectory publisher.
    return LaunchDescription([
        robot_state_publisher_node,
        ros2_control_node,
        joint_state_broadcaster_spawner,
        arm_controller_spawner,
        arm_trajectory_publisher_node,
        rviz_node,
    ])
