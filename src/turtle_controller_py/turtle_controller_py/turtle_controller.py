#! /usr/bin/env python3
import rclpy
from rclpy.node import Node
from turtlesim.msg import Pose
from geometry_msgs.msg import Twist

class TurtleControllerNode(Node):
    def __init__(self):
        super().__init__("turtle_controller")
        self.pose_sub_ = self.create_subscription(
            Pose,
            "/turtle1/pose",
            self.pose_callback,
            10
        )
        self.cmd_vel_pub_ = self.create_publisher(
            Twist,
            "/turtle1/cmd_vel",
            10
        )
        self.get_logger().info("Turtle Controller has been started.")

    def pose_callback(self, pose: Pose):
        screen_middle = 5.5
        cmd = Twist()
        if pose.x < screen_middle:
            cmd.linear.x = 1.0
            cmd.angular.z = 1.0
        else:
            cmd.linear.x = 2.0
            cmd.angular.z = 2.0
        self.cmd_vel_pub_.publish(cmd)

def main(args=None):
    rclpy.init(args=args)
    node = TurtleControllerNode()
    rclpy.spin(node)
    rclpy.shutdown()

if __name__ == "__main__":
    main()