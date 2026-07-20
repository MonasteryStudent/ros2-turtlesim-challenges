#!/usr/bin/env python3

import rclpy
from rclpy.node import Node
from turtle_controller_interfaces.srv import SwitchActivation
from geometry_msgs.msg import Twist
from turtlesim.msg import Pose
from turtlesim.srv import SetPen


class TurtleControllerNode(Node):
    def __init__(self):
        super().__init__("turtle_controller")
        self.is_active = True
        self.init_pen_color_settings()
        self.pose_sub = self.create_subscription(
            Pose, "/turtle1/pose", self.pose_callback, 10)
        self.cmd_vel_pub = self.create_publisher(
            Twist, "/turtle1/cmd_vel", 10)
        self.set_pen_client = self.create_client(
            SetPen, "/turtle1/set_pen")
        self.switch_activation_service = self.create_service(
            SwitchActivation, "switch_activation", self.switch_activation_service_callback)
        self.get_logger().info("Turtle Controller has been started.")

    def init_pen_color_settings(self):
        self.pen_cur_color = "green"
        self.pen_colors = {
            "green": {"r": 0, "g": 255, "b": 0},
            "red": {"r" : 255, "g": 0, "b": 0}
        }
        self.pen_request_pending = False

    def call_set_pen(self, color_name):
        if self.pen_request_pending:
            return
        
        while not self.set_pen_client.wait_for_service(1.0):
            self.get_logger().warn("Waiting for service...")

        color = self.pen_colors[color_name]
        request = SetPen.Request()
        request.r = color["r"]
        request.g = color["g"]
        request.b = color["b"]
        self.pen_request_pending = True

        future = self.set_pen_client.call_async(request)
        future.add_done_callback(
            lambda future: self.set_pen_callback(future, color_name))

    def pose_callback(self, pose: Pose):
        if not self.is_active:
            return

        screen_middle = 5.5
        cmd = Twist()

        if pose.x < screen_middle:
            cmd.linear.x = 1.0
            cmd.angular.z = 1.0
            if self.pen_cur_color == "red":
                self.call_set_pen("green")
        else:
            cmd.linear.x = 2.0
            cmd.angular.z = 2.0
            if self.pen_cur_color == "green":
                self.call_set_pen("red")

        self.cmd_vel_pub.publish(cmd)

    def set_pen_callback(self, future, color_name):
        self.pen_cur_color = color_name
        self.pen_request_pending = False
        self.get_logger().info(f"Pen color changed to {color_name}.")

    def switch_activation_service_callback(self, request, response):
        if request.activate and not self.is_active:
            self.is_active = request.activate
            response.message = "Turtle activated."
            response.success = True
        elif not request.activate and self.is_active:
            self.is_active = request.activate
            response.message = "Turtle deactivated."
            response.success = True
        elif request.activate:
            response.message = "Turtle already activated."
            response.success = False
        else:
            response.message = "Turtle already deactivated."
            response.success = False
        return response
            

def main(args=None):
    rclpy.init(args=args)
    node = TurtleControllerNode()
    rclpy.spin(node)
    rclpy.shutdown()


if __name__ == "__main__":
    main()