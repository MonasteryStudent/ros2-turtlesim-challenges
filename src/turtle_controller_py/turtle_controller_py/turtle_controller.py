#!/usr/bin/env python3

import rclpy
from rclpy.node import Node
from rclpy.parameter import Parameter

from rcl_interfaces.msg import SetParametersResult
from geometry_msgs.msg import Twist
from turtlesim.msg import Pose
from turtlesim.srv import SetPen

from turtle_controller_interfaces.srv import SwitchActivation


class TurtleControllerNode(Node):
    def __init__(self):
        super().__init__("turtle_controller")

        self.is_active = True

        self.declare_parameter("color_left", "green")
        self.declare_parameter("color_right", "red")
        self.declare_parameter("turtle_velocity", 1.0)

        self.color_left = self.get_parameter("color_left").value
        self.color_right = self.get_parameter("color_right").value
        self.turtle_velocity = self.get_parameter("turtle_velocity").value

        self.init_pen_color_settings()

        self.validate_params()

        self.pen_cur_color = self.color_left
        self.pen_request_pending = False
        self.pending_pen_color = None

        self.pose_sub = self.create_subscription(
            Pose, "/turtle1/pose", self.pose_callback, 10)
        self.cmd_vel_pub = self.create_publisher(
            Twist, "/turtle1/cmd_vel", 10)
        self.set_pen_client = self.create_client(
            SetPen, "/turtle1/set_pen")
        self.switch_activation_service = self.create_service(
            SwitchActivation, "switch_activation", self.switch_activation_service_callback)
        self.add_on_set_parameters_callback(self.parameters_callback)

        self.get_logger().info("Turtle Controller has been started.")

    def validate_velocity_param(self, velocity, errors) -> None:
        min_velocity = 0.0
        max_velocity = 3.0
        if not min_velocity < velocity <= max_velocity:
            errors.append(
                f"Invalid value for 'turtle_velocity': '{velocity}'.\n"
                f"Valid range is (0.0, 3.0]."
            )

    def validate_color_param(self, color, side, errors) -> None:
        if color not in self.pen_colors:
            errors.append(
                f"Invalid value for '{side}': '{color}'."
            )
 
    def validate_params(self) -> None:
        """Validate all configurable node parameters."""
        color_errors = []
        velocity_errors = []

        self.validate_color_param(self.color_left, "color_left", color_errors)
        self.validate_color_param(self.color_right, "color_right", color_errors)
        self.validate_velocity_param(self.turtle_velocity, velocity_errors)

        if color_errors:
            valid_colors = ", ".join(self.pen_colors.keys())
            color_errors.append(f"Valid colors are: {valid_colors}.")

        errors = color_errors + velocity_errors

        if errors:
            raise ValueError("\n".join(errors))

    def init_pen_color_settings(self) -> None:
        self.pen_colors = {
            "green" : (0, 255, 0),
            "red"   : (255, 0, 0),
            "yellow": (255, 255, 0),
            "purple": (128, 0, 128),
            "orange": (255, 165, 0),
            "cyan"  : (0, 255, 255)
        }

    def call_set_pen(self, color_name) -> None:
        """Send a request to change the turtle's pen color."""
        if self.pen_request_pending:
            # Keep only the most recently requested color while a SetPen
            # request is still in progress.
            self.pending_pen_color = color_name
            return
        
        while not self.set_pen_client.wait_for_service(timeout_sec=1.0):
            self.get_logger().warning("Waiting for service...")

        r, g, b = self.pen_colors[color_name]
        request = SetPen.Request()
        request.r = r
        request.g = g
        request.b = b
        self.pen_request_pending = True

        future = self.set_pen_client.call_async(request)
        future.add_done_callback(
            lambda future: self.set_pen_callback(future, color_name))

    def pose_callback(self, pose: Pose) -> None:
        if not self.is_active:
            return

        screen_middle = 5.5
        cmd = Twist()

        if pose.x < screen_middle:
            cmd.linear.x = self.turtle_velocity
            cmd.angular.z = self.turtle_velocity
            if self.pen_cur_color == self.color_right:
                self.call_set_pen(self.color_left)
        else:
            cmd.linear.x = self.turtle_velocity * 2.0
            cmd.angular.z = self.turtle_velocity * 2.0
            if self.pen_cur_color == self.color_left:
                self.call_set_pen(self.color_right)

        self.cmd_vel_pub.publish(cmd)

    def set_pen_callback(self, future, color_name) -> None:
        future.result()

        self.pen_cur_color = color_name
        self.pen_request_pending = False

        self.get_logger().info(f"Pen color changed to {color_name}.")

        # Apply a color change that was requested while the previous
        # SetPen request was still pending.
        if self.pending_pen_color is not None:
            next_color = self.pending_pen_color
            self.pending_pen_color = None

            if next_color != self.pen_cur_color:
                self.call_set_pen(next_color) 

    def switch_activation_service_callback(self, request, response):
        if request.activate == self.is_active:
            response.success = False
            response.message = (
                "Turtle already activated."
                if self.is_active
                else "Turtle already deactivated."
            )
            return response

        self.is_active = request.activate
        response.success = True
        response.message = (
            "Turtle activated."
            if self.is_active
            else "Turtle deactivated."
        )

        return response

    def parameters_callback(
            self, 
            params: list[Parameter]
    ) -> SetParametersResult:
        """Validate and apply parameter changes at runtime."""
        color_errors = []
        velocity_errors = []

        for param in params:
            if param.name in {"color_left", "color_right"}:
                self.validate_color_param(param.value, param.name, color_errors)
            elif param.name == "turtle_velocity":
                self.validate_velocity_param(param.value, velocity_errors)

        if color_errors:
            valid_colors = ", ".join(self.pen_colors.keys())
            color_errors.append(f"Valid colors are: {valid_colors}.")

        errors = color_errors + velocity_errors

        if errors:
            return SetParametersResult(
                successful=False,
                reason="\n".join(errors)
            )

        for param in params:
            if param.name == "color_left":
                if self.pen_cur_color == self.color_left:
                    self.call_set_pen(param.value)
                self.color_left = param.value
            elif param.name == "color_right":
                if self.pen_cur_color == self.color_right:
                    self.call_set_pen(param.value)
                self.color_right = param.value
            elif param.name == "turtle_velocity":
                self.turtle_velocity = param.value

        return SetParametersResult(successful=True)


def main(args=None):
    rclpy.init(args=args)
    node = TurtleControllerNode()
    rclpy.spin(node)
    rclpy.shutdown()


if __name__ == "__main__":
    main()