import os
from ament_index_python.packages import get_package_share_directory

from launch import LaunchDescription
from launch_ros.actions import Node


def generate_launch_description():
    ld = LaunchDescription()

    param_config = os.path.join(
        get_package_share_directory("turtle_bringup"),
        "config", "turtle_params.yaml"
    )

    turtle_controller_01 = Node(
        package="turtle_controller_py",
        executable="turtle_controller",
        namespace="/t1",
        remappings=[
            ("/turtle1/pose", "/t1/turtle1/pose"),
            ("/turtle1/cmd_vel", "/t1/turtle1/cmd_vel"),
            ("/turtle1/set_pen", "/t1/turtle1/set_pen")
        ],
        parameters=[param_config]
    )
    turtle_controller_02 = Node(
        package="turtle_controller_py",
        executable="turtle_controller",
        namespace="/t2",
        remappings=[
            ("/turtle1/pose", "/t2/turtle1/pose"),
            ("/turtle1/cmd_vel", "/t2/turtle1/cmd_vel"),
            ("/turtle1/set_pen", "/t2/turtle1/set_pen")
        ],
        parameters=[param_config]
    )
    turtlesim_node_01 = Node(
        package="turtlesim",
        executable="turtlesim_node",
        namespace="/t1",
        parameters=[param_config]
    )
    turtlesim_node_02 = Node(
        package="turtlesim",
        executable="turtlesim_node",
        namespace="/t2",
        parameters=[param_config]
    )

    ld.add_action(turtle_controller_01)
    ld.add_action(turtle_controller_02)
    ld.add_action(turtlesim_node_01)
    ld.add_action(turtlesim_node_02)

    return ld